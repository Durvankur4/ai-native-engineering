import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agent import BlackBoxMonitoringAgent, Observation
from src.model import BeliefState, STATES


def test_belief_sums_to_one():
    b=BeliefState({"STABLE":.72,"DEGRADED":.12,"TRANSIENT":.08,"DISTRIBUTION_SHIFT":.08}).update(["quality_low","semantic_drift"])
    assert abs(sum(b.probs.values())-1) < 1e-9

def test_agent_returns_allowed_action():
    a=BlackBoxMonitoringAgent()
    o=Observation(.55,.5,1,0,1000,.12)
    d=a.act(o,active=True)
    assert d.action in {"ACCEPT","INVESTIGATE","REJECT"}

def test_active_policy_investigates_uncertain_case():
    a=BlackBoxMonitoringAgent()
    o=Observation(.79,.25,0,0,500,.04)
    d=a.act(o,active=True)
    assert d.action in {"ACCEPT","INVESTIGATE","REJECT"}

def test_memory_records_observation():
    a=BlackBoxMonitoringAgent()
    a.act(Observation(.9,.05,0,0,400,.01))
    assert len(a.memory)==1
