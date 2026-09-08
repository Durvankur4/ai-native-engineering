"""Synthetic testbed with controllable hidden states and observable evidence."""
from dataclasses import dataclass
import random, math
from typing import List
from .agent import Observation

CATEGORIES=["math","code","instruction","safety","knowledge"]

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

def make_observation(rng, state, category):
    base_quality={"STABLE":0.90,"DEGRADED":0.56,"TRANSIENT":0.62,"DISTRIBUTION_SHIFT":0.78}[state]
    category_penalty={"math":0.00,"code":0.03,"instruction":0.02,"safety":0.01,"knowledge":0.02}[category]
    q=_bounded(rng.gauss(base_quality-category_penalty,0.08))
    sem=_bounded(rng.gauss({"STABLE":0.08,"DEGRADED":0.48,"TRANSIENT":0.22,"DISTRIBUTION_SHIFT":0.38}[state],0.13))
    fmt=int(rng.random() < {"STABLE":0.04,"DEGRADED":0.34,"TRANSIENT":0.18,"DISTRIBUTION_SHIFT":0.12}[state])
    saf=int(category=="safety" and rng.random() < {"STABLE":0.03,"DEGRADED":0.22,"TRANSIENT":0.08,"DISTRIBUTION_SHIFT":0.15}[state])
    lat=max(150,rng.gauss({"STABLE":420,"DEGRADED":560,"TRANSIENT":1050,"DISTRIBUTION_SHIFT":480}[state],140))
    err=max(0.0,min(0.5,rng.gauss({"STABLE":0.02,"DEGRADED":0.14,"TRANSIENT":0.18,"DISTRIBUTION_SHIFT":0.05}[state],0.035)))
    return Observation(q,sem,fmt,saf,lat,err)


def generate_cases(n=50, seed=7):
    rng=random.Random(seed)
    states=[]
    # 50 cases: mostly stable, with localized degradations and transient events.
    for i in range(n):
        if 16 <= i <= 26: st="DEGRADED"
        elif 31 <= i <= 35 or i in (43,44): st="TRANSIENT"
        elif 37 <= i <= 41: st="DISTRIBUTION_SHIFT"
        else: st="STABLE"
        states.append(st)
    rng.shuffle(CATEGORIES)
    cases=[]
    for i,st in enumerate(states,1):
        cat=CATEGORIES[i % len(CATEGORIES)]
        obs=make_observation(rng,st,cat)
        blind_spot = (st == "DEGRADED" and 16 <= i <= 20)
        if blind_spot:
            # Hidden failure mode: average observable quality remains high while a narrow
            # high-cost capability has regressed. This tests the Week 1 warning against a
            # single aggregate score representing the full state.
            obs.quality = _bounded(rng.gauss(0.84,0.04))
            obs.semantic_drift = _bounded(rng.gauss(0.10,0.03))
            obs.format_failure = 0
            obs.safety_shift = 0
            obs.latency_ms = max(150,rng.gauss(430,80))
            obs.error_rate = max(0.0,min(0.05,rng.gauss(0.02,0.01)))
        elif i == 30 and st == "STABLE":
            # Evaluator-noise style false alarm: observable signals look degraded even
            # though the hidden state is stable. This tests over-rejection.
            obs.quality = _bounded(rng.gauss(0.62,0.03))
            obs.semantic_drift = _bounded(rng.gauss(0.50,0.05))
            obs.format_failure = 1
            obs.safety_shift = 0
            obs.latency_ms = max(150,rng.gauss(650,100))
            obs.error_rate = max(0.0,min(0.15,rng.gauss(0.10,0.02)))
        drift=st != "STABLE"
        note=("narrow high-cost capability regression / observational blind spot" if blind_spot else
              {"STABLE":"reference-like behavior","DEGRADED":"persistent quality regression","TRANSIENT":"temporary anomaly","DISTRIBUTION_SHIFT":"request distribution changed"}[st])
        cases.append(Case(f"case-{i:03d}",st,cat,i,obs,drift,note))
    return cases
