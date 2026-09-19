"""Belief model, state-aware costs, and finite-horizon acquisition policy."""
from dataclasses import dataclass
from collections import defaultdict
from typing import Dict, Iterable, Tuple, Optional, Sequence
import math
import random

STATES = ("STABLE", "DEGRADED", "TRANSIENT", "DISTRIBUTION_SHIFT")
ACTIONS = ("ACCEPT", "INVESTIGATE", "REJECT")
OBSERVABLE_KEYS = ("quality_low", "semantic_drift", "format_failure", "safety_shift", "latency_high", "error_high")
PROBES = ("semantic_drift", "format_failure", "safety_shift", "latency_high", "error_high", "capability_issue")

# These are only the probe-generation hypotheses. The six-channel initial evidence model
# is fitted empirically from held-out synthetic training cases and therefore captures
# dependencies among those six channels instead of multiplying marginal likelihoods.
CAPABILITY_PROBE_PRIOR = {"STABLE": 0.01, "DEGRADED": 0.95, "TRANSIENT": 0.10, "DISTRIBUTION_SHIFT": 0.20}

@dataclass(frozen=True)
class Costs:
    false_accept: float = 10.0
    false_reject: float = 3.0
    investigate: float = 0.4
    transient_accept: float = 4.0
    shift_accept: float = 6.0
    transient_reject: float = 1.0
    shift_reject: float = 2.0

    def state_action_cost(self, action: str, state: str) -> float:
        if action == "ACCEPT":
            return {"STABLE":0.0,"DEGRADED":self.false_accept,"TRANSIENT":self.transient_accept,"DISTRIBUTION_SHIFT":self.shift_accept}[state]
        if action == "REJECT":
            return {"STABLE":self.false_reject,"DEGRADED":0.0,"TRANSIENT":self.transient_reject,"DISTRIBUTION_SHIFT":self.shift_reject}[state]
        raise ValueError(action)

class NaiveEvidenceModel:
    """Legacy marginal-likelihood model used only as an ablation."""
    LIKELIHOODS = {
        "quality_low":       {"STABLE": 0.08, "DEGRADED": 0.78, "TRANSIENT": 0.60, "DISTRIBUTION_SHIFT": 0.35},
        "semantic_drift":    {"STABLE": 0.10, "DEGRADED": 0.72, "TRANSIENT": 0.58, "DISTRIBUTION_SHIFT": 0.70},
        "format_failure":    {"STABLE": 0.04, "DEGRADED": 0.55, "TRANSIENT": 0.35, "DISTRIBUTION_SHIFT": 0.22},
        "safety_shift":      {"STABLE": 0.03, "DEGRADED": 0.38, "TRANSIENT": 0.18, "DISTRIBUTION_SHIFT": 0.30},
        "latency_high":      {"STABLE": 0.10, "DEGRADED": 0.33, "TRANSIENT": 0.72, "DISTRIBUTION_SHIFT": 0.15},
        "error_high":        {"STABLE": 0.04, "DEGRADED": 0.45, "TRANSIENT": 0.55, "DISTRIBUTION_SHIFT": 0.12},
    }
    def signature_likelihood(self, state: str, signature: tuple[int, ...]) -> float:
        value=1.0
        for key, present in zip(OBSERVABLE_KEYS, signature):
            p=self.LIKELIHOODS[key][state]
            value *= p if present else (1-p)
        return value
    def probe_probability(self, state: str, probe: str) -> float:
        if probe == "capability_issue": return CAPABILITY_PROBE_PRIOR[state]
        return self.LIKELIHOODS[probe][state]
    def information_gain(self, belief: "BeliefState", probe: str) -> float:
        h0=belief.entropy(); py=sum(belief.probs[s]*self.probe_probability(s,probe) for s in STATES)
        if py<=1e-12 or py>=1-1e-12: return 0.0
        by=belief.after_probe(probe,True); bn=belief.after_probe(probe,False)
        return h0-py*by.entropy()-(1-py)*bn.entropy()

