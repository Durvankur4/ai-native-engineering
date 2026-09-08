# Week 1 Project File

## 1. Project identity

**Project focus:** Active monitoring of black-box LLM behavior under non-stationary deployment conditions.

**Experience level:** Beginner in this project area.

**Project objective:** Design and test an agent that observes an external LLM, maintains a belief about whether its behavior remains acceptable, and chooses `ACCEPT`, `INVESTIGATE`, or `REJECT` when the true system state cannot be observed directly.

**Problem statement:**

> The agent observes external LLM inputs, outputs, evaluation signals, and runtime evidence. It must select `ACCEPT`, `INVESTIGATE`, or `REJECT` because the actual model state, provider-side updates, and true production quality are not directly visible.

## 2. Project scope

### Observable inputs

- Prompt and response pairs from fixed or sampled probes
- Output quality and task-level evaluation scores
- Semantic or structural differences from a trusted baseline
- Formatting, refusal, safety, and instruction-following changes
- Latency, token usage, and error signals
- User feedback and delayed failure reports
- Model/API metadata that is externally exposed
- Results from additional probe queries after an `INVESTIGATE` action

### Hidden state

- Silent provider-side model update
- True model capability degradation
- Prompt or context sensitivity that is not captured by the probe set
- Distribution shift in incoming requests
- Provider policy or safety behavior changes
- Measurement error in external evaluators
- A transient anomaly rather than persistent degradation

### Human-only or partially hidden information

A human may have deployment context, incident history, business impact, domain knowledge, or provider communication that is unavailable to the monitoring agent. The project therefore treats external observations as incomplete evidence rather than ground truth.

### Actions

| Action | Meaning | Main purpose |
|---|---|---|
| `ACCEPT` | Continue normal operation | Low intervention when evidence supports stability |
| `INVESTIGATE` | Collect more evidence | Resolve uncertainty before taking a stronger action |
| `REJECT` | Block, quarantine, or escalate the case | Protect the system when risk is sufficiently high |

### Error costs

The initial cost ordering is:

`False ACCEPT > False REJECT > Unnecessary INVESTIGATE`

A false accept can allow degraded or unsafe behavior to reach users. A false reject creates operational friction, while investigation consumes time and compute but can reduce both major error types. These relative costs must be validated before final evaluation.

## 3. Technical terms to understand

- LLM behavioral drift
- Model drift
- Non-stationarity
- Black-box model monitoring
- LLM observability
- Online evaluation
- Offline evaluation
- Regression testing
- Semantic output drift
- Distribution shift
- Partial observability
- POMDP
- Belief state
- Bayesian updating
- Active sensing
- Value of information
- Selective prediction
- Abstention
- Conformal prediction
- Calibration
- LLM-as-a-Judge
- Agent-as-a-Judge
- Guardrails
- Decision threshold
- False positive and false negative
- Human-in-the-loop
- Production trace

## 4. Search queries

1. `LLM behavioral drift over time black box model monitoring`
2. `silent LLM provider updates regression detection`
3. `LLM observability production evaluation drift`
4. `black box LLM uncertainty estimation`
5. `POMDP active sensing uncertainty decision making`
6. `belief state monitoring under partial observability`
7. `selective prediction abstention high uncertainty`
8. `conformal prediction black box uncertainty calibration`
9. `LLM as a judge reliability limitations`
10. `agent evaluation intermediate trajectory observability`
11. `LLM regression testing production model updates`
12. `human escalation threshold AI monitoring`

## 5. Verified Reddit communities

