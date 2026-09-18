#Review Record

## Purpose

This file records three distinct reviews of the black-box LLM monitoring agent:

1. **Practitioner review** — deployment realism, stakeholders, operational risk, and human-control boundaries.
2. **Probability review** — hidden states, priors, likelihoods, thresholds, costs, and calibration.
3. **Preprint review** — problem clarity, methodology, reproducibility, claims, limitations, ethics, and evidence.

AI review comments are treated as **review input, not ground truth**. Each comment is independently accepted or rejected, with a concrete reason and an evidence/change field.

---

## 1. Practitioner Review

**Review target:** `src/agent.py`, `src/model.py`, `results/REPORT.md`, `results/five_failure_cases.csv`, and the Week 1 project objective.

| AI review comment | Accept / Reject | Reason | Change | Evidence |
|---|---|---|---|---|
| The four hidden states (`STABLE`, `DEGRADED`, `TRANSIENT`, `DISTRIBUTION_SHIFT`) are a useful minimum simulation taxonomy, but they should not yet be treated as sufficient for deployment. Provider-side updates, prompt/configuration changes, evaluator failure, and tool/runtime changes may need separate treatment. | **Accept** | The project explicitly models incomplete state information, and the current four-state model is intentionally small. Treating it as deployment-complete would overclaim. | Keep four states for Week 1; add deployment taxonomy as a limitation and future experiment. | `src/model.py`; project research file; Week 1 hidden-state requirements. |
| The agent currently observes quality, semantic drift, formatting, safety, latency, error rate, and feedback rate, but `feedback_rate` is not used in the evidence update. | **Accept** | An observed input that does not affect belief updating is currently dead information. | Either implement feedback evidence or remove it from the Week 1 observation interface. Prefer implementing it in the next iteration. | `src/agent.py`: `feedback_rate` exists but is absent from `Observation.evidence()`. |
| The investigation action is useful because the agent can collect an independent probe before committing to `ACCEPT` or `REJECT`. | **Accept** | This directly satisfies the Week 1 requirement for an actionable agent that can obtain more evidence. | Preserve bounded investigation and explicitly document the probe as an independent evidence source. | `src/model.py`; `src/evaluate.py`; active-policy results. |
| A real deployment should not let the monitoring agent autonomously command incidents, rollback models, or make irreversible operational changes. | **Accept** | The current evidence is external and incomplete; human incident context may be unavailable to the agent. | Keep `ACCEPT / INVESTIGATE / REJECT` as a monitoring gate and escalate high-impact cases to a human. | `decisions/probability-decision-record.md` human-control boundary. |
| Investigation cost should include more than a fixed compute value; latency, provider/API cost, operational attention, and user impact may matter. | **Accept** | `0.8` is an explicit simulation parameter, not a production estimate. | Treat the current cost as synthetic and plan a sensitivity/production-trace study before deployment claims. | `src/model.py` `Costs`; `results/REPORT.md` limitation. |
| The current failure analysis shows that high-quality aggregate output can hide degraded cases. | **Accept** | Several active-policy failures are `DEGRADED` cases accepted despite quality values above the low-quality threshold. | Add targeted probes for high-risk subgroups instead of relying on aggregate quality alone. | `results/five_failure_cases.csv`: cases 017–020. |
| The agent should remember previous incidents and compare new cases with similar failures. | **Reject for Week 1 / Future work** | Memory is part of the research direction, but adding retrieval or case-based reasoning now would expand the experiment beyond the smallest testable version. | Keep `memory` as a recorded observation history; evaluate incident retrieval as a separate ablation later. | `src/agent.py` contains `self.memory`; no retrieval policy is currently defined. |

### Practitioner review conclusion

**Accepted design direction:** bounded investigation, explicit human escalation, targeted evidence collection, and a small hidden-state model.

**Main practitioner risk:** the current simulator is appropriate for a controlled Week 1 experiment but does not establish that the same state taxonomy, probe costs, or escalation policy is operationally valid.

---

## 2. Probability Review

**Review target:** `src/model.py` and `decisions/probability-decision-record.md`.

