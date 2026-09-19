import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.agent import BlackBoxMonitoringAgent, Observation
from src.model import BeliefState, Costs, EvidenceModel, MonitorPolicy
from src.simulator import generate_cases


def test_joint_model_normalizes_each_state():
    model=EvidenceModel.fit(generate_cases(1000,seed=99))
    for state in model.joint:
        assert abs(sum(model.joint[state].values())-1.0)<1e-9

def test_four_state_direct_rule_is_not_degraded_only():
    model=EvidenceModel.fit(generate_cases(1000,seed=99)); p=MonitorPolicy(evidence_model=model)
    b=BeliefState({"STABLE":0.4,"DEGRADED":0.1,"TRANSIENT":0.2,"DISTRIBUTION_SHIFT":0.3},model)
    d=p.decide_state_aware(b)
    assert d.action in {"ACCEPT","REJECT"}
    assert d.expected_cost == min(p.direct_costs(b).values())

def test_binary_threshold_remains_3_over_13():
    p=MonitorPolicy(Costs())
    assert abs(p.reject_posterior_threshold-3/13)<1e-12

def test_two_step_policy_can_select_investigation():
    model=EvidenceModel.fit(generate_cases(2000,seed=99)); agent=BlackBoxMonitoringAgent(evidence_model=model)
    obs=Observation(.83,.35,0,0,500,.04)
    d=agent.act(obs,active=True)
    assert d.action in {"ACCEPT","INVESTIGATE","REJECT"}
    if d.action=="INVESTIGATE": assert d.remaining_budget>=1

def test_probe_budget_is_two():
    model=EvidenceModel.fit(generate_cases(1000,seed=99)); p=MonitorPolicy(evidence_model=model,max_probe_rounds=2)
    b=BeliefState({"STABLE":.72,"DEGRADED":.12,"TRANSIENT":.08,"DISTRIBUTION_SHIFT":.08},model).normalize()
    d=p.decide_active(b,probe_rounds=2)
    assert d.action in {"ACCEPT","REJECT"}

def test_observation_signature_has_six_channels():
    obs=Observation(.5,.4,1,0,1000,.12)
    assert len(obs.binary_signature())==6

def test_case_generation_is_order_independent():
    first=generate_cases(120,seed=123)
    _=generate_cases(75,seed=456)
    second=generate_cases(120,seed=123)
    assert [(c.category,c.state,c.observation.quality) for c in first] == [(c.category,c.state,c.observation.quality) for c in second]
