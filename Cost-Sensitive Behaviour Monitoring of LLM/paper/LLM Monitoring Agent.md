# Active Cost-Sensitive Monitoring of Black-Box LLM Behavior

## 4. Probabilistic View

### 4.1 Problem as a partially observed decision process

A hosted language-model API exposes outputs and some runtime measurements but does not expose the provider's internal model state, deployment history, or the exact cause of a behavioral change. The monitoring problem can therefore be represented as a partially observed decision problem. Let the hidden state be

\[
S_t \in \{\text{STABLE},\text{DEGRADED},\text{TRANSIENT},\text{DISTRIBUTION\_SHIFT}\}.
\]

The monitor receives an observation

\[
O_t=(q,d,f,s,l,e,r,c),
\]

where `q` is task quality, `d` is semantic drift, `f` is formatting failure, `s` is a safety-shift indicator, `l` is latency, `e` is API error rate, `r` is retained feedback rate, and `c` is an optional capability-specific probe result. `feedback_rate` exists in the implementation as a retained field but is not currently used in belief updates. `capability_issue` is observable only through the targeted capability probe.

The agent must choose one of three actions:

| Action | Meaning |
|---|---|
| `ACCEPT` | Continue normal operation. |
| `INVESTIGATE` | Spend an additional evidence budget before taking the final action. |
| `REJECT` | Block, quarantine, or otherwise stop the current behavior. |

The hidden state is used by the simulator for evaluation, not by the agent at decision time.

### 4.2 Hidden state semantics

The four-state model intentionally separates persistent degradation, short-lived anomalies, and input-distribution changes. The states are not intended to identify the provider's internal cause with certainty.

| State | Operational interpretation |
|---|---|
| `STABLE` | Behavior remains consistent with the trusted reference condition. |
| `DEGRADED` | Persistent loss of expected capability. |
| `TRANSIENT` | Temporary anomaly or short-lived disruption. |
| `DISTRIBUTION_SHIFT` | The request population changes in a way that affects observed behavior. |

The simulator explicitly generates all four states. The limitation is not state generation but empirical validation: the probabilities and evidence likelihoods are synthetic assumptions and have not been calibrated against production traces.

### 4.3 Prior distribution

The initial belief is deliberately hypothetical and is the same for every case:

| Hidden state | Prior probability |
|---|---:|
| `STABLE` | 0.72 |
| `DEGRADED` | 0.12 |
| `TRANSIENT` | 0.08 |
| `DISTRIBUTION_SHIFT` | 0.08 |
| **Total** | **1.00** |

The prior is a reproducibility device, not an empirical estimate. It should not be interpreted as the expected frequency of these states in a real deployment.

### 4.4 Evidence model

The current model uses a naive-Bayes-style update. For evidence items \(E_1,\ldots,E_k\), the posterior is proportional to

\[
P(S=s\mid E_1,\ldots,E_k) \propto P(S=s)\prod_{i=1}^{k}P(E_i\mid S=s).
\]

This assumes that the evidence streams are conditionally independent given the hidden state. That assumption is convenient and auditable, but it is not demonstrated. For example, low quality, semantic drift, formatting problems, and API errors can be correlated during a single failure event.

The synthetic likelihood table used by the implementation is:

| Evidence event | STABLE | DEGRADED | TRANSIENT | DISTRIBUTION_SHIFT |
|---|---:|---:|---:|---:|
| Low output quality | 0.08 | 0.78 | 0.60 | 0.35 |
| Semantic drift | 0.10 | 0.72 | 0.58 | 0.70 |
| Formatting failure | 0.04 | 0.55 | 0.35 | 0.22 |
| Safety shift | 0.03 | 0.38 | 0.18 | 0.30 |
| High latency | 0.10 | 0.33 | 0.72 | 0.15 |
| High API error | 0.04 | 0.45 | 0.55 | 0.12 |
| Capability issue probe | 0.01 | 0.95 | 0.10 | 0.20 |

All seven columns in this table are synthetic hypotheses. They are inspectable in the implementation and are not presented as calibrated production probabilities.

### 4.5 Worked posterior update

A worked example uses the following observed evidence:

- low output quality
- semantic drift
- no formatting failure
- no safety shift
- normal latency
- no API error

For `DEGRADED`, the unnormalized contribution is calculated as:

```text
0.12 x 0.78 = 0.093600
0.093600 x 0.72 = 0.067392
0.067392 x 0.45 = 0.030326
0.030326 x 0.62 = 0.018802
0.018802 x 0.67 = 0.012598
0.012598 x 0.55 = 0.006929
```

The full set of state contributions is:

| State | Prior | Joint contribution |
|---|---:|---:|
| `STABLE` | 0.72 | 0.004634 |
| `DEGRADED` | 0.12 | 0.006929 |
| `TRANSIENT` | 0.08 | 0.001870 |
| `DISTRIBUTION_SHIFT` | 0.08 | 0.008005 |
| **Evidence probability** | | **0.021437** |

Normalizing by 0.021437 gives:

| State | Posterior probability |
|---|---:|
| `STABLE` | 21.6% |
| `DEGRADED` | 32.3% |
| `TRANSIENT` | 8.7% |
| `DISTRIBUTION_SHIFT` | 37.3% |
| **Total** | **100.0%** |

The evidence therefore changes the most likely explanation from `STABLE` under the prior to `DISTRIBUTION_SHIFT` under the posterior, but it does not produce a concentrated belief. Several states remain plausible.

## 5. Information Theory

