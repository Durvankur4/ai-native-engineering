from pathlib import Path
import pandas as pd
from src.evaluate import run_policy, fit_evidence_model, metrics
from src.model import Costs
from src.simulator import generate_cases


def main():
    out=Path("results"); out.mkdir(exist_ok=True)
    model=fit_evidence_model(generate_cases(n=6000,seed=901)); cases=generate_cases(n=50,seed=7)
    rows=[]
    for c in [0.4,0.6,0.8,1.0,1.2,1.5,2.0]:
        m=metrics(run_policy("active",cases,model,Costs(investigate=c),seed=7))
        rows.append({"investigation_cost":c,"investigations":m["investigations"],"investigation_rate":m["investigation_rate"],"false_accept":m["false_accept"],"false_reject":m["false_reject"],"decision_cost":m["decision_cost"],"recall":m["event_recall"],"precision":m["event_precision"]})
    df=pd.DataFrame(rows); df.to_csv(out/"investigation_cost_grid.csv",index=False); return df
if __name__=="__main__": print(main().to_string(index=False))
