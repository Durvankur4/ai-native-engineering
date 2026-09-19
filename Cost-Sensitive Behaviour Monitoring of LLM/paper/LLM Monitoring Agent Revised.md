# Active Cost-Sensitive Monitoring of Black-Box LLM Behavior

## Abstract

Hosted large language model APIs expose outputs and runtime signals while hiding deployment state and the causes of behavioral change. This paper studies a monitoring agent that chooses ACCEPT, INVESTIGATE, or REJECT under uncertainty about four hidden states: STABLE, DEGRADED, TRANSIENT, and DISTRIBUTION_SHIFT. An earlier prototype multiplied marginal evidence likelihoods, collapsed the state model to a DEGRADED-versus-not-DEGRADED threshold, and implemented only one-step acquisition despite a two-round budget. The revised monitor fits a joint six-channel evidence model from 6,000 separate synthetic training cases, assigns explicit action costs to all four states, and performs two-step decision-aware value-of-information planning with probe reuse forbidden. The simulator deliberately introduces correlated evidence channels. Investigation cost is selected on five development seeds and locked at 0.4 before evaluation on 20 held-out seeds of 120 cases each. The active policy has mean decision cost 81.51 plus or minus 3.70 at a 95 percent t confidence level, event recall 0.968 plus or minus 0.011, event precision 0.962 plus or minus 0.010, 84.1 investigated cases, and 84.9 total probe calls per 120 cases. One-step VOI costs 84.92 plus or minus 3.97, EIG costs 92.75 plus or minus 3.83, and always-acquire costs 99.60 plus or minus 4.63. The active policy therefore uses 29.3 percent fewer probe calls than always-acquire while achieving lower mean decision cost. The remaining gaps are substantial: there are no human-reviewed production traces, probe costs are hypothetical, sequential probe outcomes remain conditionally independent given state, and the synthetic state semantics are not externally validated. The contribution is a reproducible probabilistic decision framework and controlled evidence-acquisition benchmark, not a production-monitoring validation.

## 1. Introduction

Externally hosted LLM services can change behavior even when the service interface remains stable. Public evaluations have documented substantial changes across model versions and tasks, including shifts in reasoning, safety behavior, instruction following, and code formatting, motivating continuous monitoring rather than one-time acceptance testing [1]. The monitoring problem becomes harder when the observer cannot inspect provider-side state, deployment history, or internal causes.

This paper considers a narrower decision problem:

> Given externally observable LLM evidence and a hidden behavioral state, which action should a monitor take, and when is additional evidence worth acquiring?

The agent has three actions. ACCEPT continues operation. REJECT blocks or quarantines the current behavior. INVESTIGATE acquires an additional probe before the final action. The core difficulty is that evidence is incomplete, acquisition is costly, and different hidden states have different consequences.

The original prototype treated six observable signals as conditionally independent given state, used only the posterior probability of DEGRADED in the decision threshold, and described a two-round investigation budget while evaluating only one probe. Review of that design exposed four further problems. The benchmark used a single seed. Acquisition baselines were narrow. Statistical uncertainty was not reported. The decision-cost model did not distinguish persistent degradation from transient anomalies or distribution shift.

We revise the system rather than merely listing these issues as limitations. The initial evidence model now uses a complete joint likelihood over the six binary evidence channels. The synthetic generator contains a shared latent failure pressure so evidence channels can co-vary. The main policy uses a four-state loss matrix. Acquisition is planned over a two-probe horizon. The evaluation compares random, always-acquire, entropy-greedy, one-step VOI, and two-step VOI policies. Investigation cost is selected on a development split rather than tuned on the held-out test set. Results are reported over 20 independent test seeds with 95 percent confidence intervals.

The resulting contribution is intentionally modest. The paper does not claim that the policy is production-ready. Because the revision changes the evidence model, state costs, and acquisition horizon together, the comparison is an engineering ablation within one controlled simulator rather than a causal proof that any single component explains the full improvement. It demonstrates a reproducible way to combine probabilistic state estimation, information theory, acquisition costs, and finite-horizon planning for black-box LLM monitoring, and it exposes the conditions under which the policy still fails.

## 2. Related Work