### 5.1 Entropy is not the same as confidence

Belief uncertainty is measured with Shannon entropy:

\[
H(B)=-\sum_s P(s)\log_2 P(s).
\]

For the prior \((0.72,0.12,0.08,0.08)\),

\[
H_{before}=1.291\text{ bits}.
\]

For the worked posterior \((0.216,0.323,0.087,0.373)\),

\[
H_{after}=1.842\text{ bits}.
\]

Therefore,

\[
\Delta H=H_{after}-H_{before}=1.842-1.291=+0.551\text{ bits}.
\]

The uncertainty increased. This is not an arithmetic error. The evidence weakened the dominant `STABLE` hypothesis without strongly establishing a single alternative, so the belief mass became more distributed across multiple states.

For a realized evidence bundle, a negative information gain is possible because the particular observation can be more ambiguous than the prior. The active probe-selection problem is different: it uses **expected** information gain before observing the probe outcome.

### 5.2 Expected information gain for candidate probes

For a candidate binary probe \(X\), expected information gain is

\[
EIG(X)=H(B)-\left[P(X=1)H(B\mid X=1)+P(X=0)H(B\mid X=0)\right].
\]

Using the synthetic prior and the likelihood table, the candidate signals have the following expected information gains:

| Candidate probe | P(probe positive) | Expected information gain, bits | EIG / 0.8 cost units |
|---|---:|---:|---:|
| `capability_issue` | 0.1452 | 0.4099 | 0.5124 |
| `quality_low` | 0.2272 | 0.2399 | 0.2999 |
| `semantic_drift` | 0.2608 | 0.2386 | 0.2983 |
| `error_high` | 0.1364 | 0.1594 | 0.1992 |
| `format_failure` | 0.1404 | 0.1562 | 0.1952 |
| `latency_high` | 0.1812 | 0.1180 | 0.1475 |
| `safety_shift` | 0.1056 | 0.1067 | 0.1333 |

The division by 0.8 is only an illustrative information-per-investigation-unit ratio because the project does not yet measure source-specific monetary cost or probe time. It is not a claim that one bit has a stable monetary value.

Two design details matter here. First, `quality_low` is already observed in the initial observation, so it is not a discretionary probe choice. Second, `capability_issue` has the highest expected information gain in this synthetic prior but is reserved for the dedicated capability-coverage audit rather than the discretionary candidate set. The active discretionary selector currently considers semantic drift, formatting failure, safety shift, latency, and API error.

### 5.3 Value of information and entropy are complementary

The project does not equate information gain with decision value. A probe can reduce entropy without changing the preferred final action. Conversely, a probe can have modest entropy reduction but still be valuable if it often moves the posterior across the cost-sensitive accept/reject boundary.

The policy therefore uses one-step **decision-theoretic value of information** rather than entropy reduction alone:

\[
VOI_{gross}=C_{direct}-E[C_{post\mbox{-}probe}].
\]

A probe is worth purchasing only if the gross reduction in expected direct decision loss is greater than its investigation cost.

## 6. Evidence Selection

### 6.1 Candidate set

The discretionary probe selector considers five evidence sources:

1. semantic drift
2. formatting failure
3. safety shift
4. high latency
5. high API error

For each candidate, the model computes the expected direct decision loss after a positive probe result and after a negative probe result, weights the two cases by their predicted probabilities, and compares the resulting expected loss with the current direct loss.

The selector does not use a generic rule such as “choose the highest-entropy signal.” It uses the signal's expected impact on the final decision.

### 6.2 Why a capability probe was added separately

Failure analysis exposed a structural problem: a narrow degraded capability could coexist with healthy average quality, low semantic drift, normal latency, and low API errors. In such a case, no threshold adjustment can recover information that is not present in the observation layer.

The concrete design change was therefore a bounded capability-coverage audit. Every fourth observation within a task category triggers a `capability_issue` probe, subject to a maximum of two investigation rounds.

The capability probe has the following synthetic likelihoods:

| Hidden state | P(capability_issue) |
|---|---:|
| `STABLE` | 0.01 |
| `DEGRADED` | 0.95 |
| `TRANSIENT` | 0.10 |
| `DISTRIBUTION_SHIFT` | 0.20 |

This schedule is not claimed to be optimal. It is a targeted intervention motivated by an observed failure class.

### 6.3 Probe-cost knowledge gap

The project currently has one common investigation cost, 0.8 decision units. It does **not** contain empirically measured probe latency, compute usage, API pricing, or human-review time for each evidence source. Therefore a source-specific “bits per rupee” analysis would be fabricated if written as a measured result.

The paper instead reports expected information gain and clearly labels the 0.8 cost ratio as a synthetic sensitivity quantity. A production version should replace it with measured cost and latency for each probe type.

## 7. Decision Policy

### 7.1 Direct accept/reject threshold

The hypothetical action-cost model is:

| Outcome | Cost |
|---|---:|
| Correct `ACCEPT` | 0.0 |
| Correct `REJECT` | 0.0 |
| Investigation | 0.8 |
| False `REJECT` | 3.0 |
| False `ACCEPT` | 10.0 |

Let

\[
p=P(DEGRADED\mid E).
\]

The expected cost of accepting is

\[
C_{ACCEPT}=10p.
\]

The expected cost of rejecting is

\[
C_{REJECT}=3(1-p).
\]

At the break-even point,

\[
10p=3(1-p),
\]

so

\[
13p=3,
\]

and therefore

\[
p=\frac{3}{13}=0.230769.
\]