class EvidenceModel:
    def __init__(self, joint=None, probe_probs=None):
        self.joint = joint or {}
        self.probe_probs = probe_probs or CAPABILITY_PROBE_PRIOR.copy()

    @classmethod
    def fit(cls, cases: Sequence, alpha: float = 1.0):
        counts = {s: defaultdict(float) for s in STATES}
        totals = {s: 0.0 for s in STATES}
        probe_counts = {s: {p: 0.0 for p in PROBES} for s in STATES}
        probe_totals = {s: 0.0 for s in STATES}
        for case in cases:
            sig = case.observation.binary_signature()
            counts[case.state][sig] += 1.0
            totals[case.state] += 1.0
            probe_counts[case.state]["capability_issue"] += float(case.state == "DEGRADED" and 16 <= ((case.time_step-1)%50)+1 <= 20)
            probe_totals[case.state] += 1.0
            for p in ("semantic_drift","format_failure","safety_shift","latency_high","error_high"):
                positives = set(case.observation.evidence())
                probe_counts[case.state][p] += float(p in positives)
        all_sigs = [tuple((mask >> i) & 1 for i in range(len(OBSERVABLE_KEYS))) for mask in range(1 << len(OBSERVABLE_KEYS))]
        joint = {}
        for state in STATES:
            denom = totals[state] + alpha * len(all_sigs)
            joint[state] = {sig:(counts[state][sig] + alpha) / denom for sig in all_sigs}
        probes = {state:{} for state in STATES}
        for state in STATES:
            denom = probe_totals[state] + 2*alpha
            for p in PROBES:
                if p == "capability_issue":
                    probes[state][p] = CAPABILITY_PROBE_PRIOR[state]
                else:
                    probes[state][p] = (probe_counts[state][p] + alpha) / denom
        return cls(joint, probes)

    def signature_likelihood(self, state: str, signature: tuple[int, ...]) -> float:
        return self.joint[state][signature]

    def probe_probability(self, state: str, probe: str) -> float:
        return self.probe_probs[state][probe]

    def information_gain(self, belief: "BeliefState", probe: str) -> float:
        h0 = belief.entropy()
        py = sum(belief.probs[s] * self.probe_probability(s, probe) for s in STATES)
        if py <= 1e-12 or py >= 1-1e-12:
            return 0.0
        by = belief.after_probe(probe, True)
        bn = belief.after_probe(probe, False)
        return h0 - py*by.entropy() - (1-py)*bn.entropy()

@dataclass
class BeliefState:
    probs: Dict[str,float]
    model: Optional[EvidenceModel] = None

    def normalize(self):
        s = sum(self.probs.values())
        if s <= 0:
            raise ValueError("Belief mass must be positive")
        self.probs = {k:v/s for k,v in self.probs.items()}
        return self

    def update_full_observation(self, observation) -> "BeliefState":
        if self.model is None:
            raise ValueError("EvidenceModel is required for full observation updates")
        signature = observation.binary_signature()
        self.probs = {s:self.probs[s] * self.model.signature_likelihood(s, signature) for s in STATES}
        return self.normalize()

    def after_probe(self, probe: str, present: bool) -> "BeliefState":
        if self.model is None:
            raise ValueError("EvidenceModel is required for probe updates")
        updated = {s:self.probs[s] * (self.model.probe_probability(s, probe) if present else (1-self.model.probe_probability(s, probe))) for s in STATES}
        return BeliefState(updated, self.model).normalize()

    def entropy(self) -> float:
        return -sum(p*math.log(p, 2) for p in self.probs.values() if p > 0)

    @property
    def degraded_probability(self):
        return self.probs["DEGRADED"]

@dataclass
class Decision:
    action: str
    expected_cost: float
    reason: str
    belief: Dict[str,float]
    probe: str = ""
    remaining_budget: int = 0

