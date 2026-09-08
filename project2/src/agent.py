from dataclasses import dataclass, asdict
from typing import Dict, List
from .model import BeliefState, Costs, MonitorPolicy, STATES, Decision

@dataclass
class Observation:
    quality: float
    semantic_drift: float
    format_failure: int
    safety_shift: int
    latency_ms: float
    error_rate: float
    feedback_rate: float = 0.0

    def evidence(self) -> List[str]:
        ev=[]
        ev.append("quality_low" if self.quality < 0.70 else "quality_ok")
        if self.semantic_drift >= 0.30: ev.append("semantic_drift")
        if self.format_failure: ev.append("format_failure")
        if self.safety_shift: ev.append("safety_shift")
        if self.latency_ms >= 900: ev.append("latency_high")
        if self.error_rate >= 0.08: ev.append("error_high")
        return ev

class BlackBoxMonitoringAgent:
    def __init__(self, prior=None, costs=None, reject_threshold=0.55, accept_threshold=0.20, max_probe_rounds=2):
        self.prior=prior or {"STABLE":0.72,"DEGRADED":0.12,"TRANSIENT":0.08,"DISTRIBUTION_SHIFT":0.08}
        self.costs=costs or Costs()
        self.policy=MonitorPolicy(self.costs,reject_threshold,accept_threshold,max_probe_rounds)
        self.memory=[]

    def initial_belief(self):
        return BeliefState(dict(self.prior)).normalize()

    def observe(self, observation: Observation):
        belief=self.initial_belief().update(observation.evidence())
        self.memory.append({"observation":asdict(observation),"belief":dict(belief.probs)})
        return belief

    def act(self, observation: Observation, active=True, probe_rounds=0):
        belief=self.observe(observation)
        decision=self.policy.decide_active(belief,probe_rounds) if active else self.policy.decide_binary(belief)
        return decision

    def investigate(self, belief: BeliefState, observation: Observation):
        # A practical probe: re-evaluate on an independent probe slice.
        updated=BeliefState(dict(belief.probs)).update(observation.evidence())
        return updated
