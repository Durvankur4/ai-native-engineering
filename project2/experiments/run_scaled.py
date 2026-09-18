"""Run the 120-case scaled baseline/binary/active comparison."""
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt

from src.evaluate import run_policy, metrics
from src.simulator import generate_cases

N_CASES = 120
SEED = 7
POLICIES = ["baseline", "binary", "active"]


def main(out_dir="results"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cases = generate_cases(n=N_CASES, seed=SEED)

    rows = []
    for policy in POLICIES:
        df = run_policy(policy, cases)
        df.to_csv(out / f"{policy}_decisions_120.csv", index=False)
        m = metrics(df)
        rows.append({
            "policy": policy,
            "n": m["n"],
            "false_accept": m["false_accept"],
            "false_reject": m["false_reject"],
            "investigations": int((df["initial_action"] == "INVESTIGATE").sum()),
            "investigation_rate": m["investigation_rate"],
            "decision_cost": m["decision_cost"],
            "recall": m["degradation_recall"],
            "precision": m["degradation_precision"],
        })

    summary = pd.DataFrame(rows)
    summary.to_csv(out / "scale_120_summary.csv", index=False)
    (out / "scale_120_summary.json").write_text(json.dumps(rows, indent=2))

    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(POLICIES))
    width = 0.22
    ax.bar([i - width for i in x], summary["false_accept"], width, label="False ACCEPT")
    ax.bar(list(x), summary["false_reject"], width, label="False REJECT")
    ax.bar([i + width for i in x], summary["investigations"], width, label="Investigations")
    ax.set_xticks(list(x), [p.capitalize() for p in POLICIES])
    ax.set_ylabel("Cases")
    ax.set_title(f"120-case policy comparison (seed={SEED})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "scale_120_policy_comparison.png", dpi=160)
    plt.close(fig)

    return summary


if __name__ == "__main__":
    print(main().to_string(index=False))