class MonitorPolicy:
    def __init__(self, costs: Costs = None, evidence_model: EvidenceModel = None, max_probe_rounds: int = 2):
        self.costs = costs or Costs()
        self.evidence_model = evidence_model
        self.max_probe_rounds = max_probe_rounds

    @property
    def reject_posterior_threshold(self):
        return self.costs.false_reject / (self.costs.false_accept + self.costs.false_reject)

    def direct_costs(self, belief: BeliefState) -> Dict[str,float]:
        return {
            action: sum(belief.probs[s] * self.costs.state_action_cost(action, s) for s in STATES)
            for action in ("ACCEPT","REJECT")
        }

    def immediate_risk_costs(self, belief: BeliefState) -> Tuple[float,float]:
        c = self.direct_costs(belief)
        return c["ACCEPT"], c["REJECT"]

    def decide_binary(self, belief: BeliefState) -> Decision:
        fa = belief.degraded_probability * self.costs.false_accept
        fr = (1-belief.degraded_probability) * self.costs.false_reject
        if fa <= fr:
            return Decision("ACCEPT",fa,"binary DEGRADED-only comparator",dict(belief.probs))
        return Decision("REJECT",fr,"binary DEGRADED-only comparator",dict(belief.probs))

    def decide_state_aware(self, belief: BeliefState) -> Decision:
        costs = self.direct_costs(belief)
        action = min(costs, key=costs.get)
        return Decision(action,costs[action],"four-state expected-cost rule",dict(belief.probs))

    def _probe_expected_value(self, belief: BeliefState, probe: str, remaining: int) -> float:
        py = sum(belief.probs[s] * self.evidence_model.probe_probability(s, probe) for s in STATES)
        if py <= 1e-12 or py >= 1-1e-12:
            return float("inf")
        by = belief.after_probe(probe, True)
        bn = belief.after_probe(probe, False)
        if remaining <= 1:
            downstream = py * self.decide_state_aware(by).expected_cost + (1-py) * self.decide_state_aware(bn).expected_cost
        else:
            downstream = py * self._optimal_value(by, remaining-1, banned={probe}) + (1-py) * self._optimal_value(bn, remaining-1, banned={probe})
        return self.costs.investigate + downstream

    def _optimal_value(self, belief: BeliefState, remaining: int, banned=None) -> float:
        banned = banned or set()
        direct = self.decide_state_aware(belief).expected_cost
        if remaining <= 0:
            return direct
        best_probe = direct
        for probe in PROBES:
            if probe in banned:
                continue
            best_probe = min(best_probe, self._probe_expected_value(belief, probe, remaining))
        return best_probe

    def choose_probe(self, belief: BeliefState, remaining: int = 1, banned=None) -> Tuple[str,float,float]:
        banned = set(banned or set())
        direct = self.decide_state_aware(belief).expected_cost
        candidates=[]
        for probe in PROBES:
            if probe in banned:
                continue
            value=self._probe_expected_value(belief, probe, remaining)
            candidates.append((probe,value))
        if not candidates:
            return "", 0.0, direct
        probe, value = min(candidates, key=lambda x:x[1])
        gross = direct - (value - self.costs.investigate)
        return probe, gross, value

    def decide_active(self, belief: BeliefState, probe_rounds: int = 0, used_probes=None) -> Decision:
        used_probes = set(used_probes or set())
        direct = self.decide_state_aware(belief)
        remaining = self.max_probe_rounds - probe_rounds
        if remaining <= 0:
            return direct
        candidates=[]
        for probe in PROBES:
            if probe in used_probes:
                continue
            value=self._probe_expected_value(belief, probe, remaining)
            candidates.append((probe,value))
        if not candidates:
            return direct
        probe, best_value = min(candidates, key=lambda x:x[1])
        if best_value + 1e-12 < direct.expected_cost:
            gross = direct.expected_cost - (best_value - self.costs.investigate)
            return Decision("INVESTIGATE",best_value,f"decision-aware VOI: gross value={gross:.3f}; probe cost={self.costs.investigate:.3f}",dict(belief.probs),probe,remaining)
        return direct