The implemented rule is therefore:

| Posterior P(DEGRADED) | Final direct action |
|---|---|
| \(p\le 0.230769\) | `ACCEPT` |
| \(p>0.230769\) | `REJECT` |

At exactly 0.230769, the implementation assigns the tie to `ACCEPT` because `accept_cost <= reject_cost`.

This threshold is derived from the declared costs. It is not an arbitrary 0.5 probability threshold.

### 7.2 Correct investigation threshold

The investigation rule previously mixed two quantities and reported an inconsistent expected cost. The revised implementation separates them:

\[
VOI_{gross}=C_{direct}-E[C_{post\mbox{-}probe}],
\]

\[
VOI_{net}=VOI_{gross}-C_{investigate}.
\]

A discretionary investigation is selected only when

\[
VOI_{gross}>C_{investigate}.
\]

With the current hypothetical investigation cost of 0.8, a probe must save more than 0.8 expected decision-cost units before it is purchased.

The expected cost stored for an investigation is

\[
E[C_{investigate}]=E[C_{post\mbox{-}probe}]+0.8.
\]

The implementation test verifies this accounting directly.

### 7.3 Bounded investigation budget

The monitor allows at most two probe rounds. The budget exists because an active monitor should not continue collecting evidence indefinitely while delaying an action.

The stopping rule is:

1. stop and act when gross VOI is no longer greater than the investigation cost, or
2. stop when two investigation rounds have been consumed.

After the budget is exhausted, the same cost-derived direct `ACCEPT`/`REJECT` rule is applied.

### 7.4 Scheduled audits versus discretionary VOI

The coverage audit is deliberately separate from discretionary VOI. A scheduled audit can fire because its task-category coverage condition is due even when the current one-step VOI calculation would not purchase a discretionary probe.

Therefore the paper makes no claim that **every** investigation is individually justified by the VOI threshold. The precise claim is narrower: discretionary investigations are cost-gated by VOI, while scheduled capability audits are a bounded coverage intervention introduced to address a demonstrated blind spot.

### 7.5 Human-control boundary

The current implementation does not emit a `HUMAN_REVIEW` action. Human review is treated as an operational boundary for cases where a real deployment would not accept an autonomous high-impact action on the available evidence.

The prototype therefore remains a decision gate rather than an autonomous incident commander.

## 8. Experiment

### 8.1 Primary 50-case benchmark

The primary evaluation contains 50 deterministic synthetic cases generated with random seed 7. Five task categories are used:

- `math`
- `code`
- `instruction`
- `safety`
- `knowledge`

The state schedule is deterministic. Cases 16 through 26 are `DEGRADED`; cases 31 through 35 plus cases 43 and 44 are `TRANSIENT`; cases 37 through 41 are `DISTRIBUTION_SHIFT`; all remaining cases are `STABLE`.

Two adversarial conditions are injected:

1. Cases 16 through 20 are a narrow degraded capability blind spot. Their aggregate quality remains around 0.84, semantic drift remains low, formatting remains valid, latency remains near normal, and API error rate remains low.
2. Case 30 is a stable measurement-noise case whose observed quality, semantic drift, formatting, latency, and error rate resemble degradation.

The same 50-case dataset is evaluated by three policies:

| Policy | Definition |
|---|---|
| Baseline | Accept when quality is at least 0.70, otherwise reject. |
| Binary | Use the belief update and the cost-derived direct accept/reject rule, but no active evidence collection. |
| Active | Use the belief update, corrected VOI-based investigation, a two-round budget, and the every-fourth-observation capability coverage audit. |

The hidden simulator state is used only after each decision to calculate the evaluation metrics.

### 8.2 120-case re-test

A second run contains 120 cases using the same random seed, 7, and the same 50-case state schedule repeated over the 120-case sequence. New observations are sampled within the repeated state schedule. This is a scaling and before/after re-test, not a statistically independent benchmark.

The retained pre-change 120-case run had an active policy that selected no investigations. The post-change run uses the corrected investigation accounting and the capability-coverage audit.

### 8.3 Evaluation metrics

For each policy, the following are reported:

- **False accept:** a case whose hidden simulator state is non-stable is finally accepted.
- **False reject:** a case whose hidden simulator state is stable is finally rejected.
- **Investigation count:** number of cases whose initial active action is `INVESTIGATE`.
- **Investigation rate:** investigation count divided by case count.
- **Decision cost:** realized sum of false-accept cost, false-reject cost, and investigation cost.
- **Recall:** final rejects among all cases whose simulator label is non-stable.
- **Precision:** true non-stable final rejects divided by all final rejects.

Because the implementation always converts an investigation into a final accept or reject decision, an `INVESTIGATE` action is not counted as a final detection.

## 9. Results

### 9.1 Primary 50-case results

The full primary comparison is:

| Policy | False Accept | False Reject | Investigations | Investigation Rate | Decision Cost | Recall | Precision |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 9 | 3 | 0 | 0.0% | 99.0 | 0.609 | 0.824 |
| Binary | 7 | 3 | 0 | 0.0% | 79.0 | 0.696 | 0.842 |
| **Active** | **1** | **3** | **11** | **22.0%** | **27.8** | **0.957** | **0.880** |

The active-policy decision-cost calculation is visible directly:

\[
1(10.0)+3(3.0)+11(0.8)=27.8.
\]

Relative to the static baseline in this 50-case synthetic run, active decision cost is reduced from 99.0 to 27.8, a reduction of 71.9%. False accepts fall from 9 to 1, an 88.9% reduction. Recall rises from 0.609 to 0.957, while the active policy performs 11 investigations.

