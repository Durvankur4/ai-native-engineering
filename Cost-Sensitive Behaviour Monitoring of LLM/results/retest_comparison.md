# Re-test Record

## Purpose

The previous 120-case run exposed two coupled problems in the active policy:

1. `INVESTIGATE` was effectively disabled because the implementation required positive value after an investigation cost of `1.0`, while the paper and decision record described a different cost.
2. The reported `expected_cost` for an investigation did not equal the expected post-probe decision loss plus probe cost.

A third problem came from failure analysis: degraded cases could preserve healthy aggregate quality and remain invisible to the observation model.

## Fixes

### Decision-cost correction

Investigation now follows an explicit two-step calculation:

`gross_VOI = current_direct_cost - expected_post_probe_direct_cost`

`net_VOI = gross_VOI - investigation_cost`

A discretionary investigation is selected only when:

`gross_VOI > investigation_cost`

The default hypothetical investigation cost is now `0.8`, matching the project decision record and paper. The reported expected cost is now:

`expected_post_probe_direct_cost + investigation_cost`

### Design change caused by the failure analysis

The dominant failure was an observational blind spot: a degraded case could have healthy aggregate quality, low semantic drift, normal latency, and low error rate. Retuning the decision threshold cannot recover information that is not observed.

The agent therefore adds a **capability-coverage audit**. Every fourth observation within each task category triggers a targeted capability probe, subject to the existing two-round investigation cap. This is a bounded coverage rule, not a claim that the audit is always higher value than a direct decision.

The targeted probe adds a `capability_issue` evidence event with explicit synthetic likelihood assumptions. The simulator forces this signal to appear in the known injected blind-spot cases so the design change can be tested directly.

## 120-case before/after re-test

| Policy | Before: False Accept | After: False Accept | Before: Investigations | After: Investigations | Before: Decision Cost | After: Decision Cost | Before: Recall | After: Recall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 23 | 23 | 0 | 0 | 242.0 | 242.0 | 0.549 | 0.549 |
| Binary | 21 | 21 | 0 | 0 | 222.0 | 222.0 | 0.588 | 0.588 |
| Active | 21 | 10 | 0 | 31 | 222.0 | 136.8 | 0.588 | 0.804 |

The active policy's investigation rate moved from `0%` to `25.8%`. False accepts fell by `52.4%`, and realized decision cost fell by `38.4%` on this synthetic 120-case run.

## Five classified failures from the new run

| Case | Failure class | What happened | Why it failed |
|---|---|---|---|
| `case-066` | Aggregate quality blind spot | `DEGRADED` was accepted without investigation. | The injected regression preserved healthy aggregate metrics and this case was outside the scheduled audit point. |
| `case-087` | Distribution-shift under-detection | `DISTRIBUTION_SHIFT` was accepted. | The evidence model still assigns substantial probability to stable behavior when the shift does not create a strong degradation signal. |
| `case-039` | Probe non-resolution | Investigation occurred, but the final action was `ACCEPT` on a drifting case. | The capability probe was not sufficiently specific for distribution shift, so evidence collection did not separate the competing states. |
| `case-027` | Quality-threshold false alarm | A stable case was rejected. | Quality fell below the 0.70 observation threshold even though semantic drift was low. |
| `case-080` | Measurement-noise false alarm | A stable case was investigated and then rejected. | The observation strongly resembled degradation, so the cost rule remained conservative after the probe. |

## Interpretation

The re-test establishes a metric movement under the revised implementation, but it does not prove production superiority. The scheduled audit rule is itself a design assumption, the probe likelihoods are synthetic, and the hidden state is known only to the simulator for scoring.

The new failure table is also useful because the remaining errors are structurally different. The capability audit reduces the original blind-spot failure, but it does not solve distribution shift or guarantee that an investigation resolves uncertainty. Those are separate evidence-model problems.
