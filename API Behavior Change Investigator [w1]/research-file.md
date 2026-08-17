# Research Preparation: Model/API Behavior Change Investigator

## 1. The Problem Statement

An AI agent observes a request to use an AI model or API. The current behavior of that model/API, and whether it has changed relative to a known baseline, may be unknown.

The agent must make a decision from incomplete and imperfect evidence:

- **ACCEPT** — proceed when the available evidence supports continued use.
- **REJECT** — do not proceed when the evidence indicates unacceptable behavior or risk.
- **INVESTIGATE** — collect additional evidence when the current evidence is insufficient for a reliable decision.

The core difficulty is that the agent does not directly observe the true state of the model/API. It observes outputs, metadata, historical behavior, documentation, reports, and other signals, then infers the hidden state.

A stronger formulation is:

> **An agent that detects and investigates unexplained behavioral changes in black-box LLM APIs using historical behavioral fingerprints and incomplete evidence.**

---

## 2. The Project Objective

### Primary objective

Develop an AI agent that can make reliable **accept/reject/investigate** decisions about an LLM/API when its underlying state is not directly observable and available evidence is incomplete.

### Specific objectives

1. Establish a behavioral baseline for an LLM/API.
2. Detect whether observable behavior has changed relative to that baseline.
3. Distinguish genuine model/API changes from other causes such as:
   - input distribution shift,
   - prompt changes,
   - retrieval/database changes,
   - API routing,
   - inference configuration,
   - nondeterminism.
4. Aggregate evidence from multiple sources with different reliability levels.
5. Estimate confidence or uncertainty in the decision.
6. Investigate suspected changes instead of forcing a binary conclusion.
7. Attribute a detected change to the most plausible cause when sufficient evidence exists.
8. Measure false positives, false negatives, attribution errors, and wrong-action errors.

### Core research question

> **Can an AI agent make reliable decisions about whether to trust an LLM API when its underlying state is unobservable and evidence is incomplete?**

---

## 3. Technical Terms

| Term | Why it matters |
|---|---|
| **LLM behavioral drift** | Change in observable model behavior over time |
| **Model/API drift** | Broader term covering behavior changes at an API endpoint |
| **Behavioral change detection** | Detecting that an endpoint behaves differently from its baseline |
| **Longitudinal LLM evaluation** | Evaluating the same system repeatedly over time |
| **LLM regression testing** | Checking whether a change caused previously acceptable behavior to degrade |
| **Black-box model evaluation** | Inferring behavior using only inputs and outputs |
| **Model fingerprinting** | Building a behavioral signature of an endpoint and comparing future responses against it |
| **API observability** | Monitoring responses, errors, latency, tokens, versions, etc. |
| **AI/LLM observability** | Observing model behavior rather than only infrastructure |
| **Concept drift** | Statistical ML term for changing relationships/distributions; related, but not identical to this problem |
| **Distribution shift** | Change in the input distribution that can look like model drift |
| **Change-point detection** | Statistical detection of a point where behavior changes |
| **Anomaly detection** | Detecting observations that differ from an expected baseline |
| **Uncertainty estimation** | Estimating how confident the agent should be in its conclusion |
| **Selective prediction / abstention** | Allowing the system to say "I don't know" rather than forcing a decision |
| **Decision-making under uncertainty** | The theoretical framing for accept/reject/investigate decisions |
| **Evidence aggregation** | Combining multiple weak signals into a decision |
| **Causal attribution** | Determining why behavior changed |
| **Provenance** | Tracking where evidence, configuration, model, and version information came from |
| **Partially observable decision problem** | Decision-making when the true system state cannot be directly observed |

---

## 4. Search Queries

### Core problem

```text
"LLM behavioral drift" detection
"LLM behavior drift" API
"LLM model drift" production
"LLM API behavioral changes"
"LLM endpoint stability" black box
"LLM behavioral fingerprinting"
"longitudinal LLM evaluation"
"LLM regression testing model updates"
```

### Incomplete-information and uncertainty angle

```text
"decision making under uncertainty" AI agent
"selective prediction" language models
"abstention" LLM evaluation
"AI agent" "uncertainty" decision making
"risk sensitive" decision making LLM
"evidence aggregation" AI agents
"partially observable" AI decision making LLM
```

### Detecting why behavior changed

```text
"LLM drift" causal attribution
"LLM behavior change" attribution
"model drift" change point detection LLM
"LLM regression" root cause analysis
"AI observability" behavioral drift
"LLM API" silent update attribution
```

### API-specific

```text
"LLM API" "silent update"
"LLM API" "model behavior changed"
"LLM API" "behavioral consistency"
"API endpoint" LLM stability
"black box" LLM API monitoring
"model version" behavioral regression LLM
"LLM endpoint" behavioral stability
```

### Reddit-specific searches

