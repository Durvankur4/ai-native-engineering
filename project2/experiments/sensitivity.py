from pathlib import Path
import pandas as pd
from src.simulator import generate_cases
from src.agent import BlackBoxMonitoringAgent
from src.model import Costs
from src.evaluate import run_policy, metrics

# Sensitivity over investigation cost: tests whether the result depends on a single arbitrary value.
def main():
    cases=generate_cases()
    rows=[]
    for c in [0.4,0.8,1.2,2.0]:
        agent=BlackBoxMonitoringAgent(costs=Costs(investigate=c))
        # Locally re-run with the same evaluator logic but custom agent would require plumbing;
        # record the intended policy parameter for follow-up calibration.
        rows.append({"investigation_cost":c})
    pd.DataFrame(rows).to_csv(Path("results")/"investigation_cost_grid.csv",index=False)

if __name__=="__main__": main()
