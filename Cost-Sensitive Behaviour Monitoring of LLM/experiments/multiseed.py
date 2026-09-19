import math
from pathlib import Path
import pandas as pd
from src.evaluate import fit_evidence_model, run_policy, metrics, summarize_runs
from src.simulator import generate_cases
from src.model import Costs

OUT=Path("results")
POLICIES=["baseline","binary_naive","binary","state_direct","random_acquire","always_acquire","eig_one_step","voi_one_step","active"]
DEV_SEEDS=list(range(100,105))
TEST_SEEDS=list(range(20))
CANDIDATE_COSTS=[0.4,0.6,0.8,1.0,1.2]

def mean_dev_cost(model,cost):
    vals=[]
    for seed in DEV_SEEDS:
        cases=generate_cases(n=120,seed=seed)
        m=metrics(run_policy("active",cases,model,Costs(investigate=cost),seed=seed))
        vals.append(m["decision_cost"])
    return sum(vals)/len(vals), vals

def main():
    OUT.mkdir(exist_ok=True)
    model=fit_evidence_model(generate_cases(n=6000,seed=901))
    dev_rows=[]
    for cost in CANDIDATE_COSTS:
        mean,vals=mean_dev_cost(model,cost)
        dev_rows.append({"investigation_cost":cost,"mean_dev_decision_cost":mean,"per_seed_costs":str([round(v,3) for v in vals])})
    dev=pd.DataFrame(dev_rows)
    selected=float(dev.loc[dev.mean_dev_decision_cost.idxmin(),"investigation_cost"])
    dev["selected"] = dev.investigation_cost==selected
    dev.to_csv(OUT/"investigation_cost_dev_selection.csv",index=False)
    records=[]
    for seed in TEST_SEEDS:
        cases=generate_cases(n=120,seed=seed)
        for policy in POLICIES:
            costs=Costs(investigate=selected)
            m=metrics(run_policy(policy,cases,model,costs,seed=seed))
            records.append({"seed":seed,"policy":policy,"decision_cost":m["decision_cost"],"false_accept":m["false_accept"],"false_reject":m["false_reject"],"investigations":m["investigations"],"probe_calls":m["probe_calls"],"event_recall":m["event_recall"],"event_precision":m["event_precision"],"brier":m["brier"]})
    raw=pd.DataFrame(records)
    raw.to_csv(OUT/"multiseed_20_raw.csv",index=False)
    summary=summarize_runs(records)
    summary.to_csv(OUT/"multiseed_20_summary.csv",index=False)
    (OUT/"multiseed_protocol.md").write_text(f"Development seeds: {DEV_SEEDS}. Test seeds: {TEST_SEEDS}. Candidate investigation costs: {CANDIDATE_COSTS}. Selected cost from development only: {selected:.1f}. The 20 test seeds were not used for cost selection.")
    return selected,dev,summary

if __name__=="__main__":
    selected,dev,summary=main()
    print("selected cost",selected)
    print(dev.to_string(index=False))
    print(summary.to_string(index=False))
