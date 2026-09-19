# Experiment Report

## Primary 50-case benchmark

| Policy | Cases | False Accept | False Reject | Investigations | Investigation Rate | Decision Cost | Recall | Precision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 50 | 9 | 3 | 0 | 0.0% | 99.0 | 0.609 | 0.824 |
| binary | 50 | 7 | 3 | 0 | 0.0% | 79.0 | 0.696 | 0.842 |
| active | 50 | 1 | 3 | 11 | 22.0% | 27.8 | 0.957 | 0.880 |

Seed: `7`.

## 120-case re-test

| Policy | Cases | False Accept | False Reject | Investigations | Investigation Rate | Decision Cost | Recall | Precision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 120 | 23 | 4 | 0 | 0.0% | 242.0 | 0.549 | 0.875 |
| binary | 120 | 21 | 4 | 0 | 0.0% | 222.0 | 0.588 | 0.882 |
| active | 120 | 10 | 4 | 31 | 25.8% | 136.8 | 0.804 | 0.911 |

## Before/after active comparison

| Metric | Before | After |
|---|---:|---:|
| False accepts | 21 | 10 |
| False rejects | 4 | 4 |
| Investigations | 0 | 31 |
| Investigation rate | 0.0% | 25.8% |
| Decision cost | 222.0 | 136.8 |
| Recall | 0.588 | 0.804 |
| Precision | 0.882 | 0.911 |

The 120-case active decision cost falls by 38.4%, and false accepts fall by 52.4%, relative to the retained pre-change run on the same seeded testbed.

The active policy does not claim superiority from these results. The comparison demonstrates that the revised implementation and the targeted capability-coverage design materially change behavior in the controlled synthetic environment.