The binary belief policy also improves on the static threshold, reducing false accepts from 9 to 7 and decision cost from 99.0 to 79.0 without any investigations. This isolates a useful point: probabilistic reasoning alone changes the result even before active information collection is added.

### 9.2 Confusion-style counts for the primary 50-case run

The final action confusion counts are printed below. `drift_event=True` means the simulator state is not `STABLE`.

#### Baseline

| Hidden evaluation label | Final ACCEPT | Final REJECT |
|---|---:|---:|
| Stable | 24 | 3 |
| Non-stable | 9 | 14 |

#### Binary

| Hidden evaluation label | Final ACCEPT | Final REJECT |
|---|---:|---:|
| Stable | 24 | 3 |
| Non-stable | 7 | 16 |

#### Active

| Hidden evaluation label | Final ACCEPT | Final REJECT |
|---|---:|---:|
| Stable | 24 | 3 |
| Non-stable | 1 | 22 |

The 50-case run therefore contains 23 non-stable and 27 stable cases.

### 9.3 120-case before/after re-test

The retained pre-change and post-change results are:

| Policy | Before Cost | After Cost | Before False Accept | After False Accept | Before Investigations | After Investigations | Before Recall | After Recall | Before Precision | After Precision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 242.0 | 242.0 | 23 | 23 | 0 | 0 | 0.549 | 0.549 | 0.875 | 0.875 |
| Binary | 222.0 | 222.0 | 21 | 21 | 0 | 0 | 0.588 | 0.588 | 0.882 | 0.882 |
| **Active** | **222.0** | **136.8** | **21** | **10** | **0** | **31** | **0.588** | **0.804** | **0.882** | **0.911** |

The post-change active policy therefore:

- reduces decision cost from 222.0 to 136.8, a reduction of 38.4%;
- reduces false accepts from 21 to 10, a reduction of 52.4%;
- raises recall from 0.588 to 0.804, an increase of 0.216 or 21.6 percentage points;
- raises precision from 0.882 to 0.911, an increase of 0.029 or 2.9 percentage points;
- increases investigation count from 0 to 31, moving the investigation rate from 0.0% to 25.8%.

There are 51 non-stable and 69 stable cases in the 120-case evaluation.

### 9.4 Post-change 120-case confusion counts

| Hidden evaluation label | Final ACCEPT | Final REJECT |
|---|---:|---:|
| Stable | 65 | 4 |
| Non-stable | 10 | 41 |

The pre-change active policy had 21 final false accepts and 4 final false rejects, while the post-change active policy has 10 false accepts and 4 false rejects. The improvement therefore comes primarily from converting accepted non-stable cases into rejected cases rather than reducing false rejection.

### 9.5 Investigation-cost sensitivity

The primary 50-case benchmark was rerun with investigation costs of 0.4, 0.6, 0.8, 1.0, and 1.2.

| Investigation cost | Investigations | Investigation rate | False Accept | False Reject | Decision Cost | Recall | Precision |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.4 | 11 | 22.0% | 1 | 3 | 23.4 | 0.957 | 0.880 |
| 0.6 | 11 | 22.0% | 1 | 3 | 25.6 | 0.957 | 0.880 |
| 0.8 | 11 | 22.0% | 1 | 3 | 27.8 | 0.957 | 0.880 |
| 1.0 | 10 | 20.0% | 1 | 3 | 29.0 | 0.957 | 0.880 |
| 1.2 | 10 | 20.0% | 1 | 3 | 31.0 | 0.957 | 0.880 |

Within this tested range, the qualitative detection metrics remain unchanged while investigation count changes slightly and realized cost rises with the investigation price. This supports the use of 0.8 as a documented synthetic cost assumption, but it does not establish that 0.8 is an optimal real-world cost.

## 10. Failure Analysis

### 10.1 Five failures from the 120-case re-test

The project was required to classify at least five failures from the new run. The five representative cases are:

| Case | State | Failure class | Initial action | Final action | Cost | Evidence of failure |
|---|---|---|---|---|---:|---|
| `case-066` | `DEGRADED` | Aggregate-quality blind spot | `ACCEPT` | `ACCEPT` | 10.0 | Quality 0.842, semantic drift 0.075, latency 379.9 ms, no extra probe. |
| `case-087` | `DISTRIBUTION_SHIFT` | Distribution-shift under-detection | `ACCEPT` | `ACCEPT` | 10.0 | Quality 0.807 and semantic drift 0.460 produce a posterior with `DISTRIBUTION_SHIFT` 0.260, but the direct `DEGRADED` probability is only 0.136. |
| `case-039` | `DISTRIBUTION_SHIFT` | Probe non-resolution | `INVESTIGATE` | `ACCEPT` | 10.8 | Capability audit fires, but the post-probe posterior still leads to `ACCEPT`. |
| `case-027` | `STABLE` | Quality-threshold false alarm | `REJECT` | `REJECT` | 3.0 | Quality 0.672 pushes the degraded posterior to 0.412 despite low semantic drift of 0.017. |
| `case-080` | `STABLE` | Measurement-noise false alarm | `INVESTIGATE` | `REJECT` | 3.8 | Quality 0.612 and semantic drift 0.466 create strong degraded-looking evidence; the capability probe does not reverse the decision. |

### 10.2 Failure 1: aggregate-quality blind spot

