from dataclasses import dataclass, asdict
from typing import Dict, List
from .model import BeliefState, Costs, MonitorPolicy, Decision, EvidenceModel, OBSERVABLE_KEYS

@dataclass
class Observation:
    quality: float
    semantic_drift: float
    format_failure: int
    safety_shift: int
    latency_ms: float
    error_rate: float
    feedback_rate: float = 0.0
    capability_issue: int = 0

    def evidence(self) -> List[str]:
        ev = ["quality_low" if self.quality < 0.70 else "quality_ok"]
        ev.append("semantic_drift" if self.semantic_drift >= 0.30 else "semantic_ok")
        ev.append("format_failure" if self.format_failure else "format_ok")
        ev.append("safety_shift" if self.safety_shift else "safety_ok")
        ev.append("latency_high" if self.latency_ms >= 900 else "latency_ok")
        ev.append("error_high" if self.error_rate >= 0.08 else "error_ok")
        if self.capability_issue:
            ev.append("capability_issue")
        return ev

    def binary_signature(self) -> tuple[int, ...]:
        positives = set(self.evidence())
        names = OBSERVABLE_KEYS
        return tuple(int(name in positives) for name in names)

class BlackBoxMonitoringAgent:
    def __init__(self, prior=None, costs=None, evidence_model: EvidenceModel = None, max_probe_rounds=2):
        self.prior = prior or {"STABLE":0.72,"DEGRADED":0.12,"TRANSIENT":0.08,"DISTRIBUTION_SHIFT":0.08}
        self.costs = costs or Costs()
        self.evidence_model = evidence_model
        self.policy = MonitorPolicy(self.costs, evidence_model=evidence_model, max_probe_rounds=max_probe_rounds)
        self.memory = []

    def initial_belief(self):
        return BeliefState(dict(self.prior), self.evidence_model).normalize()

    def observe(self, observation: Observation):
        belief = self.initial_belief().update_full_observation(observation)
        self.memory.append({"observation":asdict(observation),"belief":dict(belief.probs)})
        return belief

    def act(self, observation: Observation, active=True, probe_rounds=0):
        belief = self.observe(observation)
        if not active:
            return self.policy.decide_binary(belief)
        return self.policy.decide_active(belief, probe_rounds=probe_rounds)
