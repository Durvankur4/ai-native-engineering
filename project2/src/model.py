"""Belief model and decision policy for the Week 1 black-box LLM monitor."""
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Tuple
import math

STATES = ("STABLE", "DEGRADED", "TRANSIENT", "DISTRIBUTION_SHIFT")
ACTIONS = ("ACCEPT", "INVESTIGATE", "REJECT")

# Evidence likelihoods are deliberately explicit, inspectable hypotheses.
# They are calibrated by simulation, not presented as production ground truth.
LIKELIHOODS = {
    "quality_low":       {"STABLE": 0.08, "DEGRADED": 0.78, "TRANSIENT": 0.60, "DISTRIBUTION_SHIFT": 0.35},
    "quality_ok":        {"STABLE": 0.92, "DEGRADED": 0.22, "TRANSIENT": 0.40, "DISTRIBUTION_SHIFT": 0.65},
    "semantic_drift":    {"STABLE": 0.10, "DEGRADED": 0.72, "TRANSIENT": 0.58, "DISTRIBUTION_SHIFT": 0.70},
    "format_failure":    {"STABLE": 0.04, "DEGRADED": 0.55, "TRANSIENT": 0.35, "DISTRIBUTION_SHIFT": 0.22},
    "safety_shift":      {"STABLE": 0.03, "DEGRADED": 0.38, "TRANSIENT": 0.18, "DISTRIBUTION_SHIFT": 0.30},
    "latency_high":      {"STABLE": 0.10, "DEGRADED": 0.33, "TRANSIENT": 0.72, "DISTRIBUTION_SHIFT": 0.15},
    "error_high":        {"STABLE": 0.04, "DEGRADED": 0.45, "TRANSIENT": 0.55, "DISTRIBUTION_SHIFT": 0.12},
}

@dataclass(frozen=True)
class Costs:
    false_accept: float = 12.0
    false_reject: float = 5.0
    investigate: float = 0.8
    human_escalation: float = 2.0

@dataclass
class BeliefState:
    probs: Dict[str, float]

    def normalize(self) -> "BeliefState":
        s=sum(self.probs.values())
        if s <= 0: raise ValueError("Belief mass must be positive")
        self.probs={k:v/s for k,v in self.probs.items()}
        return self

    def update(self, evidence: Iterable[str], present: Iterable[str]=()) -> "BeliefState":
        present=set(present)
        evidence=list(evidence)
        out={}
        for state,p in self.probs.items():
            score=p
            for ev in evidence:
                score*=LIKELIHOODS[ev][state]
            for ev in present:
                score*=1-LIKELIHOODS[ev][state]
            out[state]=score
        self.probs=out
        return self.normalize()

    @property
    def unsafe_probability(self) -> float:
        return 1.0-(self.probs["STABLE"]+self.probs["DISTRIBUTION_SHIFT"])

    @property
    def degraded_probability(self) -> float:
        return self.probs["DEGRADED"]

    @property
    def transient_probability(self) -> float:
        return self.probs["TRANSIENT"]

@dataclass
class Decision:
    action: str
    expected_cost: float
    reason: str
    belief: Dict[str,float]

class MonitorPolicy:
    def __init__(self, costs: Costs=None, reject_threshold: float=0.55, accept_threshold: float=0.20, max_probe_rounds: int=2):
        self.costs=costs or Costs()
        self.reject_threshold=reject_threshold
        self.accept_threshold=accept_threshold
        self.max_probe_rounds=max_probe_rounds

    def immediate_risk_costs(self, belief: BeliefState) -> Tuple[float,float]:
        unsafe=belief.unsafe_probability
        # Distribution shift is not always unsafe, so it carries half of degraded cost.
        false_accept=belief.degraded_probability*self.costs.false_accept + belief.transient_probability*0.35*self.costs.false_accept
        false_reject=(belief.probs["STABLE"]+0.5*belief.probs["DISTRIBUTION_SHIFT"])*self.costs.false_reject
        return false_accept,false_reject

    def decide_binary(self, belief: BeliefState) -> Decision:
        fa,fr=self.immediate_risk_costs(belief)
        if fa <= fr:
            return Decision("ACCEPT",fa,"binary threshold: expected false-accept cost <= false-reject cost",dict(belief.probs))
        return Decision("REJECT",fr,"binary threshold: expected false-reject cost < false-accept cost",dict(belief.probs))

    def _posterior_after(self, belief: BeliefState, ev: str, present: bool) -> BeliefState:
        b=BeliefState(dict(belief.probs))
        return b.update([ev] if present else [], [] if present else [ev])

    def investigation_value(self, belief: BeliefState, probe_event: str) -> float:
        """Expected value of a binary probe under the current belief."""
        p_yes=sum(belief.probs[s]*LIKELIHOODS[probe_event][s] for s in STATES)
        p_no=1-p_yes
        if p_yes <= 1e-9 or p_no <= 1e-9:
            return 0.0
        by=self._posterior_after(belief,probe_event,True)
        bn=self._posterior_after(belief,probe_event,False)
        cy=self.decide_binary(by).expected_cost
        cn=self.decide_binary(bn).expected_cost
        current=min(self.immediate_risk_costs(belief))
        expected_after=p_yes*cy+p_no*cn+self.costs.investigate
        return current-expected_after

    def choose_probe(self, belief: BeliefState) -> Tuple[str,float]:
        candidates=["semantic_drift","format_failure","safety_shift","latency_high","error_high"]
        vals=[(ev,self.investigation_value(belief,ev)) for ev in candidates]
        return max(vals,key=lambda x:x[1])

    def decide_active(self, belief: BeliefState, probe_rounds: int=0) -> Decision:
        fa,fr=self.immediate_risk_costs(belief)
        direct=min(fa,fr)
        probe,voi=self.choose_probe(belief)
        if probe_rounds < self.max_probe_rounds and voi > 0:
            return Decision("INVESTIGATE",self.costs.investigate+max(0,-voi),f"probe={probe}; estimated value-of-information={voi:.3f}",dict(belief.probs))
        if fa <= fr:
            return Decision("ACCEPT",fa,"active policy: direct acceptance has lower expected cost",dict(belief.probs))
        return Decision("REJECT",fr,"active policy: direct rejection has lower expected cost",dict(belief.probs))