| AI review comment | Accept / Reject | Reason | Change | Evidence |
|---|---|---|---|---|
| The prior probabilities sum to 100%, which satisfies the basic probability-record requirement. | **Accept** | The record explicitly gives 72%, 12%, 8%, and 8%. | Keep the prior and record it as a simulation prior, not an empirical deployment prior. | `decisions/probability-decision-record.md`. |
| The likelihood table is not empirically calibrated and should not be described as measured probabilities. | **Accept** | The code comments explicitly describe the values as inspectable hypotheses calibrated by simulation. | Add a prominent calibration limitation to the probability record and preprint. | `src/model.py`; `decisions/probability-decision-record.md`. |
| The model multiplies likelihoods for multiple evidence signals as if they are conditionally independent. | **Accept** | This is a strong modeling assumption. Signals such as quality and semantic drift can be correlated. | State conditional-independence as a limitation and add a future correlated-evidence sensitivity/ablation test. | `BeliefState.update()` in `src/model.py`. |
| A generic probability threshold such as 0.5 should determine `ACCEPT` or `REJECT`. | **Reject** | Week 1 explicitly asks for cost-sensitive decisions. A 0.5 threshold ignores asymmetric false-accept and false-reject costs. | Keep expected-cost comparison as the primary binary decision rule. | `MonitorPolicy.immediate_risk_costs()`; `Costs(false_accept=12, false_reject=5)`. |
| The `reject_threshold` and `accept_threshold` parameters are not actually used in the current decision methods. | **Accept** | The policy constructor exposes thresholds, but `decide_binary()` and `decide_active()` currently use expected cost instead. This creates misleading configuration. | Remove unused thresholds or implement them consistently. Prefer removing them for the current cost-based policy. | `src/model.py`: constructor versus `decide_binary()` / `decide_active()`. |
| The value-of-information calculation is conceptually appropriate for deciding whether another probe is worth its cost. | **Accept with qualification** | The implementation compares expected post-probe decision cost plus investigation cost with current decision cost. This is a reasonable one-step simulation mechanism. | Keep VOI, but label it as a one-step synthetic estimator and validate it with ablation experiments. | `MonitorPolicy.investigation_value()`; active-policy results. |
| The current probability model proves that the active policy is better than the baseline. | **Reject** | One 50-case synthetic run cannot establish general superiority or production validity. | Use hypothesis-generating language and add repeated seeds, sensitivity analysis, and confidence intervals. | `results/REPORT.md`: explicitly calls the result hypothesis-generating. |
| The model should include evaluator uncertainty because an external LLM judge can itself be wrong. | **Accept** | The research base identifies judge reliability as a separate uncertainty source. | Add evaluator error as a future hidden variable or explicitly model noisy quality measurements. | Research material on LLM-as-a-Judge reliability; current `Observation` model. |

### Probability review conclusion

The current model is suitable as an **inspectable Week 1 simulation**, not as a calibrated probabilistic model. The highest-priority next change is to validate priors/likelihoods and remove or implement the currently unused threshold parameters.

---

## 3. Preprint Review

**Review target:** Week 1 experiment outputs, project claims, reproducibility, limitations, and paper structure.

