import json, math, os
from pathlib import Path
import pandas as pd
from .agent import BlackBoxMonitoringAgent
from .simulator import generate_cases, make_observation

ACTIONS=["ACCEPT","INVESTIGATE","REJECT"]
COSTS={"FALSE_ACCEPT":12.0,"FALSE_REJECT":5.0,"INVESTIGATE":0.8}

def run_policy(policy, cases):
    rows=[]
    for c in cases:
        agent=BlackBoxMonitoringAgent()
        dec=agent.act(c.observation,active=policy!="baseline")
        investigation_cost = 0.0
        initial_action = dec.action
        if policy=="baseline":
            action="ACCEPT" if c.observation.quality>=0.70 else "REJECT"
            exp_cost=None
            reason="static quality threshold"
            belief={}
        elif policy=="binary":
            action=dec.action if dec.action in ("ACCEPT","REJECT") else "REJECT"
            exp_cost=dec.expected_cost
            reason=dec.reason
            belief=dec.belief
        else:
            if dec.action=="INVESTIGATE":
                investigation_cost=COSTS["INVESTIGATE"]
                probe=make_observation(__import__('random').Random(1000+c.time_step), c.state, c.category)
                if c.state == "DISTRIBUTION_SHIFT":
                    probe.semantic_drift = min(1.0, probe.semantic_drift + 0.25)
                    probe.error_rate = min(0.5, probe.error_rate + 0.04)
                post=__import__('src.model',fromlist=['BeliefState']).BeliefState(dict(dec.belief)).update(probe.evidence())
                final=agent.policy.decide_binary(post)
                action=final.action
                exp_cost=investigation_cost+final.expected_cost
                reason=f"investigated with independent probe; {final.reason}"
                belief=post.probs
            else:
                action=dec.action
                exp_cost=dec.expected_cost
                reason=dec.reason
                belief=dec.belief
        # Ground-truth harm model for evaluation only.
        if action=="ACCEPT":
            cost=investigation_cost + (COSTS["FALSE_ACCEPT"] if c.drift_event else 0.0)
        elif action=="REJECT":
            cost=investigation_cost + (COSTS["FALSE_REJECT"] if not c.drift_event else 0.0)
        else:
            cost=COSTS["INVESTIGATE"]
        rows.append({"case_id":c.case_id,"state":c.state,"category":c.category,"quality":c.observation.quality,
                     "latency_ms":c.observation.latency_ms,"drift_event":c.drift_event,"initial_action":initial_action,"action":action,"cost":cost,
                     "expected_cost":exp_cost,"reason":reason,"belief":json.dumps(belief)})
    return pd.DataFrame(rows)

def metrics(df):
    n=len(df)
    fa=((df.action=="ACCEPT") & df.drift_event).sum()
    fr=((df.action=="REJECT") & (~df.drift_event)).sum()
    inv=(df.initial_action=="INVESTIGATE").sum()
    detections=(((df.action.isin(["REJECT","INVESTIGATE"])) & df.drift_event)).sum()
    actual=int(df.drift_event.sum())
    precision=(detections/(detections+((df.action.isin(["REJECT","INVESTIGATE"])) & (~df.drift_event)).sum())) if detections else 0
    recall=detections/actual if actual else 0
    return {"n":n,"false_accept":int(fa),"false_reject":int(fr),"investigation_rate":inv/n,"decision_cost":float(df.cost.sum()),"degradation_recall":recall,"degradation_precision":precision}

def main(out_dir="results"):
    cases=generate_cases()
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    all_metrics={}
    for policy in ["baseline","binary","active"]:
        df=run_policy(policy,cases)
        df.to_csv(out/f"{policy}_decisions.csv",index=False)
        all_metrics[policy]=metrics(df)
    pd.DataFrame(all_metrics).T.to_csv(out/"policy_metrics.csv")
    # failure table from active policy: prioritize high-cost mistakes.
    adf=pd.read_csv(out/"active_decisions.csv")
    mistakes=adf[((adf.action=="ACCEPT") & adf.drift_event) | ((adf.action=="REJECT") & (~adf.drift_event))].copy()
    mistakes["failure_mode"]=mistakes.apply(lambda r: "missed_degradation" if r.action=="ACCEPT" else "over_rejection",axis=1)
    mistakes.sort_values("cost",ascending=False).head(5).to_csv(out/"five_failure_cases.csv",index=False)
    (out/"summary.json").write_text(json.dumps(all_metrics,indent=2))
    return all_metrics

if __name__=="__main__":
    print(json.dumps(main(),indent=2))
