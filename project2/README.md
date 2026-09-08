# Active Black-Box LLM Monitoring Agent

## Problem

The agent observes external LLM inputs, outputs, evaluation signals, and runtime evidence and selects `ACCEPT`, `INVESTIGATE`, or `REJECT` because the actual model state and provider-side changes are hidden.

## What is implemented

- **Observable evidence:** task quality, semantic drift, formatting/safety changes, latency, error rate.
- **Hidden states:** `STABLE`, `DEGRADED`, `TRANSIENT`, `DISTRIBUTION_SHIFT`.
- **Belief:** explicit Bayesian-style state probabilities.
- **Actions:** `ACCEPT`, `INVESTIGATE`, `REJECT`.
- **Cost-sensitive policy:** false acceptance > false rejection > investigation.
- **Baseline:** static quality threshold.
- **Binary policy:** ACCEPT/REJECT using the same evidence model.
- **Active policy:** can spend a bounded investigation budget on an additional probe when estimated value-of-information exceeds probe cost.
- **Memory:** stores recent observations and beliefs for audit/replay; historical case retrieval is intentionally kept simple for Week 1.
- **Evaluation:** 50 labeled cases, confusion-style error counts, precision/recall for degradation detection, investigation rate, and decision cost.

## Important methodological boundary

The synthetic generator is **test data**, not production evidence. The current run is deliberately a stress test with an observational blind spot and an evaluator-noise false alarm, so failure analysis is possible. The likelihoods, costs, and state priors are explicit hypotheses chosen so the policy can be tested reproducibly. They should be recalibrated against human labels and historical incidents before any operational deployment.

## Real-world data path

This project is designed to replay the public **LLMDrift** dataset from Chen, Zaharia, and Zou, which contains historical generations and metadata for GPT-3.5/GPT-4 across diverse tasks and time periods. Their repository is Apache-2.0 and states that its generation CSVs include model, query parameters, query, reference answer, generated answer, and latency.

Source: https://github.com/lchen001/LLMDrift
Paper: https://arxiv.org/abs/2307.09009

Because this execution environment cannot clone GitHub, the included experiment uses a deterministic synthetic harness now. A future replay run can place any downloaded LLMDrift CSV under `data/` and adapt `src/real_data.py` into the normalized observation schema.

## Run

```bash
python -m experiments.run_experiment
```

Outputs are written to `results/`:

- `policy_metrics.csv`
- `baseline_decisions.csv`
- `binary_decisions.csv`
- `active_decisions.csv`
- `five_failure_cases.csv`
- `summary.json`

## Reproducibility

- Python 3.10+
- deterministic seed: `7`
- 50 cases
- no API key required

## Week 1 compliance map

| Requirement | Location |
|---|---|
| Input / hidden state / belief / action / cost / policy / feedback | `src/model.py`, `src/agent.py` |
| 30–50 test cases | `src/simulator.py` generates 50 |
| 2 policies + baseline | `src/evaluate.py` |
| five incorrect decisions | `results/five_failure_cases.csv` |
| probability decision record | `decisions/probability-decision-record.md` |
| repeatable test instructions | this README |
| human-control boundary | `decisions/probability-decision-record.md` |

## Architecture

```text
LLM probes -> observable evidence -> belief update -> cost/VOI policy
                                      |
                         +------------+------------+
                         |            |            |
                      ACCEPT     INVESTIGATE    REJECT
                                      |
                               extra probe
                                      |
                                final decision
```

## One-off agent call

```python
from src.agent import BlackBoxMonitoringAgent, Observation

agent = BlackBoxMonitoringAgent()
observation = Observation(quality=0.62, semantic_drift=0.41, format_failure=1,
                          safety_shift=0, latency_ms=510, error_rate=0.09)
decision = agent.act(observation, active=True)
print(decision.action, decision.belief, decision.reason)
```

## Current experiment result

The deterministic run in `results/summary.json` is the result actually executed in this environment. It is not production evidence.