| Community | Why it is relevant | Verification |
|---|---|---|
| [r/MachineLearning](https://www.reddit.com/r/MachineLearning/) | Strong fit for model evaluation, robustness, benchmarks, uncertainty, and experimental design. Recent posts include work on model evaluation and drift-related system design. | Active community page checked Sept. 2026 |
| [r/mlops](https://www.reddit.com/r/mlops/) | Directly relevant to production monitoring, model lifecycle, deployment, observability, drift, and operational failure modes. | Active community page checked Sept. 2026 |
| [r/LLMDevs](https://www.reddit.com/r/LLMDevs/) | Focused on building and operating LLM systems, with current discussions on observability, evaluations, testing, and production behavior. | Active recent discussions verified in 2026 |
| [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/) | Useful for model comparison, behavior changes, evaluation practice, inference behavior, and failure reports from hands-on users. | Active community page and recent posts verified in 2026 |
| [r/LanguageTechnology](https://www.reddit.com/r/LanguageTechnology/) | Relevant to NLP evaluation, language model behavior, benchmarks, and technical discussion of language systems. | Active community page checked Sept. 2026 |

**Discussion topics to ask about:**

- Which hidden state is missing from the monitoring model?
- Which incorrect decision has the highest operational cost?
- When should the agent investigate instead of making a binary decision?
- Which external signals are reliable indicators of persistent degradation?
- How should delayed ground truth be incorporated?
- Which evaluation failures are caused by the judge rather than the target model?
- What evidence would justify changing the action threshold?

## 6. Relevant X accounts

These accounts are useful because they cover LLM evaluation, production AI systems, agent engineering, model behavior, and observability.

| Account | Why to follow |
|---|---|
| [@sh_reya](https://x.com/sh_reya) | LLM evaluation, eval design, test-time optimization, and practical evaluation methodology. |
| [@hwchase17](https://x.com/hwchase17) | Agent systems, evaluations, production tooling, and LangChain/LangSmith ecosystem. |
| [@RLanceMartin](https://x.com/RLanceMartin) | Agent engineering, LLM application architecture, and production agent infrastructure. |
| [@simonw](https://x.com/simonw) | Practical LLM systems, model/API behavior, experimentation, and real-world software usage. |
| [@HamelHusain](https://x.com/HamelHusain) | AI engineering, agent workflows, evaluation practice, and implementation experience. |
| [@chipro](https://x.com/chipro) | Machine learning systems, deployment, and practical engineering tradeoffs. |
| [@jxnlco](https://x.com/jxnlco) | LLM application engineering, structured outputs, evaluation, and agent development. |
| [@rasbt](https://x.com/rasbt) | LLM systems and model experimentation with a strong engineering perspective. |
| [@wandb](https://x.com/wandb) | ML/LLM experiment tracking, evaluation, and production workflows. |
| [@LangChainAI](https://x.com/LangChainAI) | Agent deployment, observability, evaluation, and production use cases. |
| [@ArizePhoenix](https://x.com/ArizePhoenix) | AI observability, tracing, evaluation, and troubleshooting. |

## 7. Core material and references

### 7.1 Behavioral drift

**Chen, Zaharia, Zou. "How is ChatGPT's behavior changing over time?"**

Why it matters: establishes that the externally observed behavior of hosted LLM services can change over time even when the service appears to be the same model family. This is a direct motivation for continuous external monitoring.

https://arxiv.org/abs/2307.09009

### 7.2 Update governance and compatibility

**Chishti, Oyinloye, Li. "Test Before You Deploy: Governing Updates in the LLM Supply Chain"**

Why it matters: directly addresses silent provider-side updates, behavioral drift, risk-focused testing, compatibility gates, and the difficulty of detecting changes when the provider exposes limited internals.

https://arxiv.org/abs/2604.27789

### 7.3 Observability and production evaluation

**LangChain. "LLM observability & monitoring: how to evaluate agent behavior"**

Why it matters: separates infrastructure monitoring from behavior-level observability and emphasizes traces, online evaluation, human review, and converting production failures into repeatable tests.

https://www.langchain.com/resources/llm-monitoring-observability

### 7.4 Agent evaluation

**Zhuge et al. "Agent-as-a-Judge: Evaluate Agents with Agents." ICML 2025.**

Why it matters: evaluates agent trajectories rather than relying only on final outputs. This supports the idea that an `INVESTIGATE` action can inspect intermediate evidence.

https://proceedings.mlr.press/v267/zhuge25a.html

### 7.5 Judge reliability

**Fu and Liu. "How Reliable is Multilingual LLM-as-a-Judge?" Findings of EMNLP 2025.**

Why it matters: shows that automated judges can be inconsistent, so an external evaluator must not automatically be treated as ground truth. This is important when the monitoring agent depends on another model for evidence.

https://aclanthology.org/2025.findings-emnlp.587/

### 7.6 Practical agent evaluation

**AWS. "Evaluate Amazon Bedrock Agents with Ragas and LLM-as-a-judge."**

Why it matters: provides a concrete production-style evaluation workflow using traces, ground-truth datasets, trajectory evaluation, Ragas, and LLM-based judging.

https://aws.amazon.com/blogs/machine-learning/evaluate-amazon-bedrock-agents-with-ragas-and-llm-as-a-judge/

### 7.7 Partial observability

**Lauri, Hsu, Pajarinen. "Partially Observable Markov Decision Processes in Robotics: A Survey."**

Why it matters: provides the formal framework for decisions when the true state is hidden and observations are noisy or incomplete. The same structure maps naturally to the monitoring problem.

https://arxiv.org/abs/2209.10342

### 7.8 Selective prediction and abstention

**Feng et al. "Selective prediction-set models with coverage guarantees."**

Why it matters: supports the idea that a system can abstain when uncertainty is high instead of forcing a hard decision. This is conceptually useful for the `INVESTIGATE` action.

https://arxiv.org/abs/1906.05473

### 7.9 Conformal uncertainty

**Karimi and Samavi. "Quantifying Deep Learning Model Uncertainty in Conformal Prediction."**

Why it matters: useful background for turning predictive uncertainty into a more structured decision signal and for thinking about calibration.

https://arxiv.org/abs/2306.00876

## 8. Useful software and datasets

| Resource | Use in the project |
|---|---|
| [Langfuse](https://github.com/langfuse/langfuse) | Open-source tracing, metrics, evaluation, prompt tracking, and production LLM observability. |
| [Arize Phoenix](https://github.com/Arize-ai/phoenix) | Open-source tracing, evaluation, datasets, experiments, and AI observability. |
| [Ragas](https://github.com/explodinggradients/ragas) | Evaluation of LLM and RAG application behavior. Useful for constructing task-level quality signals. |
| Golden prompt sets | Stable probe inputs for detecting behavior changes over time. Build a small version specific to this project. |
| Production trace samples | Candidate source of delayed labels, failure cases, and investigation triggers. Use only data that can be shared safely. |

## 9. Questions the project must answer

### Hidden state

- What exact hidden states are important enough to distinguish?
- Can "degraded", "stable", and "transient anomaly" explain the observed behavior?
- Is provider-side model identity part of the hidden state if the API does not expose it reliably?

### Evidence

- Which observations are strongest indicators of real degradation?
- How many independent probes are needed before an investigation becomes credible?
- How should delayed user feedback update the belief state?
- How can evaluator error be separated from target-model error?

### Actions

- What should trigger `INVESTIGATE`?
- What evidence is sufficient for `REJECT`?
- When is `ACCEPT` justified even when uncertainty is non-zero?
- How much extra evidence is worth collecting before acting?

### Errors and cost

- Is false acceptance always more costly than false rejection for the chosen deployment scenario?
- What is the cost of repeated unnecessary investigation?
- Can action costs be estimated from realistic operational consequences rather than arbitrary numbers?

### Learning and memory

- Which past incidents should the agent remember?
- How should the agent compare a new case with previous failures?
- What information becomes stale after a model or prompt update?

## 10. Initial project hypothesis

> An active three-action monitoring policy that can spend effort on additional evidence will make better cost-sensitive decisions under incomplete state information than a simple `ACCEPT/REJECT` policy, especially when model behavior can change silently and the cost of false acceptance is high.

This is a hypothesis to test, not a confirmed result.

## 11. Planned comparison

### Policy A: Binary policy

`ACCEPT` when the monitored quality signal is above a fixed threshold, otherwise `REJECT`.

### Policy B: Active policy

`ACCEPT` when confidence is sufficiently high, `REJECT` when risk is sufficiently high, and `INVESTIGATE` when additional evidence has enough expected value to justify another observation.

### Baseline

A static threshold rule based on the same observable score without belief updates or active investigation.

### Candidate metrics

- False accept count
- False reject count
- Investigation rate
- Decision cost
- Precision and recall for degradation detection
- Calibration of risk estimates
- Average number of additional probes per investigation
- Detection delay after a simulated drift event

## 12. AI prompts used for project preparation

### Project discovery prompt

```text
I am a beginner. I want to design an AI agent for this problem: monitoring a black-box LLM whose behavior may change without a visible model update.

The agent must make decisions when information is not complete.

Help me prepare the project.

1. Give me the technical terms for this problem.
2. Give me useful search queries.
3. Identify relevant technical communities.
4. Identify researchers and engineers whose work is relevant.
5. Give me questions about hidden states, evidence, actions, and errors.
6. Identify each claim that needs a source or a test.
7. Tell me which parts of the problem are not clear.

Do not present uncertain information as fact.
```

### Design review prompt

```text
Review this monitoring-agent design as a skeptical ML systems engineer.
Identify missing hidden states, unrealistic assumptions, weak evidence signals,
poorly defined actions, incorrect cost assumptions, and failure modes that the
current policy would miss. Separate facts, assumptions, and hypotheses.
```

### Probability review prompt

```text
Review the belief-state and decision-rule design.
Check whether the hidden states are mutually understandable, whether the priors
and likelihoods have evidence behind them, whether the decision threshold is
cost-consistent, and whether the investigation action has a measurable value.
Do not accept an arbitrary probability as ground truth.
```

## 13. Important AI errors to guard against

1. **Treating observability as proof of correctness.** Traces show what happened, but they do not prove that the final behavior was correct.
2. **Treating an LLM judge as ground truth.** Judge reliability can vary, so automated scores need validation.
3. **Assuming output drift proves a provider model update.** Behavioral change can also come from prompt changes, context changes, distribution shift, tool behavior, or evaluator noise.
4. **Using popularity as evidence of relevance.** A large technical account or community is not automatically useful for this specific project.
5. **Using a single quality score as the complete state representation.** A model can preserve average quality while failing on a narrow but high-cost subset of cases.
6. **Confusing a plausible simulation with a real deployment result.** Simulated labels and costs must be clearly separated from observed production evidence.

## 14. Claims that require a source or test

| Claim | Verification needed |
|---|---|
| Hosted LLM behavior can change over time | Source plus controlled repeated evaluation |
| Silent provider updates can create application regressions | Source plus version/model comparison where possible |
| Infrastructure health can remain normal while model behavior degrades | Production-style evaluation or controlled simulation |
| `INVESTIGATE` can reduce costly errors | Controlled experiment comparing action policies |
| External LLM judges are sufficiently reliable | Agreement study against human or reference labels |
| A threshold policy is inferior to an active policy | Same test cases, same costs, policy comparison |
| Additional probing has positive value | Measure error reduction against probe cost |

## 15. Material reviewed for the project

The supplied Week 1 project template established the required structure: one problem, incomplete information, an actionable agent, human discussion, testing, probability decisions, AI review, and a reproducible project record.

The supplied project material identified the specific problem as black-box LLM monitoring under non-stationary conditions and focused the project on model drift, POMDPs, active sensing, black-box uncertainty estimation, conformal prediction, and LLM guardrails.

The supplied resource set included:

- Operationalizing AI Agents: From Experimentation to Production, Databricks roundtable
- It's 2026, and We're Still Talking Evals, MLOps Community
- Signals your production LLM stopped behaving like before, Snowinch
- Monitoring an agent after it ships: drift, regression, and evaluation in production, FlowScope
- Test Before You Deploy: Governing Updates in the LLM Supply Chain, arXiv
- How is ChatGPT's behavior changing over time?, arXiv
- LLM Observability & Monitoring: How to Evaluate Agent Behavior, LangChain
- AI Agent Observability in Production: 2026 Guide, Game Changer Labs
- Evaluate Amazon Bedrock Agents with Ragas and LLM-as-a-Judge, AWS
- Agent-as-a-Judge: Evaluate Agents with Agents, ICML 2025
- How Reliable is Multilingual LLM-as-a-Judge?, EMNLP 2025

## 16. Project output target

The immediate Week 1 output is a small, testable black-box monitoring agent with:

- clearly defined observable inputs
- explicit hidden states
- a belief representation
- `ACCEPT / INVESTIGATE / REJECT` actions
- explicit error costs
- a baseline policy
- a second active policy
- reproducible test cases
- a probability decision record
- documented failure cases
- human-control boundaries

The goal is not to claim that the monitoring approach works before testing it. The goal is to build a project in which the claim can be tested and either supported, modified, or rejected.