LLM monitoring is motivated by evidence that model behavior can vary substantially over time and across task categories. Chen et al. evaluated different versions of GPT-3.5 and GPT-4 across diverse tasks and found meaningful behavioral shifts, including changes in mathematical reasoning, instruction following, safety responses, and code formatting [1]. This establishes the operational motivation for continuous black-box evaluation but does not specify how a monitor should decide when to seek more evidence.

The decision problem is naturally related to partially observable Markov decision processes. POMDP formulations separate hidden state, observations, actions, and belief updates, while exact planning is often computationally expensive [2]. Our benchmark is deliberately simpler than a general POMDP because the hidden state is static during a case and the monitor acts mainly through information-gathering actions.

Active feature acquisition is the closest methodological family. Surveys organize acquisition policies into greedy, embedded, model-based, model-free, and hybrid approaches, emphasizing the trade-off between information value and acquisition cost [3]. Li and Oliva formulate active acquisition as an acquisition POMDP in which an agent can purchase information before making a decision, with explicit dependencies between hidden features and acquisition actions [4]. Our setting is narrower and uses a short finite horizon with an inspectable probabilistic model rather than reinforcement learning.

Change-point and drift-detection literature addresses non-stationarity and state transitions in streams. Truong et al. review multivariate change-point methods in terms of cost functions, search strategies, and constraints [5]. The present work does not replace such detectors. Instead, it treats distribution shift as one hidden explanation and asks a complementary question: after an observed anomaly, which additional measurement is worth acquiring before acting?

The work therefore sits at the intersection of LLM behavior monitoring, POMDP-style belief reasoning, active feature acquisition, and cost-sensitive decision making. The main distinction is that the evaluation explicitly couples evidence acquisition with a four-state monitoring loss rather than optimizing predictive accuracy alone.

## 3. Problem Formulation and Design Goals

Let the hidden state be

S = {STABLE, DEGRADED, TRANSIENT, DISTRIBUTION_SHIFT}.

The initial prior is hypothetical:

| State | Prior |
|---|---:|
| STABLE | 0.72 |
| DEGRADED | 0.12 |
| TRANSIENT | 0.08 |
| DISTRIBUTION_SHIFT | 0.08 |
| Total | 1.00 |

The prior is a reproducibility assumption, not an empirical deployment frequency.

Each case begins with six observable channels:

1. output quality below 0.70;
2. semantic drift above 0.30;
3. formatting failure;
4. safety shift;
5. latency above 900 ms;
6. API error rate above 0.08.

An optional capability probe is acquired later. The simulator also generates a task category from math, code, instruction, safety, and knowledge.

The revised design has five goals.

First, the initial belief model should not require conditional independence across the six evidence channels when the simulator itself generates correlated evidence. Second, the final decision should account for all four latent states. Third, acquisition should consider a second probe when it has positive expected value rather than stopping after one calculation. Fourth, the evaluation should separate development decisions from held-out test results. Fifth, the paper should show where the system fails rather than reporting only aggregate success.

## 4. Probabilistic View

### 4.1 Belief state

The monitor maintains a probability distribution b(s) over the four hidden states. Before observing a case, the belief is the hypothetical prior above. After an observation x, Bayes' rule gives

