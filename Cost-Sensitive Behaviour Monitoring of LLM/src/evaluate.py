import json, math, random
from pathlib import Path
import pandas as pd
from .agent import BlackBoxMonitoringAgent
from .model import BeliefState, Costs, EvidenceModel, NaiveEvidenceModel, MonitorPolicy, PROBES, STATES
from .simulator import generate_cases, make_investigation_probe

DEFAULT_PRIOR={"STABLE":0.72,"DEGRADED":0.12,"TRANSIENT":0.08,"DISTRIBUTION_SHIFT":0.08}


def fit_evidence_model(train_cases=None):
    train_cases=train_cases or generate_cases(n=6000,seed=901)
    return EvidenceModel.fit(train_cases,alpha=1.0)


def _final_decision(agent, belief, remaining):
    return agent.policy.decide_active(belief, probe_rounds=agent.policy.max_probe_rounds-remaining)


def run_policy(policy, cases, evidence_model=None, costs=None, seed=7):
    costs=costs or Costs(); model=evidence_model or fit_evidence_model(); policy_obj=MonitorPolicy(costs,model,max_probe_rounds=2)
    agent=BlackBoxMonitoringAgent(prior=DEFAULT_PRIOR,costs=costs,evidence_model=model,max_probe_rounds=2) if policy not in {"baseline","random_acquire","always_acquire","eig_one_step"} else None
    rows=[]
    rng=random.Random(seed+10000)
    for c in cases:
        if policy=="baseline":
            action="ACCEPT" if c.observation.quality>=0.70 else "REJECT"; initial_action=action; exp_cost=None; belief={}; probe_name=""; probes_used=0
        else:
            current_model = NaiveEvidenceModel() if policy == "binary_naive" else model
            b=BeliefState(dict(DEFAULT_PRIOR),current_model).normalize().update_full_observation(c.observation)
            current_policy_obj = MonitorPolicy(costs,current_model,max_probe_rounds=1 if policy=="voi_one_step" else 2)
            if policy=="random_acquire":
                probe_name=rng.choice(list(PROBES)); probes_used=1
                obs=make_investigation_probe(rng,c,probe_name)
                b=b.after_probe(probe_name,bool(obs.capability_issue if probe_name=="capability_issue" else probe_name in obs.evidence()))
                final=current_policy_obj.decide_state_aware(b); action=final.action; initial_action="INVESTIGATE"; exp_cost=costs.investigate+final.expected_cost; belief=b.probs
            elif policy=="always_acquire":
                probe_name="capability_issue"; probes_used=1
                obs=make_investigation_probe(rng,c,probe_name)
                b=b.after_probe(probe_name,bool(obs.capability_issue)); final=policy_obj.decide_state_aware(b)
                action=final.action; initial_action="INVESTIGATE"; exp_cost=costs.investigate+final.expected_cost
            elif policy=="voi_one_step":
                dec=current_policy_obj.decide_active(b,probe_rounds=0)
                if dec.action=="INVESTIGATE":
                    probe_name=dec.probe; probes_used=1
                    obs=make_investigation_probe(rng,c,probe_name)
                    present=bool(obs.capability_issue if probe_name=="capability_issue" else probe_name in obs.evidence())
                    b=b.after_probe(probe_name,present); final=current_policy_obj.decide_state_aware(b)
                    action=final.action; initial_action="INVESTIGATE"; exp_cost=costs.investigate+final.expected_cost; belief=b.probs
                else:
                    action=dec.action; initial_action=dec.action; exp_cost=dec.expected_cost; probe_name=""; probes_used=0
            elif policy=="eig_one_step":
                probe_name=max(PROBES,key=lambda p:current_model.information_gain(b,p)); probes_used=1
                obs=make_investigation_probe(rng,c,probe_name)
                present=bool(obs.capability_issue if probe_name=="capability_issue" else probe_name in obs.evidence())
                b=b.after_probe(probe_name,present); final=current_policy_obj.decide_state_aware(b)
                action=final.action; initial_action="INVESTIGATE"; exp_cost=costs.investigate+final.expected_cost; belief=b.probs
            else:
                if policy in {"binary","binary_naive"}:
                    dec=current_policy_obj.decide_binary(b)
                else:
                    dec=current_policy_obj.decide_active(b)
                if policy=="state_direct":
                    dec=agent.policy.decide_state_aware(b)
                initial_action=dec.action; action=dec.action; exp_cost=dec.expected_cost; belief=b.probs; probe_names=[]; probes_used=0; used_probes=set()
                while policy=="active" and action=="INVESTIGATE" and probes_used<2:
                    probes_used += 1
                    chosen_probe=dec.probe
                    used_probes.add(chosen_probe)
                    probe_names.append(chosen_probe)
                    probe=make_investigation_probe(random.Random(seed*10000+c.time_step*13+probes_used),c,chosen_probe)
                    present=bool(probe.capability_issue if chosen_probe=="capability_issue" else chosen_probe in probe.evidence())
                    b=b.after_probe(chosen_probe,present)
                    if probes_used>=2:
                        final=current_policy_obj.decide_state_aware(b); action=final.action; exp_cost=costs.investigate*probes_used+final.expected_cost; break
                    dec=current_policy_obj.decide_active(b,probe_rounds=probes_used,used_probes=used_probes)
                    if dec.action=="INVESTIGATE":
                        continue
                    action=dec.action; exp_cost=costs.investigate*probes_used+dec.expected_cost; break
                probe_name=";".join(probe_names)
                belief=b.probs
        if policy != "baseline" and "b" in locals():
            belief = b.probs
        true_cost = costs.state_action_cost(action, c.state) if action in {"ACCEPT","REJECT"} else 0.0
        true_cost += costs.investigate * probes_used
        rows.append({"case_id":c.case_id,"state":c.state,"category":c.category,"quality":c.observation.quality,"semantic_drift":c.observation.semantic_drift,"latency_ms":c.observation.latency_ms,"drift_event":c.drift_event,"initial_action":initial_action,"action":action,"probe":probe_name,"probes_used":probes_used,"cost":true_cost,"expected_cost":exp_cost,"belief":json.dumps(belief if 'belief' in locals() else {})})
    return pd.DataFrame(rows)