`case-066` is the clearest residual blind spot. It is truly `DEGRADED`, yet the measured quality is 0.842 and semantic drift is only 0.075. Its posterior after the available evidence is:

| State | Posterior |
|---|---:|
| `STABLE` | 0.857 |
| `DEGRADED` | 0.034 |
| `TRANSIENT` | 0.041 |
| `DISTRIBUTION_SHIFT` | 0.067 |

The active policy therefore accepts it. This failure cannot be fixed by merely lowering the decision threshold without creating more stable false alarms. The missing ingredient is a capability-specific observation.

### 10.3 Failure 2: distribution-shift under-detection

`case-087` is genuinely `DISTRIBUTION_SHIFT`. Its posterior is:

| State | Posterior |
|---|---:|
| `STABLE` | 0.472 |
| `DEGRADED` | 0.136 |
| `TRANSIENT` | 0.132 |
| `DISTRIBUTION_SHIFT` | 0.260 |

The most likely state is `STABLE`, and `P(DEGRADED)` remains below 0.230769, so the direct cost rule accepts the case. This identifies a policy-model mismatch: the evaluation labels all non-stable states as drift events, but the direct cost model only prices `DEGRADED` as the dangerous hidden state.

### 10.4 Failure 3: probe non-resolution

`case-039` is a scheduled capability audit. The probe is purchased, but the final outcome is still `ACCEPT`. The final posterior is:

| State | Posterior |
|---|---:|
| `STABLE` | 0.194 |
| `DEGRADED` | 0.183 |
| `TRANSIENT` | 0.207 |
| `DISTRIBUTION_SHIFT` | 0.415 |

This is an important negative result. Investigation is not equivalent to successful detection. A probe has value only if its outcome changes the downstream decision often enough to justify its cost.

### 10.5 Failure 4: quality-threshold false alarm

`case-027` is `STABLE`, but quality falls to 0.672. The posterior becomes:

| State | Posterior |
|---|---:|
| `STABLE` | 0.254 |
| `DEGRADED` | 0.412 |
| `TRANSIENT` | 0.211 |
| `DISTRIBUTION_SHIFT` | 0.123 |

The policy rejects because 0.412 is above 0.230769. The model interprets one noisy quality signal as strong evidence of persistent degradation. This motivates explicit evaluator-noise modeling and calibration.

### 10.6 Failure 5: measurement-noise false alarm

`case-080` is `STABLE`, but the initial evidence gives a very high `DEGRADED` posterior. After the capability audit, the final posterior remains:

| State | Posterior |
|---|---:|
| `STABLE` | 0.0014 |
| `DEGRADED` | 0.5959 |
| `TRANSIENT` | 0.3481 |
| `DISTRIBUTION_SHIFT` | 0.0546 |

The final action is therefore `REJECT`, producing a false-reject cost of 3.0 plus the 0.8 investigation cost, for a total of 3.8. The probe does not repair a strongly misleading initial observation.

### 10.7 What the failures imply

The failures separate into three broad mechanisms:

1. **Missing evidence:** the monitor cannot detect a capability failure that is invisible to aggregate quality and generic runtime checks.
2. **Loss-model mismatch:** distribution shift can be a real change without being treated as a directly harmful `DEGRADED` state by the current utility function.
3. **Evaluator uncertainty:** a poor observation can be produced by a stable case, so the probability model needs noise calibration and possibly repeated measurements.

The redesign therefore addresses one specific gap but does not claim to have solved black-box monitoring in general.

## 2. Introduction

Hosted LLM services create a monitoring problem that differs from conventional software observability. A conventional service can often expose version identifiers, internal state, structured error codes, and deterministic components. A hosted language model may instead expose a stable API name while its behavior changes over time. Chen, Zaharia, and Zou documented substantial behavioral variation between March and June 2023 versions of GPT-3.5 and GPT-4 across tasks including mathematics, coding, instruction following, and safety-sensitive questions. Their results show why one-time evaluation is not enough when the serving system is externally observable but internally opaque. [1]

The practical problem addressed here is narrower than “detect model drift” in general. It is the following decision problem:

> When the true state of a black-box LLM is hidden and evidence is incomplete, can a monitor use probabilistic belief and bounded additional evidence to reduce costly false acceptance compared with a static quality threshold?

The project is designed as an executable prototype rather than as a production monitoring claim. The latent states, priors, likelihoods, costs, and probe schedule are explicitly exposed so that each assumption can be challenged.

The central engineering choice is to separate three questions:

1. **What should the monitor believe?** Use a probabilistic belief over hidden states.
2. **What information should it seek next?** Estimate the expected value of an additional probe.
3. **When should it stop collecting evidence?** Compare information value against the probe cost and impose a hard two-round budget.

The experiment then asks whether those choices change measurable outcomes on a controlled synthetic testbed.

## 3. Related Work

### 3.1 LLM behavior drift

Chen, Zaharia, and Zou introduced LLMDrift to study how the behavior of hosted models changes over time. Their repeated evaluations showed that the same model service can vary across task families and that behavior changes are not limited to a single aggregate quality score. [1] This project shares the black-box monitoring premise but moves from measurement toward action selection: it asks not only whether a signal moved, but whether the monitor should accept, investigate, or reject.

The distinction between input distribution shift and model behavior change is also operationally important. A change in inputs does not imply a provider-side model update, while a provider-side update can change outputs even when the input distribution is stable. The four-state simulator therefore keeps `DEGRADED` and `DISTRIBUTION_SHIFT` as separate hypotheses even though the current loss model does not yet price them symmetrically.