P(S=s | x) = P(S=s) P(x | S=s) / sum_s' P(S=s') P(x | S=s').

The important revision is the form of P(x | s).

### 4.2 Joint initial evidence model

The earlier prototype approximated the joint evidence probability as a product of marginal probabilities:

P(x | s) approximately equal to product over i of P(E_i | s).

That assumption is not justified when signals co-vary. To address it, the revised simulator introduces a shared latent failure-pressure variable that perturbs quality, semantic drift, formatting probability, latency, and error rate together. The average absolute pairwise correlation among the six binary evidence indicators in 6,000 training cases is 0.265 for STABLE and 0.319 for DEGRADED, with maximum pairwise absolute correlations of 0.728 and 0.936 respectively. Several binary channels are constant within TRANSIENT or DISTRIBUTION_SHIFT in this simulator, so some within-state pairwise correlations are undefined rather than evidence of independence.

The new evidence model fits the complete six-bit evidence signature. For every state s and signature z in {0,1}^6, the model estimates

P(z | s) = (N(z,s) + alpha) / (N(s) + 64 alpha),

with alpha = 1 Laplace smoothing. Training uses 6,000 synthetic cases generated with seed 901. Test cases are generated from different seeds.

This removes the conditional-independence assumption for the six initial channels. A narrower assumption remains for repeated probes: after the initial observation, probe outcomes are treated as conditionally independent given the hidden state. This is explicit and appears again in the limitations.

### 4.3 Worked posterior example

Consider an observation with low quality, semantic drift, no formatting failure, no safety shift, normal latency, and no high API error. The six-bit signature is (1,1,0,0,0,0). The learned joint likelihoods for this exact signature are:

| State | P(signature | state) |
|---|---:|
| STABLE | 0.000303 |
| DEGRADED | 0.010116 |
| TRANSIENT | 0.001106 |
| DISTRIBUTION_SHIFT | 0.093373 |

Multiplying these likelihoods by the priors and normalizing gives:

| State | Posterior probability |
|---|---:|
| STABLE | 2.42% |
| DEGRADED | 13.50% |
| TRANSIENT | 0.98% |
| DISTRIBUTION_SHIFT | 83.09% |
| Total | 100.00% |

The prior entropy is 1.291 bits. The posterior entropy is 0.808 bits, so the realized entropy change is -0.484 bits. Unlike the earlier marginal-product example, the joint model can sharply concentrate probability because it recognizes that the complete evidence pattern is highly characteristic of distribution shift in the synthetic training distribution.

The point is not that this posterior is realistic. It is that the inference mechanism and its dependence assumptions are now explicit and testable.

## 5. Information Theory

### 5.1 Entropy

For belief vector b,

H(b) = - sum_s P(s) log2 P(s).

The prior entropy of (0.72, 0.12, 0.08, 0.08) is 1.291 bits. The worked posterior above has entropy 0.808 bits. This example therefore reduces uncertainty by 0.484 bits.

Entropy is not a decision objective by itself. A probe can reduce uncertainty about a state that does not affect the preferred action. The monitor therefore uses both entropy-based and decision-based acquisition baselines.

### 5.2 Expected information gain

For a binary probe X,

EIG(X) = H(B) - P(X=1) H(B | X=1) - P(X=0) H(B | X=0).

At the synthetic prior, the main candidate probes have:

| Probe | P(positive) | EIG, bits |
|---|---:|---:|
| capability_issue | 0.1452 | 0.4099 |
| error_high | 0.1888 | 0.3380 |
| latency_high | 0.0717 | 0.3169 |
| semantic_drift | 0.1836 | 0.2043 |
| format_failure | 0.1071 | 0.0177 |
| safety_shift | 0.0094 | 0.0057 |

These values are calculated from the learned synthetic observation model. They are not production information rates.

### 5.3 Value of information versus information gain

The monitor also computes decision-aware value of information. Let C_direct(b) be the minimum expected cost of ACCEPT or REJECT under belief b. For a binary probe q,

GrossVOI(q) = C_direct(b) - [P(q=1) C_direct(b_q1) + P(q=0) C_direct(b_q0)].

NetVOI(q) = GrossVOI(q) - C_probe.

A probe is economically attractive when GrossVOI exceeds the investigation cost. This directly fixes the earlier investigation-threshold accounting problem: the decision compares the same quantity before and after acquisition and adds the probe cost exactly once.

At the prior with investigation cost 0.4, the direct state-aware cost is 2.000. The one-step expected costs after candidate probes are 1.194 for capability_issue, 1.565 for error_high, 1.622 for semantic_drift, 2.189 for latency_high, 2.227 for format_failure, and 2.367 for safety_shift. The corresponding gross value for capability_issue is 1.206, so the probe clears the 0.4 cost threshold.

### 5.4 Calibration metric

We measure Brier error for the probability of any non-STABLE state:

Brier = (1/N) sum_i (p_i - y_i)^2.

On the 20 held-out seeds, the joint evidence model has mean Brier error 0.1465 plus or minus 0.0060 for the binary comparator, compared with 0.1792 plus or minus 0.0041 for the legacy marginal model. The active two-step policy has Brier error 0.0275 plus or minus 0.0052 after final evidence acquisition. These scores support the probability-quality comparison inside the simulator, but lower Brier error does not itself imply optimal action cost or production calibration.

## 6. Evidence Acquisition

### 6.1 Probe set

Six probe types are available: semantic drift, formatting failure, safety shift, high latency, high API error, and a targeted capability issue probe. A probe is an additional measurement rather than a duplicate use of the initial observation.

The capability probe was introduced because failure analysis from the previous design exposed cases where aggregate quality remained healthy while a narrow capability was degraded. Its synthetic likelihood is 0.01 in STABLE, 0.95 in DEGRADED, 0.10 in TRANSIENT, and 0.20 in DISTRIBUTION_SHIFT.

### 6.2 Acquisition policies

The revised evaluation compares four acquisition mechanisms.

**Random-acquire** chooses one probe uniformly at random and always pays its cost.

**Always-acquire** always obtains the targeted capability probe and then acts.

**EIG one-step** chooses the probe with maximum expected entropy reduction, obtains one probe, then acts.

**VOI one-step** chooses the probe with minimum expected total decision cost over one remaining probe.

**VOI two-step**, the main policy, plans over at most two probes. It recursively compares the direct action with each admissible probe and evaluates the best downstream decision or second probe after each possible outcome.

The two-step policy is therefore a finite-horizon information-acquisition controller. It is not a full general POMDP solver, but it explicitly evaluates the second probe rather than leaving the second-round budget unused.

## 7. Decision Policy

### 7.1 Four-state cost model

The main policy no longer maps every non-DEGRADED state to the same cost. The hypothetical state-action costs are:

| State | ACCEPT | REJECT |
|---|---:|---:|
| STABLE | 0 | 3 |
| DEGRADED | 10 | 0 |
| TRANSIENT | 4 | 1 |
| DISTRIBUTION_SHIFT | 6 | 2 |

Investigation adds a probe cost of 0.4 in the locked test configuration.

The direct expected cost of action a is

C(a | b) = sum_s b(s) C(a,s).

The direct policy chooses the lower of ACCEPT and REJECT. This replaces the earlier DEGRADED-only rule as the main policy.

For comparison, the older binary threshold remains in the evaluation. With false-accept cost 10 and false-reject cost 3, its threshold is

10p = 3(1-p),

so p = 3/13 = 0.230769. That threshold is retained only as a comparator because it ignores explicit transient and distribution-shift costs.

### 7.2 Two-step lookahead

Let V_k(b) be the minimum expected cost with k probes remaining. Then

V_0(b) = min_a C(a | b).

For k > 0,

V_k(b) = min( V_0(b), min_q [ C_probe + P(q=1)V_{k-1}(b_q1) + P(q=0)V_{k-1}(b_q0) ] ).

The main active policy uses k = 2. The first probe is chosen only when the best acquisition branch has lower expected cost than the direct action. After the realized probe, the same recursion determines whether a second probe is worth taking.

This directly addresses the previous myopia criticism. A probe is not chosen merely because it is informative now. It is chosen because the immediate probe and its possible downstream acquisition decisions jointly reduce expected loss.

### 7.3 Stopping rule

The agent stops acquiring evidence when either no available probe has positive net decision value or the two-probe budget is exhausted. This is a cost-sensitive stop rule, not a fixed number of investigations.

## 8. Experimental Design

### 8.1 Synthetic data generator

Each evaluation case is assigned one of the four hidden states. The 50-case scenario contains 11 DEGRADED cases, 7 TRANSIENT cases, 5 DISTRIBUTION_SHIFT cases, and 27 STABLE cases. The 120-case generator repeats this state schedule cyclically while independently sampling observations.

Five task categories are used: math, code, instruction, safety, and knowledge.

The generator contains two deliberately difficult regimes. First, a narrow capability blind spot can occur during DEGRADED cases 16 through 20 in each 50-case cycle. Aggregate quality is forced to remain around 0.84 while semantic drift, formatting failure, latency, and error rate remain small. Second, a STABLE case at cycle position 30 receives noisy degraded-looking observations to test over-rejection.

The new version also adds a shared latent failure-pressure variable. This produces correlated evidence across channels, addressing a realism gap in the original generator.

### 8.2 Training, development, and test separation

The joint likelihood model is fitted on 6,000 synthetic training cases with seed 901. These cases are not reused as test cases.

Investigation cost is selected on development seeds 100 through 104. Candidate costs are 0.4, 0.6, 0.8, 1.0, and 1.2. Mean development decision costs are:

| Investigation cost | Mean development cost |
|---:|---:|
| 0.4 | 80.04 |
| 0.6 | 98.00 |
| 0.8 | 200.84 |
| 1.0 | 198.60 |
| 1.2 | 203.80 |

The selected cost is 0.4. It is selected without using the final 20 test seeds.

The held-out test set uses seeds 0 through 19, with 120 cases per seed, for 2,400 test cases total.

### 8.3 Baselines and metrics

The evaluation includes:

1. static quality threshold;
2. legacy binary naive-Bayes decision;
3. binary decision with the revised joint evidence model;
4. four-state direct expected-cost decision without acquisition;
5. random acquisition;
6. always-acquire;
7. one-step entropy-greedy acquisition;
8. one-step decision-aware VOI;
9. two-step decision-aware VOI.

Metrics are false ACCEPTs, false REJECTs, number of investigations, investigation rate, decision cost, event recall, event precision, and Brier error. Event recall treats any non-STABLE state as a detection target. State-specific interpretation is also retained because a single event metric can hide differences among DEGRADED, TRANSIENT, and DISTRIBUTION_SHIFT.

## 9. Results

### 9.1 Seed-7 diagnostic runs

The final evaluation is the 20-seed held-out study, but the single-seed runs remain useful for debugging. On the 50-case seed-7 diagnostic run, active two-step VOI made 1 false ACCEPT and 1 false REJECT, used 37 investigated cases and 38 total probe calls, and incurred cost 39.2. One-step VOI made 2 false ACCEPTs and 1 false REJECT, used 37 investigations and 37 probe calls, and cost 42.8. EIG cost 41.0 with 50 probe calls; always-acquire cost 61.0; and the static baseline cost 89.0 with 9 false ACCEPTs and 2 false REJECTs.

On the 120-case seed-7 diagnostic run, active two-step VOI made 1 false ACCEPT and 2 false REJECTs, used 90 investigated cases and 91 probe calls, and cost 80.4. One-step VOI cost 84.0 with 90 probe calls; EIG cost 92.0 with 120 probe calls; always-acquire cost 112.0; and the static baseline cost 225.0. These runs are diagnostic rather than the basis for the primary claim, which is the 20-seed held-out evaluation below.

### 9.3 Twenty-seed held-out evaluation

All results below use the locked investigation cost of 0.4. Values are mean plus or minus the 95 percent t confidence interval over 20 independent seeds. Intervals use the seed-level standard deviation with 19 degrees of freedom. “Investigations” counts cases that enter INVESTIGATE; “Probe calls” counts every acquired probe, including a second probe when the two-step policy uses one.

| Policy | Decision cost | False ACCEPT | False REJECT | Investigations | Probe calls | Recall | Precision |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 231.30 +/- 3.74 | 24.85 +/- 0.70 | 2.40 +/- 0.28 | 0.0 | 0.0 | 0.513 +/- 0.014 | 0.916 +/- 0.010 |
| Binary naive | 246.60 +/- 3.91 | 30.65 +/- 0.95 | 2.15 +/- 0.17 | 0.0 | 0.0 | 0.399 +/- 0.019 | 0.904 +/- 0.009 |
| Binary joint | 273.30 +/- 3.80 | 38.05 +/- 0.67 | 1.60 +/- 0.24 | 0.0 | 0.0 | 0.254 +/- 0.013 | 0.891 +/- 0.015 |
| State direct | 203.00 +/- 3.54 | 16.80 +/- 0.60 | 3.95 +/- 0.65 | 0.0 | 0.0 | 0.671 +/- 0.012 | 0.897 +/- 0.016 |
| Random acquire | 174.70 +/- 8.15 | 9.20 +/- 0.84 | 3.45 +/- 0.74 | 120.0 | 120.0 | 0.820 +/- 0.016 | 0.924 +/- 0.016 |
| Always acquire | 99.60 +/- 4.63 | 1.80 +/- 0.58 | 2.90 +/- 0.73 | 120.0 | 120.0 | 0.965 +/- 0.011 | 0.945 +/- 0.014 |
| EIG one-step | 92.75 +/- 3.83 | 1.70 +/- 0.63 | 0.95 +/- 0.47 | 120.0 | 120.0 | 0.967 +/- 0.012 | 0.981 +/- 0.009 |
| VOI one-step | 84.92 +/- 3.97 | 1.95 +/- 0.62 | 2.70 +/- 0.59 | 84.05 +/- 1.14 | 84.05 +/- 1.14 | 0.962 +/- 0.012 | 0.948 +/- 0.011 |
| VOI two-step | 81.51 +/- 3.70 | 1.65 +/- 0.55 | 1.95 +/- 0.51 | 84.10 +/- 1.14 | 84.90 +/- 1.23 | 0.968 +/- 0.011 | 0.962 +/- 0.010 |

Three comparisons are especially relevant. First, two-step planning reduces mean cost by 4.0 percent relative to one-step decision-aware VOI while using only 0.85 additional probe calls per 120 cases on average. Second, it reduces cost by 12.1 percent relative to EIG acquisition while using 29.3 percent fewer probe calls than both EIG and always-acquire. Third, it reduces mean decision cost by 64.8 percent relative to the static threshold baseline. Because the same test seeds are used for every policy, paired seed-level cost differences are also informative. Two-step VOI is lower than one-step VOI by 3.41 cost units on average, with a 95 percent paired t interval of plus or minus 3.14. The corresponding paired differences are 11.24 plus or minus 4.02 versus EIG, 18.09 plus or minus 2.58 versus always-acquire, and 149.79 plus or minus 4.32 versus the static baseline.

### 9.4 Calibration and correlated evidence

The 20-seed Brier results are:

| Model | Brier error |
|---|---:|
| Legacy marginal naive Bayes | 0.1792 +/- 0.0041 |
| Revised joint evidence model | 0.1465 +/- 0.0060 |
| Active two-step final belief | 0.0275 +/- 0.0052 |
| EIG one-step final belief | 0.0219 +/- 0.0046 |

The joint model improves the non-STABLE probability score relative to the legacy marginal model. The even lower scores after acquisition show the benefit of additional evidence inside the synthetic model, but they should not be read as external calibration because the training and test distributions are generated by the same simulator family.

### 9.5 Investigation-cost sensitivity

The cost sensitivity run on the 50-case seed-7 benchmark shows a sharp regime change:

| Investigation cost | Investigations | Rate | False ACCEPT | False REJECT | Decision cost | Recall | Precision |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.4 | 37 | 0.74 | 1 | 1 | 39.2 | 0.957 | 0.957 |
| 0.6 | 36 | 0.72 | 1 | 2 | 48.6 | 0.957 | 0.917 |
| 0.8 | 6 | 0.12 | 7 | 2 | 85.8 | 0.696 | 0.889 |
| 1.0 | 5 | 0.10 | 7 | 2 | 86.0 | 0.696 | 0.889 |
| 1.2 | 5 | 0.10 | 7 | 2 | 87.0 | 0.696 | 0.889 |
| 1.5 | 0 | 0.00 | 7 | 3 | 84.0 | 0.696 | 0.842 |
| 2.0 | 0 | 0.00 | 7 | 3 | 84.0 | 0.696 | 0.842 |

This is why the revised protocol selects the investigation cost on a development split. In the development study, mean cost is 80.04 at 0.4, 98.00 at 0.6, 200.84 at 0.8, 201.80 at 1.0, and 202.76 at 1.2. The final test seeds are not used for this selection. The paper does not claim that 0.4 is a universally correct real-world cost. Rather, the sensitivity result shows that acquisition cost is a genuine policy parameter and that a deployment would need measured operational acquisition costs.

## 10. Failure Analysis

The revised 120-case seed-7 run still contains meaningful failures. The examples below are selected from the regenerated run rather than copied from the earlier prototype.

| Scope | Example | Failure class | Evidence or mechanism | Consequence |
|---|---|---|---|---|
| Case | case-037, seed 7 | DISTRIBUTION_SHIFT under-detection | Quality 0.714 and semantic drift 0.281; capability probe negative | ACCEPT, true cost 6.4 |
| Case | case-027, seed 7 | Correlated-evidence false REJECT | STABLE case with semantic drift 0.399 despite quality 0.900 | REJECT, cost 3.0 |
| Case | case-003, seed 7 | Additional acquisition on a stable case | Two-step path acquires semantic_drift then capability_issue | ACCEPT, probe cost 0.8 |
| Case | case-078, seed 7 | Second stable false REJECT | STABLE case with semantic drift 0.307 despite quality 0.961 | REJECT, cost 3.0 |
| Policy | Development/test sweep | Investigation-cost cliff | Raising cost from 0.6 to 0.8 cuts investigations from 36 to 6 on seed 7 | Cost rises from 48.6 to 85.8 |

The first failure shows that distribution shift remains the main blind spot. The second and fourth show that evidence can be sufficiently misleading to trigger false rejection even after joint modeling. The third shows the cost of a second probe: finite-horizon planning is not free, and a policy can rationally acquire additional information even when the hidden state is ultimately stable. The fifth demonstrates why acquisition cost must be measured rather than chosen for presentation quality.

### 10.1 State-level behavior

On the regenerated 120-case seed-7 active run, the benchmark contains 69 STABLE, 27 DEGRADED, 14 TRANSIENT, and 10 DISTRIBUTION_SHIFT cases. The active policy rejects all 27 DEGRADED and all 14 TRANSIENT cases, rejects 9 of 10 DISTRIBUTION_SHIFT cases, and falsely rejects 2 of 69 STABLE cases. The remaining accepted non-STABLE case is a distribution shift. Event recall is therefore 50/51 = 0.980 and event precision is 50/52 = 0.962.

This state breakdown illustrates why binary recall alone is insufficient. The monitor is highly effective on persistent degradation and transient anomalies in this synthetic benchmark but remains vulnerable to distribution shifts whose observable signature resembles STABLE behavior.

## 11. Discussion

The revision addresses the reviewer concerns in three measurable ways and also exposes what remains unresolved.

First, evidence dependence matters. The simulator contains measurable cross-channel correlation, and the joint likelihood model lowers the 20-seed Brier error from 0.1792 to 0.1465 relative to the marginal model. This does not prove that the joint model is correct outside the simulator. It does demonstrate that multiplying marginal evidence likelihoods without checking dependence is a testable modeling assumption rather than a neutral default.

Second, acquisition strategy matters. EIG is effective but acquires all 120 cases. One-step VOI reduces acquisition while two-step VOI lowers mean decision cost from 84.92 to 81.51. The two-step policy uses 84.9 probe calls per 120 cases, only 0.85 more than one-step VOI, and approximately 29.3 percent fewer calls than always-acquire. The benefit is therefore not explained by simply acquiring many more probes.

Third, the decision objective matters. The binary policies price only DEGRADED versus not-DEGRADED and perform substantially worse in decision cost. The state-aware policy explicitly prices TRANSIENT and DISTRIBUTION_SHIFT. This makes the mapping from latent states to operational consequences inspectable and avoids treating all non-DEGRADED states as equivalent.

The revised design is directly related to active feature acquisition and acquisition-POMDP work, which formalize the trade-off between the information value of a measurement and its acquisition cost. It is also complementary to change-point detection: the present monitor decides what to do with a case after evidence is observed, whereas sequence-level change-point methods detect when a stream has changed. A future version should combine these layers rather than treating DISTRIBUTION_SHIFT as an isolated case label.

## 12. Limitations and Knowledge Gaps

Several limitations remain unresolved.

**Synthetic evidence and priors.** All priors, conditional observation mechanisms, and state costs are synthetic. They are useful for controlled evaluation but cannot establish production reliability.

**Human labels and evaluator reliability.** The benchmark has programmatic state labels. It does not include human-reviewed LLM outputs, inter-rater disagreement, judge calibration, or label drift. Work on evaluator reliability and checklist-based judging motivates these concerns, but the present benchmark does not measure them.

**Sequential probe dependence.** The six initial channels use a full joint distribution, but repeated probes remain conditionally independent given state. A future model should learn joint distributions over probe sequences or explicitly represent temporal dynamics.

**Probe latency and monetary cost.** Investigation cost is normalized. We do not currently measure API latency, human review time, or monetary spend for individual probes. The 0.4 value is selected from a development split and should not be interpreted as an empirical currency value.

**Real drift and change points.** DISTRIBUTION_SHIFT is a generated state, not a production change point detector. Classical change-point methods remain relevant for sequence-level monitoring [5]. The current work treats a case as the unit of decision and does not infer change-point boundaries over a long stream.

**Learned acquisition policies.** The paper compares transparent random, always-acquire, EIG, one-step VOI, and two-step VOI strategies. It does not implement a reinforcement-learning acquisition policy. A learned policy trained only on this simulator could simply learn simulator artifacts, so adding it without real traces would not resolve the external-validity problem.

**Cost cliff.** The sensitivity table shows that a hypothetical investigation cost near 0.8 sharply changes behavior. This is not hidden. It is evidence that cost calibration is itself a major design requirement.

**Production governance.** The monitor is not an autonomous incident commander. High-impact operational actions should remain subject to human review and deployment-specific policy.

## 13. Conclusion

This paper revises an LLM monitoring prototype into a more internally consistent active sensing system. The revised monitor models correlated initial evidence jointly, prices all four hidden states explicitly, and performs two-step decision-aware information acquisition without reusing a probe within one decision episode. Investigation cost is selected on a development split and evaluated on 20 held-out seeds.

On the regenerated synthetic benchmark, the two-step policy achieves mean decision cost 81.51 compared with 84.92 for one-step VOI, 92.75 for EIG, and 99.60 for always-acquire. It uses 84.9 probe calls per 120 cases rather than 120 for the always-acquire policy. Event recall is 0.968 and event precision is 0.962. These results support the narrower claim that finite-horizon cost-sensitive acquisition can improve action cost in a controlled synthetic setting.

They do not support a production deployment claim. The next decisive experiment is a held-out replay study using real or publicly released LLM monitoring traces, human-reviewed labels, measured probe time and monetary cost, and a temporal model for sequential drift. The current paper should therefore be read as a reproducible probabilistic decision framework and controlled failure analysis, not as evidence that a monitoring agent is ready to operate without human oversight.

## AI-use statement

OpenAI ChatGPT was used as a research and engineering assistant for the probabilistic audit, derivation checks, code changes for the joint evidence model, four-state cost matrix, two-step VOI policy, failure classification, related-work search, and manuscript editing. The executable checks were independently verified against the project: Bayesian normalization, 1.291-bit prior entropy, 0.808-bit worked-posterior entropy, the 3/13 binary threshold, the seven-test suite, the 50-case and 120-case seed-7 runs, the five-seed investigation-cost development sweep, the 20-seed test, and the sensitivity grid. The final 20-seed evaluation used test seeds 0 through 19 after selecting cost 0.4 on development seeds 100 through 104. Synthetic priors, costs, likelihood assumptions, state definitions, failure interpretation, and final claims remain subject to human review; model output was treated as analysis and drafting assistance rather than experimental ground truth.

## References

[1] Lingjiao Chen, Matei Zaharia, and James Zou. How is ChatGPT's behavior changing over time? arXiv:2307.09009, 2023.

[2] Mikko Lauri, David Hsu, and Joni Pajarinen. Partially Observable Markov Decision Processes in Robotics: A Survey. IEEE Transactions on Robotics, 2022.

[3] Arman Rahbar, Linus Aronsson, and Morteza Haghir Chehreghani. A Survey on Active Feature Acquisition Strategies. arXiv:2502.11067, 2025.

[4] Yang Li and Junier Oliva. Towards Cost Sensitive Decision Making. Proceedings of The 28th International Conference on Artificial Intelligence and Statistics, PMLR 258:3601-3609, 2025.

[5] Charles Truong, Laurent Oudre, and Nicolas Vayatis. Selective review of offline change point detection methods. Signal Processing, 167:107299, 2020.

[6] Claude E. Shannon. A Mathematical Theory of Communication. Bell System Technical Journal, 27(3):379-423 and 27(4):623-656, 1948.

[7] Xiyan Fu and Wei Liu. How Reliable is Multilingual LLM-as-a-Judge? Findings of ACL 2025, 2025.

[8] Yukyung Lee, JoongHoon Kim, Jaehee Kim, Hyowon Cho, Jaewook Kang, Pilsung Kang, and Najoung Kim. CheckEval: A reliable LLM-as-a-Judge framework for evaluating text generation using checklists. Proceedings of EMNLP 2025, pages 15771-15798, 2025.
