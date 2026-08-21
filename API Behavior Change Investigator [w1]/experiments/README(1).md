# Model/API Behavior Change Investigator

## Purpose

This project tests an agent that observes current model/API responses and chooses:

- `ACCEPT` — behavior appears stable.
- `INVESTIGATE` — evidence is incomplete, minor, or missing and should receive human review.
- `REJECT` — a major behavior change is detected.

The evaluation uses the supplied 30-scenario dataset and 10 probes.

## Important evaluation design

The correct label is **hidden from the agent during decision-making**.

The notebook first runs both agent policies and the baseline. Only after all predictions are recorded does it construct the hidden gold labels for evaluation.

The agent therefore cannot directly read the scenario description as a label or use the gold decision during inference.

## Policies

### Policy A — Threshold Belief

This follows the original proof-of-concept logic:

- Major probes receive higher weight.
- Major changes increase the `changed` belief.
- Minor changes contribute to both `changed` and `unknown`.
- Missing responses contribute to `unknown`.
- `changed >= 0.60` → `REJECT`
- otherwise `stable >= 0.80` → `ACCEPT`
- otherwise → `INVESTIGATE`

### Policy B — Cost-Sensitive

This policy is intentionally more conservative:

- Any major change → `REJECT`
- Any minor change or missing response, with no major change → `INVESTIGATE`
- No detected change → `ACCEPT`

## Baseline

The baseline is an always-`ACCEPT` policy.

It is intentionally simple so that the experiment can measure whether an evidence-based agent improves over a naive default.

## Evaluation metrics

The notebook reports:

- Confusion matrix
- Precision for `REJECT`
- Recall for `REJECT`
- False-positive quantity
- False-negative quantity
- Human-review rate
- Decision cost
- Calibration using Brier score for major-change probability

Accuracy is included only as a secondary metric.

## Decision-cost model

The experiment uses this cost matrix:

| Gold | Predicted ACCEPT | Predicted INVESTIGATE | Predicted REJECT |
|---|---:|---:|---:|
| ACCEPT | 0 | 1 | 2 |
| INVESTIGATE | 3 | 0 | 2 |
| REJECT | 10 | 3 | 0 |

The highest-cost error is accepting a major change. The reason is that an undetected major behavioral change can expose users to unsafe, privacy-violating, non-compliant, or materially incorrect behavior.

## Failure conditions

Incorrect decisions receive named failure conditions, such as:

- Missed Major Refund Drift
- Missed Major Shipping Drift
- Missed Safety Drift
- Missed Privacy Drift
- Accepted Missing Critical Response
- Missed Temporary Factual Drift
- Missed API Outage Behavior

The notebook examines at least five incorrect decisions, prioritizing the highest-cost errors.

## Files

```text
model_behavior_agent_test/
├── model_behavior_agent_evaluation.ipynb
├── probes.csv
├── current_responses.csv
├── README.md
└── generated after execution/
    ├── evaluation_results.csv
    ├── probe_actions.csv
    └── failure_analysis.csv
```

## Requirements

Python 3.9+ is recommended.

Install dependencies:

```bash
python -m pip install pandas numpy matplotlib scikit-learn jupyter
```

## Repeat the test

### 1. Open the project

```bash
cd model_behavior_agent_test
```

### 2. Start Jupyter

```bash
jupyter notebook
```

Open:

```text
model_behavior_agent_evaluation.ipynb
```

### 3. Run all cells

In Jupyter:

```text
Kernel → Restart Kernel and Run All Cells
```

### 4. Check outputs

The notebook creates:

- `evaluation_results.csv` — every scenario prediction for Policy A, Policy B, and the baseline.
- `probe_actions.csv` — every probe observation and investigation action.
- `failure_analysis.csv` — incorrect decisions, named failure conditions, explanations, and costs.

## Repeating with modified test data

Edit `current_responses.csv` while preserving:

- `scenario_id`
- `description`
- `P001` through `P010`

Then rerun the notebook from the beginning.

Do not add the correct decision label to the scenario input. The experiment is designed so the agent makes its decision before the hidden evaluation labels are revealed.

## Extending the experiment

To add scenarios:

1. Add a new row to `current_responses.csv`.
2. Provide responses for the existing probes.
3. Run the notebook.
4. The hidden evaluator derives the gold decision from the observed probe changes.
5. Review the resulting metrics and failure analysis.

To add a new probe:

1. Add a row to `probes.csv`.
2. Add the corresponding column to `current_responses.csv`.
3. Define its baseline response and severity.
4. Rerun the notebook.

## Research interpretation

A good result is not simply high accuracy. A useful behavior-change investigator should reduce high-cost false negatives while keeping human-review burden reasonable.

For this dataset, Policy B is designed to demonstrate that trade-off: it is more conservative than the original threshold policy and therefore should be evaluated using decision cost, false negatives, review rate, and calibration alongside accuracy.