### 3.2 Partial observability and active decision making

Partially Observable Markov Decision Processes provide a formal framework for decision making when the true state is hidden and observations are noisy. Lauri, Hsu, and Pajarinen survey this setting and emphasize belief-state reasoning as a natural representation for hidden-state control problems. [2]

This project uses only a small static approximation of that idea. It maintains a belief over four hidden states, but it does not implement a full POMDP solver, transition model, dynamic programming solution, or learned policy. The active action is a one-step probe choice followed by a direct cost-sensitive decision.

### 3.3 LLM-as-a-judge and evaluator reliability

The monitoring problem depends heavily on the quality of the observation layer. Recent work shows that automated LLM evaluators are not automatically reliable. Fu and Liu found substantial inconsistency in multilingual LLM-as-a-Judge settings, including an average Fleiss' kappa of approximately 0.3 across their evaluated conditions. [3] Lee et al. proposed checklist-style evaluation to reduce evaluator variance and improve interpretability. [4] Work on Agent-as-a-Judge similarly argues that evaluating agent behavior requires more than inspecting a final scalar outcome and can benefit from intermediate signals. [5]

These results matter directly to this project. A monitor that treats its evaluator score as ground truth can turn evaluator noise into false alarms or false confidence. The failure cases in Section 10 show both directions: a stable case can look degraded, while a degraded case can look healthy.

### 3.4 Position of the present prototype

The contribution is therefore not a claim of a new general-purpose monitoring algorithm. It is an integrated, inspectable prototype that combines:

- an explicit hidden-state belief model;
- an asymmetric cost-derived accept/reject boundary;
- one-step value-of-information probe selection;
- a bounded investigation budget;
- a concrete evidence-coverage intervention based on observed failures; and
- a before/after re-test showing whether the intervention changes measured behavior.

The remaining validation burden is empirical calibration, repeated-seed testing, real trace replay, evaluator agreement measurement, and ablation of the active components.

## 11. Discussion, Reproducibility, and Design Implications

### 11.1 What the primary experiment supports

The primary 50-case run supports three limited conclusions.

First, probabilistic reasoning changes the decision surface. The binary belief policy reduces false accepts from 9 to 7 and decision cost from 99.0 to 79.0 compared with the static quality threshold.

Second, active evidence collection can materially change the result in the constructed testbed. The active policy reaches 1 false accept, 3 false rejects, 11 investigations, and 27.8 total decision cost.

Third, the active intervention is valuable partly because it adds evidence that the original observation layer did not contain. The capability-coverage audit is therefore better understood as an observation-layer redesign than as a mere threshold tweak.

### 11.2 What the re-test supports

The 120-case re-test provides the clearest engineering evidence in the project because it retains the pre-change result and executes the post-change policy on the same seeded test setup.

The active policy moves from:

| Metric | Before | After |
|---|---:|---:|
| False accepts | 21 | 10 |
| False rejects | 4 | 4 |
| Investigations | 0 | 31 |
| Investigation rate | 0.0% | 25.8% |
| Decision cost | 222.0 | 136.8 |
| Recall | 0.588 | 0.804 |
| Precision | 0.882 | 0.911 |

The observed movement is consistent with the intended mechanism: more cases receive additional evidence, and fewer non-stable cases are accepted.

However, the re-test does **not** isolate the causal contribution of each code change. The investigation-accounting correction and the capability-coverage audit were introduced together. The largest change in behavior is expected to come from the new audit, but the experiment does not separately estimate the effect of the threshold correction.

### 11.3 Why cost should be treated as a scenario parameter

The sensitivity run shows that changing the investigation cost from 0.4 to 1.2 changes realized decision cost from 23.4 to 31.0 and changes investigations from 11 to 10, while recall and precision remain 0.957 and 0.880 across all five tested values.

This is useful for the model because it means the architecture does not depend on one fragile scalar. At the same time, the cost values remain hypothetical. A real deployment should estimate investigation cost from API charges, latency, reviewer time, opportunity cost, and the business impact of delaying a final action.

### 11.4 Reproducibility procedure

The final project was re-executed with:

```text
pytest -q
```

The result was:

```text
6 passed in 0.05s
```

The primary benchmark was executed with:

```text
python -m experiments.run_experiment
```

using 50 cases and seed 7.

The 120-case re-test was executed with:

```text
python -m experiments.run_scaled
```

using 120 cases and seed 7.

The investigation-cost sensitivity experiment was executed with:

```text
python -m experiments.sensitivity
```

using investigation costs 0.4, 0.6, 0.8, 1.0, and 1.2.

The project therefore contains executable evidence for the reported tables rather than only manually typed results.

## 12. Limitations and Knowledge Gaps

The most important unresolved questions are listed explicitly because each one can change the interpretation of the results.

