## 1. Technical terms you should use

| Term                                  | Why it matters                                                                                           |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **LLM behavioral drift**              | Change in observable model behavior over time                                                            |
| **Model/API drift**                   | Broader term covering behavior changes at an API endpoint                                                |
| **Behavioral change detection**       | Detecting that an endpoint behaves differently from its baseline                                         |
| **Longitudinal LLM evaluation**       | Evaluating the same system repeatedly over time                                                          |
| **LLM regression testing**            | Checking whether a change caused previously acceptable behavior to degrade                               |
| **Black-box model evaluation**        | Inferring behavior using only inputs and outputs                                                         |
| **Model fingerprinting**              | Building a behavioral signature of an endpoint and comparing future responses against it                 |
| **API observability**                 | Monitoring responses, errors, latency, tokens, versions, etc.                                            |
| **AI/LLM observability**              | Observing model behavior rather than just infrastructure                                                 |
| **Concept drift**                     | Statistical ML term for changing relationships/distributions; related, but not identical to your problem |
| **Distribution shift**                | Change in the input distribution that can look like model drift                                          |
| **Change-point detection**            | Statistical detection of a point where behavior changes                                                  |
| **Anomaly detection**                 | Detecting observations that differ from an expected baseline                                             |
| **Uncertainty estimation**            | Estimating how confident the agent should be in its conclusion                                           |
| **Selective prediction / abstention** | Allowing the system to say "I don't know" rather than forcing a decision                                 |
| **Decision-making under uncertainty** | The theoretical framing for your accept/reject/investigate decision                                      |
| **Evidence aggregation**              | Combining multiple weak signals into a decision                                                          |
| **Causal attribution**                | Determining *why* behavior changed                                                                       |
| **Provenance**                        | Tracking where evidence/configuration/model information came from                                        |

There is already research specifically exploring black-box endpoint stability and behavioral fingerprints ([DOI][1])

---

# 2. Useful search queries


### Start 

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

### incomplete-information angle

```text
"decision making under uncertainty" AI agent
"selective prediction" language models
"abstention" LLM evaluation
"AI agent" "uncertainty" decision making
"risk sensitive" decision making LLM
"evidence aggregation" AI agents
```

### Detecting *why* something changed

```text
"LLM drift" causal attribution
"LLM behavior change" attribution
"model drift" change point detection LLM
"LLM regression" root cause analysis
"AI observability" behavioral drift
```

### API-specific

```text
"LLM API" "silent update"
"LLM API" "model behavior changed"
"LLM API" "behavioral consistency"
"API endpoint" LLM stability
"black box" LLM API monitoring
"model version" behavioral regression LLM
```

### Search Reddit specifically

```text
site:reddit.com/r/LLMDevs "model update" behavior
site:reddit.com/r/mlops "LLM drift"
site:reddit.com/r/OpenAI "behavior changed"
site:reddit.com/r/ClaudeAI "behavior changed"
site:reddit.com/r/LocalLLaMA "model behavior"
site:reddit.com/r/AI_Agents "evaluation" regression
```

A useful real-world signal is that developers report cases where an API continues returning HTTP-successful responses while JSON adherence, tool calling, refusals, or agent behavior changes. That is almost exactly the failure mode a proposed system should investigate. ([Reddit][2])

---

# 3. Reddit communities

prioritize these:

