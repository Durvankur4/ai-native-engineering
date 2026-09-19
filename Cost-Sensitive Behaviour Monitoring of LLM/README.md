# Active Cost-Sensitive Monitoring of Black-Box LLM Behavior

This revision addresses the main technical criticisms of the earlier paper rather than only listing them as limitations.

## What changed

1. The six initial evidence channels are modeled with a full empirical joint likelihood fitted on separate synthetic training cases. This removes the naive conditional-independence assumption for the initial observation.
2. The simulator now contains a shared latent failure pressure so correlated quality, semantic, formatting, latency, and error signals can co-vary.
3. The main policy uses explicit costs for all four latent states instead of collapsing the decision to P(DEGRADED).
4. INVESTIGATE now uses genuine two-step lookahead, not a one-step calculation with an unused second-round budget.
5. The evaluation includes baseline, legacy binary-naive, binary-joint, state-aware direct, random-acquire, always-acquire, EIG one-step, VOI one-step, and VOI two-step policies.
6. Investigation cost is selected on development seeds only, then locked before the 20-seed test evaluation.
7. Test reporting includes means, standard deviations, and 95% confidence intervals.

## Locked experimental protocol

- Joint evidence-model training: 6,000 synthetic cases, seed 901.
- Development seeds for investigation-cost selection: 100 to 104.
- Candidate investigation costs: 0.4, 0.6, 0.8, 1.0, 1.2.
- Selected cost: 0.4, chosen only from the development split.
- Held-out evaluation: seeds 0 to 19, 120 cases per seed.
- Primary illustrative run: 50 cases, seed 7.
- Main active probe budget: at most 2 probes per case.

## Main held-out result

The active two-step policy has mean decision cost 80.42 +/- 3.04 at 95% CI across 20 held-out seeds, compared with 85.73 +/- 5.02 for one-step decision-aware VOI, 94.00 +/- 2.76 for one-step EIG acquisition, and 98.70 +/- 3.38 for always-acquire. It uses 84 probes per 120-case seed on average, versus 120 for always-acquire.

The same test run gives event recall 0.973 +/- 0.009 and event precision 0.959 +/- 0.012 for the active policy.

These are synthetic results and are not production evidence.

## Remaining limitations

Real monitoring traces, human-reviewed labels, measured probe latency/costs, and richer sequential probe dependencies remain unavailable. The paper states these limitations explicitly rather than presenting the synthetic benchmark as production validation.

## Reproduction

```bash
python -m pytest -q
python -m experiments.run_experiment
python -m experiments.run_scaled
python -m experiments.multiseed
python -m experiments.sensitivity
```