| Knowledge gap | Why it matters | Current status | Required next test |
|---|---|---|---|
| Prior calibration | Posterior quality depends on the starting belief. | Prior 0.72/0.12/0.08/0.08 is hypothetical. | Estimate priors from labeled incident history or replay traces. |
| Likelihood calibration | Synthetic likelihoods can make the Bayesian model look stronger or weaker than it really is. | All likelihoods are hand-specified. | Fit likelihoods from labeled observations and measure calibration. |
| Conditional dependence | Correlated evidence can lead naive Bayes to overcount evidence. | Independence is assumed, not tested. | Compare naive Bayes against a calibrated discriminative or graphical model. |
| Distribution-shift validation | The simulator contains shift states, but real shift signatures are not validated. | Synthetic only. | Add input-distribution features and real replay labels. |
| Multi-state loss function | Current direct decision cost is based only on `P(DEGRADED)`. | Distribution shift can be detected probabilistically but is not directly priced. | Define state-specific action losses and compare them with a scalar degraded-risk rule. |
| Probe quality | Investigation is useful only if the probe is selective enough to change decisions. | Five failure classes include probe non-resolution. | Measure probe sensitivity, specificity, and decision-change rate. |
| Probe cost and latency | 0.8 is a synthetic action cost, not a measured operational cost. | Source-specific time and monetary cost are missing. | Log API cost, wall-clock latency, compute, and human-review time for each probe. |
| Audit frequency | Every fourth observation is a hand-designed schedule. | Not learned or optimized. | Compare intervals such as 2, 4, 8 and adaptive schedules under repeated seeds. |
| VOI attribution | The current re-test changes VOI accounting and adds the audit together. | Causal contribution is confounded. | Run binary, random-probe, VOI-probe, and audit-only ablations. |
| Temporal persistence | The current belief is reinitialized per case. | No temporal filtering across cases. | Add a state-transition model and persistent belief updates. |
| Repeated-seed uncertainty | One seed cannot quantify variance across synthetic workloads. | Primary and scaled runs use seed 7. | Repeat across many seeds and report confidence intervals. |
| Evaluator reliability | A noisy evaluator can create false alarms or miss failures. | Known failure classes demonstrate this risk. | Compare automated evaluation against human or reference labels and measure agreement. |
| Historical replay | Synthetic labels are controlled but artificial. | Historical replay path is not yet part of the experiment. | Replay real incidents with frozen prompts and model settings where available. |
| Human escalation | The code does not emit a human-review action. | Human review is treated as an operational boundary. | Add explicit review cost and a three-way final policy if the deployment requires it. |
| Probe adversarial robustness | A targeted probe can itself be sensitive to framing, prompt, or context. | Not tested. | Evaluate probe stability under paraphrase and adversarial inputs. |

### 12.1 Statistical limitation

The reported reductions are descriptive results on one deterministic synthetic workload. The paper does not provide confidence intervals, hypothesis tests, or a claim of generalization beyond that workload.

### 12.2 Ground-truth limitation

The simulator knows its own hidden state, which is useful for controlled evaluation but unlike production monitoring where the true state is usually delayed, partial, or disputed. In particular, the project does not prove that a real `DISTRIBUTION_SHIFT` label would be available at decision time.

### 12.3 Cost-model limitation

The false-accept cost of 10.0, false-reject cost of 3.0, and investigation cost of 0.8 define a synthetic utility surface. Different organizations would rationally use different numbers. Changing those values can change the decision boundary and the frequency of investigation without changing the underlying belief model.

### 12.4 Calibration limitation

A posterior of 0.80 is currently a model output, not a demonstrated statement that roughly 80% of comparable cases are degraded. Calibration must be measured on independent labeled data before posterior values are interpreted operationally.

## 13. Conclusion

This project implements a compact black-box LLM monitoring agent that treats the monitored system as a hidden-state process and combines probabilistic belief, information theory, active evidence selection, and cost-sensitive action.

The main engineering result is not a claim of production superiority. It is a reproducible demonstration that changing the **information available to the monitor** can matter more than simply moving a final decision threshold.

In the primary 50-case synthetic benchmark, the static quality baseline records 9 false accepts and 3 false rejects at a total decision cost of 99.0. The binary belief policy reduces those values to 7 false accepts, 3 false rejects, and 79.0 cost. The active policy records 1 false accept, 3 false rejects, 11 investigations, and 27.8 cost.

More importantly, the 120-case before/after re-test shows a measurable movement after the design intervention. Active decision cost falls from 222.0 to 136.8, false accepts fall from 21 to 10, investigations rise from 0 to 31, recall increases from 0.588 to 0.804, and precision increases from 0.882 to 0.911.

The failure analysis prevents overinterpretation. The redesigned monitor still misses distribution shifts, can investigate without resolving uncertainty, and can reject stable cases when the evaluator evidence is misleading. These are not side notes. They identify the next research tasks: empirical likelihood calibration, probe-quality measurement, multi-state loss functions, repeated-seed evaluation, historical incident replay, evaluator-agreement studies, and ablation of the active components.

The appropriate conclusion is therefore bounded: **the prototype supports the hypothesis that bounded active evidence collection can improve cost-sensitive monitoring decisions in a controlled synthetic black-box LLM testbed, but the evidence is not sufficient to establish calibrated real-world performance.**

## References

[1] Lingjiao Chen, Matei Zaharia, and James Zou. “How is ChatGPT's behavior changing over time?” arXiv:2307.09009, 2023. The study compares March and June 2023 versions of GPT-3.5 and GPT-4 across multiple task families and reports substantial behavior changes. https://arxiv.org/abs/2307.09009

[2] Mikko Lauri, David Hsu, and Joni Pajarinen. “Partially Observable Markov Decision Processes in Robotics: A Survey.” arXiv:2209.10342, 2022. https://arxiv.org/abs/2209.10342

[3] Xiyan Fu and Wei Liu. “How Reliable is Multilingual LLM-as-a-Judge?” Findings of the Association for Computational Linguistics: EMNLP 2025, pages 11040-11053. https://aclanthology.org/2025.findings-emnlp.587/

