"""Synthetic LLM monitoring testbed with correlated evidence and controllable states."""
from dataclasses import dataclass
import math
import random
from .agent import Observation

CATEGORIES=["math","code","instruction","safety","knowledge"]
CAPABILITY_PROBE_PROB={"STABLE":0.01,"DEGRADED":0.95,"TRANSIENT":0.10,"DISTRIBUTION_SHIFT":0.20}

@dataclass
class Case:
    case_id: str
    state: str
    category: str
    time_step: int
    observation: Observation
    drift_event: bool
    note: str

def _bounded(x): return max(0.0,min(1.0,x))

def _sigmoid(x): return 1/(1+math.exp(-x))

def make_observation(rng, state, category):
    means = {
        "STABLE": {"q":0.90,"sem":0.08,"lat":420,"err":0.02},
        "DEGRADED": {"q":0.56,"sem":0.48,"lat":560,"err":0.14},
        "TRANSIENT": {"q":0.62,"sem":0.22,"lat":1050,"err":0.18},
        "DISTRIBUTION_SHIFT": {"q":0.78,"sem":0.38,"lat":480,"err":0.05},
    }[state]
    category_penalty={"math":0.00,"code":0.03,"instruction":0.02,"safety":0.01,"knowledge":0.02}[category]
    # Shared latent pressure intentionally induces realistic co-movement among channels.
    pressure = rng.gauss(0,1) if state != "STABLE" else rng.gauss(0,0.65)
    q = _bounded(rng.gauss(means["q"]-category_penalty + 0.045*pressure,0.07))
    sem = _bounded(rng.gauss(means["sem"] + 0.065*pressure,0.10))
    fmt_p = {"STABLE":0.04,"DEGRADED":0.34,"TRANSIENT":0.18,"DISTRIBUTION_SHIFT":0.12}[state]
    fmt = int(rng.random() < _sigmoid(math.log(fmt_p/(1-fmt_p)) + 0.45*pressure))
    saf_p = {"STABLE":0.03,"DEGRADED":0.22,"TRANSIENT":0.08,"DISTRIBUTION_SHIFT":0.15}[state]
    saf = int(category=="safety" and rng.random() < _sigmoid(math.log(saf_p/(1-saf_p)) + 0.35*pressure))
    lat = max(150,rng.gauss(means["lat"] + 45*pressure,120))
    err = max(0.0,min(0.5,rng.gauss(means["err"] + 0.018*pressure,0.025)))
    return Observation(q,sem,fmt,saf,lat,err)

def make_investigation_probe(rng, case: Case, probe_name: str) -> Observation:
    if probe_name == "capability_issue":
        cycle_i=((case.time_step-1)%50)+1
        blind_spot = case.state=="DEGRADED" and 16<=cycle_i<=20
        capability_issue = int(blind_spot or rng.random()<CAPABILITY_PROBE_PROB[case.state])
        return Observation(0.90,0.05,0,0,420,0.01,capability_issue=capability_issue)
    probe=make_observation(rng,case.state,case.category)
    if case.state=="DISTRIBUTION_SHIFT":
        probe.semantic_drift=min(1.0,probe.semantic_drift+0.20)
        probe.error_rate=min(0.5,probe.error_rate+0.03)
    return probe

def generate_cases(n=120, seed=7):
    rng=random.Random(seed)
    base_states=[]
    for i in range(1,51):
        if 16<=i<=26: st="DEGRADED"
        elif 31<=i<=35 or i in (43,44): st="TRANSIENT"
        elif 37<=i<=41: st="DISTRIBUTION_SHIFT"
        else: st="STABLE"
        base_states.append(st)
    states=[base_states[(i-1)%len(base_states)] for i in range(1,n+1)]
    categories = CATEGORIES.copy()
    rng.shuffle(categories)
    cases=[]
    for i,st in enumerate(states,1):
        cat=categories[i%len(categories)]
        obs=make_observation(rng,st,cat)
        cycle_i=((i-1)%50)+1
        blind_spot=st=="DEGRADED" and 16<=cycle_i<=20
        if blind_spot:
            obs.quality=_bounded(rng.gauss(0.84,0.04)); obs.semantic_drift=_bounded(rng.gauss(0.10,0.03))
            obs.format_failure=0; obs.safety_shift=0; obs.latency_ms=max(150,rng.gauss(430,80)); obs.error_rate=max(0,min(0.05,rng.gauss(0.02,0.01)))
        elif cycle_i==30 and st=="STABLE":
            obs.quality=_bounded(rng.gauss(0.62,0.03)); obs.semantic_drift=_bounded(rng.gauss(0.50,0.05)); obs.format_failure=1
            obs.safety_shift=0; obs.latency_ms=max(150,rng.gauss(650,100)); obs.error_rate=max(0,min(0.15,rng.gauss(0.10,0.02)))
        drift=st!="STABLE"
        note=("narrow capability regression / correlated-evidence blind spot" if blind_spot else
              {"STABLE":"reference-like behavior","DEGRADED":"persistent quality regression","TRANSIENT":"temporary anomaly","DISTRIBUTION_SHIFT":"request distribution changed"}[st])
        cases.append(Case(f"case-{i:03d}",st,cat,i,obs,drift,note))
    return cases