| Community               | Relevance                                                                                                                                                                                            |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **r/LLMDevs**           | Probably the closest fit. Developers discuss model APIs, agents, evaluation, model changes and production problems. ([Reddit][3])                                                                    |
| **r/MLOps**             | Very important because your system overlaps with monitoring, regression testing, deployment and production ML. The community explicitly covers evaluation, monitoring and reliability. ([Reddit][4]) |
| **r/AI_Agents**         | Useful for the agent-specific side: tool selection, autonomous actions, evaluation and failures.                                                                                                     |
| **r/MachineLearning**   | Better for academic terminology, papers and methodological discussions.                                                                                                                              |
| **r/LocalLLaMA**        | Useful because local models make behavioral changes easier to reproduce and compare; it also has extensive model-comparison discussions. ([Reddit][5])                                               |
| **r/OpenAI**            | Useful for firsthand reports of API/model behavior changes.                                                                                                                                          |
| **r/ClaudeAI**          | Useful for observing reports of behavioral changes across model updates.                                                                                                                             |
| **r/PromptEngineering** | Useful for understanding how prompt/model interactions create apparent behavioral changes. There are discussions about automated testing across model switches. ([Reddit][6])                        |
| **r/MLQuestions**       | Good for beginner-friendly methodological discussion around evaluation and regression. ([Reddit][7])                                                                                                 |

### One important warning

**Reddit should be evidence for discovering failure modes, not proof that a failure mode is statistically common.**

For example, a Reddit user saying "OpenAI changed the model" establishes that someone observed something—not necessarily that the provider actually changed the underlying model.

That distinction should become part of your research methodology.

---

# 4. Researchers / engineers to follow on X

I would start with people whose work overlaps **evaluation, ML systems, production AI, and model behavior** rather than simply following famous LLM researchers.

### Highest priority

**Chip Huyen — @chipro**