```text
site:reddit.com/r/LLMDevs "model update" behavior
site:reddit.com/r/mlops "LLM drift"
site:reddit.com/r/OpenAI "behavior changed"
site:reddit.com/r/ClaudeAI "behavior changed"
site:reddit.com/r/LocalLLaMA "model behavior"
site:reddit.com/r/AI_Agents "evaluation" regression
```

---

## 5. Reddit Communities

The following communities are relevant to the research topic and were identified in the research material:

| Community | Relevance |
|---|---|
| **r/LLMDevs** | Model APIs, agents, evaluation, model changes, and production problems |
| **r/MLOps** | Monitoring, regression testing, deployment, evaluation, and production ML |
| **r/AI_Agents** | Agent decision-making, tool use, evaluation, and failure modes |
| **r/MachineLearning** | Academic terminology, papers, methodology, and ML research |
| **r/LocalLLaMA** | Model comparisons, reproducibility, local deployment, and behavioral differences |
| **r/OpenAI** | Reports concerning API and model behavior changes |
| **r/ClaudeAI** | Reports concerning behavioral changes across model updates |
| **r/PromptEngineering** | Prompt/model interaction and evaluation across model changes |
| **r/MLQuestions** | Methodological questions around evaluation and regression |

### Important methodological warning

Reddit should be treated as a source for **discovering failure modes and generating hypotheses**, not as proof that a failure mode is statistically common.

A single report establishes that an observation occurred; it does not establish the prevalence or cause of the behavior.

---

## 6. Relevant X Accounts

### Highest priority

| Account | Relevance |
|---|---|
| **Chip Huyen — @chipro** | AI engineering, production ML systems, evaluation, and engineering metrics |
| **Hamel Husain — @HamelHusain** | LLM evaluations, traces, error analysis, and production evaluation |
| **Shreya Shankar — @sh_reya** | LLM evaluation, data systems, and evaluation methodology |
| **Simon Willison — @simonw** | Practical LLM APIs, model capabilities, and developer-facing behavior |
| **Eugene Yan — @eugeneyan** | Production ML/AI engineering and evaluation |

### Also relevant

| Account | Relevance |
|---|---|
| **Jason Liu — @jxnlco** | LLM evaluation and observability |
| **Andrej Karpathy — @karpathy** | Model behavior and AI engineering at a systems level |

---

## 7. Five Useful Papers / Articles

The first source was already identified in the research file. The remaining sources were added to complete the requested five-resource set and verified against current web sources.

### 1. Behavioral Fingerprints for LLM Endpoint Stability and Identity

**Authors:** Jonah Leshin, Manish Shah, Ian Timmis, Daniel Kang  
**Venue:** ACM Conference on AI and Agentic Systems, 2026  
**DOI:** 10.1145/3786335.3813194

Why it matters:

- Directly addresses black-box LLM endpoint stability.
- Uses behavioral fingerprints.
- Compares output distributions over time.
- Uses energy distance and permutation testing.
- Provides a concrete change-detection architecture.

Source: https://doi.org/10.1145/3786335.3813194

### 2. Token-Efficient Change Detection in LLM APIs

**Authors:** Timothée Chauvin, Clément Lalanne, Erwan Le Merrer, Jean-Michel Loubes, François Taïani, Gilles Tredan  
**Year:** 2026

Why it matters:

- Directly studies black-box change detection in LLM APIs.
- Useful for investigating statistical tests and probe design.
- Particularly relevant to reducing the cost of repeated API testing.

Source: https://arxiv.org/abs/2602.11083

### 3. How Is ChatGPT’s Behavior Changing over Time?

**Authors:** Lingjiao Chen, Matei Zaharia, James Zou  
**Venue:** Harvard Data Science Review, 2024

Why it matters:

- Provides empirical evidence that LLM behavior can vary over time.
- Useful for motivating longitudinal evaluation.
- Provides background for treating model behavior as something that must be measured repeatedly.

Source: https://hdsr.mitpress.mit.edu/pub/y95zitmz

### 4. Behavioral Consistency and Transparency Analysis on Large Language Model API Gateways

**Authors:** Guanjie Lin, Yinxin Wan, Shichao Pei, Ting Xu, Kuai Xu, Guoliang Xue  
**Year:** 2026

Why it matters:

- Studies black-box measurement of LLM API gateways.
- Examines silent model substitution, behavioral consistency, latency, and operational transparency.
- Closely matches the problem of determining whether an API is behaving as expected.

Source: https://arxiv.org/abs/2604.21083

### 5. The Ultimate AI Evals FAQ

**Author:** Hamel Husain  
**Year:** 2025

Why it matters:

- Practical reference for LLM evaluation.
- Covers error analysis, production evaluation, evaluation design, regression, and agentic workflows.
- Useful for designing the evaluation layer of the proposed agent.