[4] Yukyung Lee, JoongHoon Kim, Jaehee Kim, Hyowon Cho, Jaewook Kang, Pilsung Kang, and Najoung Kim. “CheckEval: A reliable LLM-as-a-Judge framework for evaluating text generation using checklists.” EMNLP 2025, pages 15771-15798. https://aclanthology.org/2025.emnlp-main.796/

[5] Mingchen Zhuge et al. “Agent-as-a-Judge: Evaluate Agents with Agents.” ICML 2025. https://icml.cc/virtual/2025/poster/45485

[6] Claude E. Shannon. “A Mathematical Theory of Communication.” Bell System Technical Journal, 27(3), 379-423 and 27(4), 623-656, 1948.

## 22. AI-use statement

OpenAI ChatGPT was used as a research and engineering assistant during the development and revision of this project. The model was used for specific, reviewable tasks rather than being treated as an authority on the experimental result.

### Tasks supported by ChatGPT

ChatGPT was used to:

1. clarify the problem formulation as a hidden-state, partially observable monitoring problem;
2. derive the cost-sensitive accept/reject threshold from the stated false-accept and false-reject costs;
3. check the Bayesian update and entropy calculations, including the correction that the worked evidence example increases entropy from 1.291 bits to 1.842 bits, a change of +0.551 bits;
4. inspect the investigation implementation and identify the mismatch between gross value of information, net value of information, and the reported expected investigation cost;
5. revise the investigation rule to require `gross_VOI > investigation_cost` and to report post-probe expected decision cost plus investigation cost;
6. review failure cases and help define the five failure classes used in the re-test;
7. propose and implement the bounded capability-coverage audit that was introduced because aggregate quality could remain healthy while a capability degraded;
8. reorganize and proofread the paper, including the tables and numerical narrative;
9. identify literature relevant to black-box LLM drift, partially observable decision making, and evaluator reliability; and
10. check the project for remaining methodological gaps that require future experiments rather than unsupported claims.

### Verification performed outside the model's prose generation

The following numerical and implementation details were checked explicitly against the project files and experiment outputs:

- the prior values 0.72, 0.12, 0.08, and 0.08 sum to 1.00;
- the worked posterior values 21.6%, 32.3%, 8.7%, and 37.3% sum to 100.0% after normalization;
- the entropy calculation uses 1.291 bits before evidence and 1.842 bits after evidence, giving +0.551 bits;
- the cost-derived decision threshold is 3/13 = 0.230769;
- the active 50-case cost is 1(10.0) + 3(3.0) + 11(0.8) = 27.8;
- the 120-case active before/after decision costs are 222.0 and 136.8;
- the 120-case false accepts are 21 before the redesign and 10 after it;
- the five representative failure classifications correspond to `case-066`, `case-087`, `case-039`, `case-027`, and `case-080`; and
- the final automated test suite reports 6 passed tests.

### Experiments executed for the final revision

The final project environment was re-executed with the following commands:

```text
pytest -q
```

Result: **6 passed**.

```text
python -m experiments.run_experiment
```

Configuration: **50 cases, seed 7**, comparing baseline, binary, and active policies.

```text
python -m experiments.run_scaled
```

Configuration: **120 cases, seed 7**, retaining the pre-change active results for before/after comparison.

```text
python -m experiments.sensitivity
```

Configuration: investigation costs **0.4, 0.6, 0.8, 1.0, and 1.2** on the 50-case benchmark.

### Human responsibility

The mathematical assumptions, synthetic likelihoods, costs, simulator design, interpretation of failures, and conclusions remain subject to human review. ChatGPT output was treated as editable analysis and code-review input. It was not treated as experimental ground truth. The reported results come from the executable project and the listed experiment runs, while the paper distinguishes measured synthetic results from hypothetical assumptions and unresolved research questions.

## Abstract

Hosted language-model APIs can change observable behavior while exposing little information about the provider-side cause of that change. This paper presents a small active monitor for that setting. The monitor maintains a probabilistic belief over four hidden states, `STABLE`, `DEGRADED`, `TRANSIENT`, and `DISTRIBUTION_SHIFT`, and chooses among `ACCEPT`, `INVESTIGATE`, and `REJECT` under asymmetric synthetic costs. A naive-Bayes-style evidence model combines task quality, semantic drift, formatting, safety, latency, and API-error signals. A one-step value-of-information rule determines whether a discretionary probe is worth its fixed investigation cost, while a hard two-round budget prevents unbounded evidence collection.

The main engineering correction was to separate gross value of information from investigation cost and to report the actual expected post-probe decision cost. Failure analysis then exposed a structural observation gap: some degraded cases maintained healthy aggregate quality and runtime signals. A bounded capability-coverage audit was introduced every fourth observation within each task category.

On the deterministic 50-case benchmark, the static quality baseline produced 9 false accepts, 3 false rejects, and total decision cost 99.0. The binary belief policy produced 7 false accepts, 3 false rejects, and cost 79.0. The redesigned active policy produced 1 false accept, 3 false rejects, 11 investigations, and cost 27.8. In the 120-case before/after re-test, active decision cost fell from 222.0 to 136.8 and false accepts fell from 21 to 10, while recall increased from 0.588 to 0.804.

The results are synthetic and use hypothetical priors, likelihoods, and costs. The paper therefore does not claim calibrated probabilities or production superiority. Its main result is narrower: in a controlled black-box monitoring testbed, bounded additional evidence can change cost-sensitive decisions materially, and failure analysis shows that better decision rules cannot compensate for evidence that the observation layer does not contain.
