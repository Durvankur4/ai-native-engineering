# Experiment Report

| Policy | False Accept | False Reject | Investigation | Decision Cost | Recall | Precision |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 11 | 1 | 0% | 137.0 | 0.522 | 0.923 |
| binary | 4 | 2 | 10% | 58.0 | 0.826 | 0.905 |
| active | 4 | 1 | 10% | 57.0 | 0.826 | 0.950 |

Interpretation: the active policy used a bounded investigation path and achieved lower decision cost than the binary policy in this synthetic run. The result is a hypothesis-generating experiment, not evidence of deployment superiority.