Source: https://hamelhusain.substack.com/p/the-ultimate-ai-evals-faq-now-new

---

## 8. Questions That Need to Be Answered

### A. Hidden state

1. What exactly is the hidden state?
   - Model version?
   - Model weights?
   - Behavioral policy?
   - API routing?
   - System prompt?
   - Safety policy?
   - Inference configuration?

2. Can multiple hidden states produce the same observed output?
3. Can the same hidden state produce different outputs?
4. How do temperature and nondeterminism affect inference?
5. Could apparent drift actually come from changed inputs?
6. Could the prompt itself have changed?
7. Could retrieval or database state have changed?
8. Could the provider have routed requests to another backend?
9. What evidence distinguishes model change from input distribution shift?
10. What exactly does "changed" mean?

### B. Baseline

11. What should the reference state be?
   - Previous day?
   - Last known version?
   - Historical fingerprint?
   - Documented provider behavior?
   - Expected application behavior?

12. How large should the baseline dataset be?
13. How often should the baseline be refreshed?
14. How should nondeterministic outputs be represented?

### C. Evidence

15. Which evidence sources are most reliable?
16. How should conflicting evidence be handled?
17. How should evidence reliability be quantified?
18. How many independent observations are required before declaring a change?
19. How should provider announcements be weighted against black-box evidence?

### D. Investigation

20. What additional probes should be run after detecting a possible change?
21. How should the agent choose the next probe?
22. When should investigation stop?
23. What evidence is sufficient to move from INVESTIGATE to ACCEPT or REJECT?
24. Can the investigation identify the cause of the change?

### E. Decision-making

25. What exactly does ACCEPT mean?
26. What exactly does REJECT mean?
27. What exactly does INVESTIGATE mean?
28. How should the costs of false positives and false negatives affect the decision?
29. Should the agent optimize for accuracy, risk, expected loss, or calibrated confidence?

---

## 9. AI Prompts

These prompts can be used as starting points for research and experimentation.

### Prompt 1 — Behavioral assessment

```text
Given the current API response, historical baseline responses, API metadata, and known configuration, assess whether the endpoint appears stable, changed, degraded, improved, or unknown.

Do not assume that a behavioral difference proves a model update.

Return:
1. Observed differences
2. Evidence supporting change
3. Evidence against change
4. Alternative explanations
5. Confidence
6. Recommended action: ACCEPT, REJECT, or INVESTIGATE
```

### Prompt 2 — Evidence aggregation

```text
Analyze the following evidence about an LLM API.

For each evidence item:
- identify the observation,
- estimate its reliability,
- identify what hypothesis it supports,
- identify competing explanations.

Then aggregate the evidence without treating any single weak signal as conclusive.

Return:
- Stable probability
- Changed probability
- Unknown probability
- Main supporting evidence
- Main uncertainty
- Recommended action
```

### Prompt 3 — Causal attribution

```text
A behavioral change has been detected in an LLM API.

Evaluate these possible causes:
1. Model/version change
2. Provider routing change
3. Inference-stack change
4. Sampling/configuration change
5. Prompt change
6. Input distribution shift
7. Retrieval/database change
8. Nondeterminism

Rank the hypotheses using the available evidence.

Do not claim causal certainty when the evidence only supports correlation.
```

### Prompt 4 — Investigation planning

```text
A possible behavioral change has been detected, but evidence is insufficient for a final decision.

Select the smallest set of additional investigations that would most reduce uncertainty.

Possible investigations:
- repeated probes,
- baseline comparison,
- metadata inspection,
- regression suite,
- provider documentation/changelog,
- independent benchmark,
- alternative endpoint comparison.

Explain which uncertainty each investigation is intended to reduce.
```

### Prompt 5 — Decision policy

```text
Based on the evidence and estimated uncertainty, choose exactly one action:

ACCEPT
REJECT
INVESTIGATE

Do not force ACCEPT or REJECT when the evidence is insufficient.

State:
- decision,
- confidence,
- decisive evidence,
- unresolved uncertainty,
- expected consequence of making the wrong decision.
```

---

## 10. Important AI Errors

The system should explicitly model at least four error categories.

### 1. False positive

**Decision:** "The model changed."  
**Reality:** The model did not change.

Possible cause:

- input distribution shift,
- nondeterminism,
- prompt change,
- retrieval change,
- noisy observations.

### 2. False negative

**Decision:** "ACCEPT."  
**Reality:** The model actually changed.

This can be more costly than a false positive when a behavioral change breaks safety constraints, structured outputs, tool calls, or downstream systems.

### 3. Wrong attribution

The system correctly detects:

> "Something changed."

But incorrectly concludes:

> "The model provider changed the model."

The actual cause could be:

- prompt modification,
- retrieval system change,
- parser change,
- inference configuration,
- API routing,
- infrastructure changes.

### 4. Wrong action

The system correctly recognizes uncertainty but selects the wrong action.

Example:

> Evidence is insufficient → system chooses **ACCEPT** instead of **INVESTIGATE**.

This is important because the proposed system is not merely a detector. It is a **decision-making agent**.

---

## 11. Evidence Model

Potential evidence sources:

- API response
- HTTP metadata
- Model/version identifier
- Latency
- Token usage
- Error rate
- Structured-output validity
- Tool-call behavior
- Refusal behavior
- Benchmark score
- Historical outputs
- Provider changelog
- Provider documentation
- User reports
- Independent tests

### Example evidence hierarchy

| Evidence | Approximate strength |
|---|---|
| Provider explicitly announces version change | High |
| Reproducible behavioral regression | High |
| Repeated black-box experiment | High |
| API metadata changed | High |
| One Reddit report | Low |
| One unusual response | Very low |
| "It feels worse" | Very low |

The research problem is therefore not simply **detecting drift**.

The stronger problem is:

> **How should an agent combine imperfect evidence to decide whether an AI API has changed and whether it should still be trusted?**

---

## 12. Claims That Require Sources vs. Experiments

| Claim | Required evidence |
|---|---|
| LLM APIs can change behavior over time | Source + experiment |
| API providers sometimes update models | Provider documentation/source |
| Model names do not necessarily guarantee behavioral identity | Source + experiment |
| Temperature can create output variability | Source + experiment |
| Output distributions can detect changes | Source + experiment |
| A golden dataset can detect regression | Source + experiment |
| Reddit users report behavioral changes | Reddit evidence |
| A proposed detector identifies drift | Experiment |
| A detector is better than a fixed threshold | Experiment |
| The agent chooses the correct action | Experiment |
| A confidence score is calibrated | Experiment |
| The system distinguishes model drift from input drift | Experiment |
| The system identifies the cause of drift | Experiment |
| The agent reduces false positives | Experiment |
| The agent reduces false negatives | Experiment |

A paper should not be cited as evidence that a proposed algorithm works. That claim must be demonstrated experimentally.

---

## 13. Proposed Agent Loop

```text
OBSERVE
   ↓
FORM HYPOTHESES
   ↓
COLLECT EVIDENCE
   ↓
UPDATE BELIEF
   ↓
CHOOSE ACTION
   ↓
OBSERVE RESULT
```

### Agent state

```text
Hidden state:
    Stable
    Changed
    Unknown

Evidence:
    API metadata
    Probe outputs
    Historical baseline
    Regression tests
    Provider information
    External reports

Actions:
    Accept
    Investigate
    Reject
```

### Investigation loop

```text
Possible change
      ↓
Run additional probes
      ↓
Compare against historical baseline
      ↓
Check provider metadata
      ↓
Run regression suite
      ↓
Search provider documentation/changelog
      ↓
Recalculate confidence
      ↓
Accept / Reject / Continue investigation
```

---

## 14. Critical Scope Questions Before Implementation

The current problem formulation has five major ambiguities that should be resolved before coding.

### 1. What is the request?

Possible interpretations:

```text
User → "Use Model X to summarize this"
```

```text
Application → API call
```

```text
Developer → "Switch from Model A to Model B"
```

These produce different system designs.

### 2. What does ACCEPT mean?

Possible meanings:

- Continue using the model.
- Accept the model as sufficiently stable.
- Accept the individual API request.

These are different decisions.

### 3. What does REJECT mean?

Possible meanings:

- Stop the API request.
- Reject the model as unsuitable.
- Reject the current output.

The action must be explicitly defined.

### 4. What information does the agent receive?

A possible observation space is:

```text
Request
Model name
API response
Timestamp
Historical responses
Provider documentation
Benchmark results
Logs
Metadata
```

Without defining the observation space, the agent architecture cannot be specified precisely.

### 5. What happens after INVESTIGATE?

INVESTIGATE must correspond to an actual procedure rather than simply expressing uncertainty.

The procedure should specify:

- which probes to run,
- which evidence to collect,
- how evidence changes belief,
- when investigation stops,
- how the final action is selected.

---

## 15. Recommended Research Direction

A focused project definition is:

> **An agent that detects and investigates unexplained behavioral changes in black-box LLM APIs using historical behavioral fingerprints and incomplete evidence.**

This avoids building only another generic LLM monitoring dashboard.

The project should establish these components before implementation:

1. **Observation space**
2. **Hidden-state definition**
3. **Evidence types**
4. **Action semantics**
5. **Failure costs**
6. **Baseline construction**
7. **Experimental scenarios**
8. **Decision policy**
9. **Evaluation metrics**

Only after these definitions should the agent architecture and implementation be designed.
