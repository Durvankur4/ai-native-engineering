# 120-Case Policy Comparison

| Policy | False Accept | False Reject | Investigations | Investigation Rate | Decision Cost | Recall | Precision |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 23 | 4 | 0 | 0.0% | 242.0 | 0.549 | 0.875 |
| Binary | 21 | 4 | 0 | 0.0% | 222.0 | 0.588 | 0.882 |
| Active | 10 | 4 | 31 | 25.8% | 136.8 | 0.804 | 0.911 |

Seed: `7`.

The active policy uses a capability-coverage audit every fourth observation within each task category, plus any discretionary investigation that satisfies the corrected VOI threshold. These results are a scaling/re-test artifact, not production evidence.
