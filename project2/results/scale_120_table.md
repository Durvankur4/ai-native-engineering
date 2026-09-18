# Section 18 — 120-case scaled experiment

The simulator was extended from the original 50-case run to 120 cases. The random seed remains fixed at `7`. The original 50-case state schedule is repeated to preserve the original first 50 cases exactly; additional observations are newly sampled by the same state-specific observation generator. All three policies receive the same 120 generated cases.

## Results

| Policy | Cases | False ACCEPT | False REJECT | Investigations | Investigation rate | Decision cost | Recall | Precision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 120 | 23 | 4 | 0 | 0.0% | 242.0 | 0.549 | 0.875 |
| binary | 120 | 21 | 4 | 0 | 0.0% | 222.0 | 0.588 | 0.882 |
| active | 120 | 21 | 4 | 0 | 0.0% | 222.0 | 0.588 | 0.882 |

## Figure

![120-case policy comparison](scale_120_policy_comparison.png)

## Interpretation

The scaled run preserves the same policy structure while increasing the sample size to 120 cases. The active policy did not investigate any case under the current hypothetical costs and two-probe budget, so its results are identical to the binary policy in this run. The experiment is a simulator-based generalization check, not evidence about production performance.