| AI review comment | Accept / Reject | Reason | Change | Evidence |
|---|---|---|---|---|
| The problem statement is specific enough: monitor externally observable LLM behavior when the true deployment state is hidden and select `ACCEPT`, `INVESTIGATE`, or `REJECT`. | **Accept** | It identifies the input, action space, and hidden-state problem required by Week 1. | Use this formulation consistently throughout the preprint. | `README.md`; `research-file.md`; `src/agent.py`. |
| The experiment meets the basic Week 1 test-size requirement. | **Accept** | The experiment uses 50 cases, within the required 30–50 range. | Report the exact case count and evaluation protocol. | `results/summary.json`; `results/*.csv`. |
| Comparing only against the baseline is insufficient because the project already contains both a binary and active policy. | **Reject** | The current experiment actually compares three policies: baseline, binary, and active. | Present all three clearly in the paper. | `results/REPORT.md`; `src/evaluate.py`. |
| The active policy result should be reported as evidence of deployment superiority. | **Reject** | The data are synthetic and the experiment is a single Week 1 run. | Describe the result as preliminary and hypothesis-generating. | `results/REPORT.md`. |
| The result table should include false accepts, false rejects, investigation rate, decision cost, recall, and precision. | **Accept** | These metrics expose the trade-off created by the third action and asymmetric costs. | Retain the full policy table in the preprint. | `results/REPORT.md`. |
| The paper should analyze at least five incorrect decisions and name the failure modes. | **Accept** | This is an explicit Week 1 requirement and the repository already contains five failure cases. | Include the five failure cases and explain why each error occurred. | `results/five_failure_cases.csv`. |
| The active policy appears to reduce cost mainly because the investigation mechanism can resolve some uncertain cases, but the experiment does not isolate the causal contribution of VOI from other policy differences. | **Accept** | The current experiment is not an ablation study. | Add a future ablation: binary policy vs active policy with random probe selection vs active policy with VOI probe selection. | `src/model.py`; `src/evaluate.py`; `results/REPORT.md`. |
| The paper should distinguish behavioral drift from the cause of drift. | **Accept** | Output changes can result from provider updates, prompts, context, distribution shift, tools, or evaluator noise. | State that observed behavioral change is evidence of a change in behavior, not proof of a specific provider-side update. | `research-file.md`; drift references. |
| The preprint should state that the hidden state is unavailable at decision time and only used for evaluation. | **Accept** | Otherwise the simulation could be mistaken for a classifier with access to ground truth. | Explicitly separate agent observations from simulator labels. | `src/evaluate.py`; `decisions/probability-decision-record.md`. |
| The current project should claim calibrated uncertainty. | **Reject** | The likelihoods are hand-specified simulation hypotheses and no reliability analysis is reported. | Use terms such as “belief state,” “synthetic probabilities,” and “uncalibrated likelihood assumptions.” | `src/model.py`; probability decision record. |
| The paper needs explicit ethics and human-control limitations. | **Accept** | Autonomous rejection or escalation based on an imperfect monitor can create operational harm. | Include human review for high-impact cases and describe irreversible-action boundaries. | `decisions/probability-decision-record.md`. |
| The experiment should be described as reproducible only if the exact data-generation procedure, dependencies, commands, and policy versions are recorded. | **Accept** | Reproducibility requires more than publishing a result table. | Add a README test command, dependency versions, seed information, and artifact/version metadata. | `pyproject.toml`, `requirements.txt`, `results/`, probability record. |

### Preprint review conclusion

The paper can make a defensible **methodological claim** about constructing and testing a cost-sensitive active monitoring policy, but it should not make a deployment-performance or calibration claim from the current synthetic experiment.

---

## 4. Cross-Review Changes

The three reviews converge on the following changes:

### Required before treating Week 1 as complete

- [x] Keep `ACCEPT / INVESTIGATE / REJECT` as the explicit action space.
- [x] Keep a hidden-state belief representation.
- [x] Compare an active policy against simpler policies.
- [x] Include asymmetric decision costs.
- [x] Include at least 30 test cases; current run uses 50.
- [x] Analyze at least five incorrect decisions.
- [x] Create a probability decision record.
- [x] Maintain an explicit human-control boundary.
- [x] Clearly separate synthetic results from production evidence.
- [x] Remove or implement unused `accept_threshold` / `reject_threshold` parameters.
- [ ] Decide whether `feedback_rate` is a real evidence signal or should be removed.

### Next experiment

1. **Calibration study:** replace or fit synthetic likelihoods using labeled replay data.
2. **Sensitivity study:** vary false-accept cost, false-reject cost, and investigation cost.
3. **VOI ablation:** compare VOI probe selection against random probe selection.
4. **Correlated evidence test:** evaluate the conditional-independence assumption.
5. **Repeated runs:** use multiple random seeds and report uncertainty around policy metrics.
6. **Targeted failures:** add cases where aggregate quality remains high while a narrow capability or safety property degrades.

---

## 5. Important AI-Review Errors to Avoid

The following review claims must **not** be treated as established facts without evidence:

- Four hidden states are sufficient for real deployment.
- The chosen priors represent real-world frequencies.
- The likelihood table is calibrated.
- The active policy will outperform simpler policies in production.
- The investigation cost of `0.8` represents a real operational cost.
- Observed behavioral drift proves a provider-side model update.
- An LLM evaluator can be treated as ground truth.

These are assumptions or hypotheses requiring evidence, controlled experiments, or production data.

---

## 6. Final Review Decision

**Overall status: CONDITIONAL ACCEPT**

The Week 1 design satisfies the core structure of an agent operating under incomplete information and has a reproducible synthetic comparison between baseline, binary, and active policies.

The work should **not** yet claim calibrated uncertainty, production readiness, or general superiority of the active policy. The strongest next step is to validate the probability model and investigate the failure mode where degraded cases retain apparently good aggregate quality.

**Evidence reviewed:**

- `src/agent.py`
- `src/model.py`
- `src/evaluate.py`
- `results/REPORT.md`
- `results/summary.json`
- `results/five_failure_cases.csv`
- `decisions/probability-decision-record.md`
- Week 1 project requirements