def metrics(df):
    n=len(df); fa=int(((df.action=="ACCEPT")&df.drift_event).sum()); fr=int(((df.action=="REJECT")&(~df.drift_event)).sum()); inv=int((df.initial_action=="INVESTIGATE").sum())
    detections=int(((df.action=="REJECT")&df.drift_event).sum()); actual=int(df.drift_event.sum()); positives=int((df.action=="REJECT").sum())
    recall=detections/actual if actual else 0; precision=detections/positives if positives else 0
    brier=float("nan")
    scored=[]
    for raw,truth in zip(df.belief,df.drift_event):
        try:
            b=json.loads(raw)
            if b:
                p_nonstable=1-float(b.get("STABLE",0.0)); scored.append((p_nonstable,float(truth)))
        except Exception:
            pass
    if scored: brier=sum((p-y)**2 for p,y in scored)/len(scored)
    state_rows={s:int((df.state==s).sum()) for s in STATES}
    state_reject={s:int(((df.state==s)&(df.action=="REJECT")).sum()) for s in STATES}
    return {"n":n,"false_accept":fa,"false_reject":fr,"investigations":inv,"investigation_rate":inv/n,"probe_calls":int(df.probes_used.sum()),"decision_cost":float(df.cost.sum()),"event_recall":recall,"event_precision":precision,"brier":brier,"state_counts":state_rows,"state_reject":state_reject}


def summarize_runs(run_rows):
    df=pd.DataFrame(run_rows)
    out=[]
    for policy,g in df.groupby("policy"):
        n=len(g); row={"policy":policy,"seeds":n}
        for metric in ["decision_cost","false_accept","false_reject","investigations","probe_calls","event_recall","event_precision","brier"]:
            vals=g[metric].astype(float); mean=vals.mean(); std=vals.std(ddof=1) if n>1 else 0.0; ci=1.96*std/math.sqrt(n) if n>1 else 0.0
            row[f"{metric}_mean"]=mean; row[f"{metric}_std"]=std; row[f"{metric}_ci95"]=ci
        out.append(row)
    return pd.DataFrame(out)


def run_suite(out_dir="results", n_cases=120, seed=7):
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    train=generate_cases(n=6000,seed=901); model=EvidenceModel.fit(train,alpha=1.0)
    cases=generate_cases(n=n_cases,seed=seed)
    policies=["baseline","binary_naive","binary","state_direct","random_acquire","always_acquire","eig_one_step","voi_one_step","active"]
    records=[]
    for policy in policies:
        df=run_policy(policy,cases,model,Costs(),seed=seed); df.to_csv(out/f"{policy}_decisions_{n_cases}.csv",index=False); records.append({"policy":policy,**metrics(df)})
    summary=[]
    for r in records:
        flat={"policy":r["policy"],"n":r["n"],"false_accept":r["false_accept"],"false_reject":r["false_reject"],"investigations":r["investigations"],"investigation_rate":r["investigation_rate"],"probe_calls":r["probe_calls"],"decision_cost":r["decision_cost"],"recall":r["event_recall"],"precision":r["event_precision"],"brier":r["brier"]}
        summary.append(flat)
    pd.DataFrame(summary).to_csv(out/f"policy_comparison_{n_cases}.csv",index=False)
    return records


def main(out_dir="results", n_cases=50, seed=7):
    return run_suite(out_dir,n_cases,seed)

if __name__=="__main__":
    print(pd.DataFrame([{k:v for k,v in r.items() if k!="state_counts" and k!="state_reject"} for r in main()]).to_string(index=False))