[Chip Huyen on X](https://x.com/chipro?utm_source=chatgpt.com)

Particularly relevant to AI engineering, production ML systems and evaluation. Her material explicitly discusses evaluating AI systems and engineering metrics. ([Thread Reader App][8])

**Hamel Husain — @HamelHusain**

[Hamel Husain on X](https://x.com/HamelHusain?utm_source=chatgpt.com)

Very relevant to **LLM evaluations, traces, error analysis and production evaluation**. His evaluation work recommends starting with manual error analysis before building elaborate evaluation infrastructure. ([Hamel Husain][9])

**Shreya Shankar — @sh_reya**

[Shreya Shankar on X](https://x.com/sh_reya?utm_source=chatgpt.com)

Worth following specifically for **LLM evaluation, data/ML systems and evaluation methodology**.

**Simon Willison — @simonw**

[Simon Willison on X](https://x.com/simonw?utm_source=chatgpt.com)

Useful for understanding practical changes in LLM APIs, model capabilities and developer-facing behavior.

**Eugene Yan — @eugeneyan**

[Eugene Yan on X](https://x.com/eugeneyan?utm_source=chatgpt.com)

Useful for production ML/AI engineering and evaluation thinking.

### Also worth following

**Jason Liu — @jxnlco**

[Jason Liu on X](https://x.com/jxnlco?utm_source=chatgpt.com)

Relevant to LLM evaluation and observability.

**Andrej Karpathy — @karpathy**

[Andrej Karpathy on X](https://x.com/karpathy?utm_source=chatgpt.com)

Less directly about your exact problem, but useful for understanding model behavior and AI engineering at a systems level.

---

# 5. Questions you should ask about your hidden state

This is probably the **most important part of your research**.

Your agent doesn't actually observe:

> "The model changed."

It observes evidence from which it has to infer a hidden state.

Define something like:

```text
H = {stable, changed, degraded, improved, unknown}
```

Then ask:

1. **What exactly is the hidden state?**

   * Model version?
   * Actual model weights?
   * Behavioral policy?
   * API routing?
   * System prompt?
   * Safety policy?
   * Inference configuration?

2. Can multiple hidden states produce the same observed output?

3. Can the same hidden state produce different outputs?

4. How do temperature and nondeterminism affect your inference?

5. Could the apparent drift actually come from changed user inputs?

6. Could it be caused by your own prompt changing?

7. Could it be caused by a retrieval/database change?

8. Could the provider route the request to another backend?

9. What evidence would distinguish **model change** from **input distribution shift**?

10. What does "changed" actually mean?

This is important because recent work has shown that API behavior can vary even when the apparent endpoint/model identity remains the same. ([DOI][1])

---

# 6. Questions about evidence

Your agent needs an **evidence model**, not simply a collection of observations.

Ask:

### Evidence sources

* API response
* HTTP metadata
* model/version identifier
* latency
* token usage
* error rate
* structured-output validity
* tool-call behavior
* refusal behavior
* benchmark score
* historical outputs
* provider changelog
* provider documentation
* user reports
* independent tests

Then ask:

> **How reliable is each source?**

For example:

| Evidence                                     | Strength |
| -------------------------------------------- | -------- |
| Provider explicitly announces version change | High     |
| Reproducible behavioral regression           | High     |
| Repeated black-box experiment                | High     |
| API metadata changed                         | High     |
| 1 Reddit report                              | Low      |
| One unusual response                         | Very low |
| "It feels worse"                             | Very low |

The interesting research problem is therefore not merely **detecting drift**.

It is:

> **How should an agent combine imperfect evidence to decide whether an AI API has changed?**

That is much more defensible as an AI-agent research problem.

---

# 7. Questions about actions

Your three actions are currently:

```text
ACCEPT
REJECT
INVESTIGATE
```

But define what they mean.

### ACCEPT

Does this mean:

> "Continue using the model"?

Or:

> "There is sufficient evidence that the model has not changed"?

Those are different decisions.

### REJECT

Does rejection mean:

> stop the API request?

Or:

> reject the model as unsuitable?

Again, different.

### INVESTIGATE

What does the agent actually do?

For example:

```text
Run additional probes
        ↓
Compare against historical baseline
        ↓
Check provider metadata
        ↓
Run regression suite
        ↓
Search provider changelog
        ↓
Recalculate confidence
```

This makes **INVESTIGATE** an actual agent action rather than a vague "I'm unsure."

---

# 8. Questions about errors

You should explicitly model at least four errors.

### False positive

Agent says:

> "The model changed."

But it didn't.

Possible cause:

**input distribution changed.**

### False negative

Agent says:

> "Accept."

But the model actually changed.

This is potentially much worse.

### Wrong attribution

Agent correctly detects:

> "Something changed."

But incorrectly concludes:

> "The model provider changed it."

when the real cause was your prompt, retrieval system, parser, etc.

### Wrong action

Agent correctly determines uncertainty but chooses **ACCEPT** when it should **INVESTIGATE**.

This last category is especially important because your system is not merely a detector—it is a **decision-making agent**.

---

# 9. Claims that need a source vs. claims that need a test

This distinction will make your research considerably stronger.

| Claim                                                        | Source or test?                   |
| ------------------------------------------------------------ | --------------------------------- |
| LLM APIs can change behavior over time                       | **Source + experiment**           |
| API providers sometimes update models                        | **Provider documentation/source** |
| Model names do not necessarily guarantee behavioral identity | **Source + experiment**           |
| Temperature can create output variability                    | **Source + experiment**           |
| Output distributions can be used to detect changes           | **Source + experiment**           |
| A golden dataset can detect regression                       | **Source + experiment**           |
| Reddit users experience behavioral changes                   | **Reddit evidence**               |
| Your detector can identify drift                             | **Your experiment**               |
| Your detector is better than a fixed threshold               | **Your experiment**               |
| Your agent chooses the correct action                        | **Your experiment**               |
| Your confidence score is calibrated                          | **Your experiment**               |
| Your system can distinguish model drift from input drift     | **Your experiment**               |
| Your system can identify the cause of drift                  | **Your experiment**               |
| Your agent reduces false positives                           | **Your experiment**               |
| Your agent reduces false negatives                           | **Your experiment**               |

Do **not** cite a paper to prove that *your proposed algorithm works*. That is something you must demonstrate experimentally.

---

# 10. What is unclear in your current problem

This is where I would be critical.

Your current formulation:

> "The agent observes a request to use an AI model/API. It must select accept, reject, or investigate because the model/API's current behaviour and whether it has changed are not known."

has **five major ambiguities**.

### 1. What is the "request"?

Is it:

```text
User → "Use GPT-X to summarize this"
```

or:

```text
Application → API call
```

or:

```text
Developer → "Switch from Model A to Model B"
```

These produce completely different systems.

---

### 2. What does "accept" mean?

Accepting a **request** is different from accepting a **model**.

You need to define the object being classified.

---

### 3. What does "changed" mean?

Changed relative to:

```text
yesterday?
last known version?
documented provider behavior?
your own baseline?
expected behavior?
another model?
```

You need a reference state.

---

### 4. What information does the agent actually receive?

For example:

```text
request
model name
API response
timestamp
historical responses
provider documentation
benchmark results
logs
```

Without defining the observation space, you cannot design the agent.

---

### 5. What happens after INVESTIGATE?

This is the biggest missing piece.

An agent that says **INVESTIGATE** but has no investigation procedure isn't really solving the problem.

You need:

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

That starts looking like a proper **partially observable decision problem** rather than a simple classifier.

---

# 11. The research direction I would recommend

I would narrow your project to this:

> **An agent that detects and investigates unexplained behavioral changes in black-box LLM APIs using historical behavioral fingerprints and incomplete evidence.**

Then your agent could maintain:

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

The core research question becomes:

> **Can an AI agent make reliable decisions about whether to trust an LLM API when its underlying state is unobservable and evidence is incomplete?**

That is substantially stronger than simply building another "LLM monitoring dashboard."

There is also a useful research precedent: recent work has explicitly investigated black-box behavioral fingerprints for detecting endpoint stability, while other work has studied longitudinal evaluation and attribution of drift. ([DOI][1])

### One thing I would *not* do yet

Don't start coding the agent.

First establish:

1. **Observation space**
2. **Hidden-state definition**
3. **Evidence types**
4. **Action semantics**
5. **Failure costs**
6. **Baseline construction**
7. **Experimental scenarios**

Only then design the agent architecture.

That will prevent you from accidentally building a generic "LLM evaluator" that already overlaps heavily with existing evaluation/observability tooling.

[1]: https://doi.org/10.1145/3786335.3813194?utm_source=chatgpt.com "Behavioral Fingerprints for LLM Endpoint Stability and Identity | Proceedings of the ACM Conference on AI and Agentic Systems"
[2]: https://www.reddit.com/r/OpenAI/comments/1u91x79/building_independent_llm_drift_detection_sharing/?utm_source=chatgpt.com "Building independent LLM drift detection - sharing the methodology, looking for feedback on the approach"
[3]: https://fi.reddit.com/r/LLMDevs/comments/1urscak/how_do_you_tell_an_intentional_gap_from_a/?utm_source=chatgpt.com "How do you tell an intentional gap from a forgotten one in AI-generated code?:LLMDevs"
[4]: https://www.reddit.com/r/mlops/comments/1t6e6he/rmlops_has_been_reopened/?utm_source=chatgpt.com "r/mlops has been re-opened"
[5]: https://vi.reddit.com/r/LocalLLaMA/comments/1oy1v7q/model_recommendations_for_128gb_strix_halo_and/?sort=new&utm_source=chatgpt.com "Model recommendations for 128GB Strix Halo and other big unified RAM machines? : LocalLLaMA"
[6]: https://www.reddit.com/r/PromptEngineering/comments/1ujgqsh/i_added_automated_testing_to_my_prompts_now/?utm_source=chatgpt.com "I added automated testing to my prompts. Now prompt changes fail CI if they break evaluation — including across model switches. Here's how it works."
[7]: https://www.reddit.com/r/MLQuestions/comments/1t81s8t/how_do_ai_engineers_actually_evaluate_llmrag/?utm_source=chatgpt.com "How do AI engineers actually evaluate LLM/RAG systems in practice?"
[8]: https://threadreaderapp.com/user/chipro?utm_source=chatgpt.com "Chip Huyen's Threads – Thread Reader App"
[9]: https://hamelhusain.substack.com/p/the-ultimate-ai-evals-faq-now-new?utm_source=chatgpt.com "The Ultimate AI Evals FAQ (Now New & Improved)"
