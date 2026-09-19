"""Generate confusion-matrix images (action vs. ground-truth drift) for each policy.

Reads results/{baseline,binary,active}_decisions.csv and writes one PNG per
policy into results/confusion_matrices/.

Usage:
    python3 plot_confusion.py
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

ACTIONS = ["ACCEPT", "INVESTIGATE", "REJECT"]
GROUND_TRUTH = ["NO DRIFT", "DRIFT"]


def build_matrix(df):
    # rows = ground truth (no drift / drift), cols = action taken
    mat = np.zeros((2, len(ACTIONS)), dtype=int)
    for _, row in df.iterrows():
        gt = 1 if row["drift_event"] else 0
        a = ACTIONS.index(row["action"])
        mat[gt, a] += 1
    return mat


def plot_matrix(mat, title, out_path):
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(mat, cmap="Blues")
    ax.set_xticks(range(len(ACTIONS)))
    ax.set_xticklabels(ACTIONS)
    ax.set_yticks(range(len(GROUND_TRUTH)))
    ax.set_yticklabels(GROUND_TRUTH)
    ax.set_xlabel("Policy action")
    ax.set_ylabel("Ground truth")
    ax.set_title(title)
    vmax = mat.max() if mat.max() > 0 else 1
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val = mat[i, j]
            color = "white" if val > vmax * 0.6 else "black"
            ax.text(j, i, str(val), ha="center", va="center",
                     color=color, fontsize=13, fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main(results_dir="results"):
    results_dir = Path(results_dir)
    out_dir = results_dir / "confusion_matrices"
    out_dir.mkdir(exist_ok=True)
    for policy in ["baseline", "binary", "active"]:
        csv_path = results_dir / f"{policy}_decisions.csv"
        if not csv_path.exists():
            print(f"skipping {policy}: {csv_path} not found (run the experiment first)")
            continue
        df = pd.read_csv(csv_path)
        mat = build_matrix(df)
        out_path = out_dir / f"{policy}_confusion_matrix.png"
        plot_matrix(mat, f"{policy.capitalize()} policy — action vs. ground truth", out_path)
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()