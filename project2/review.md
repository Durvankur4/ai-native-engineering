# Week 2 — Progress Notes (Probabilistic View of AI Agents)

*Numbers marked "hypothetical" are assumptions, not measured values, and are labeled as such.*

---

## Problem Statement (Stage 0 — Gate: passed)

The agent observes external LLM responses and API responses, and must choose
**accept / reject / investigate**, because whether the response is **adequate or degraded**
is not directly known (hidden state).

---

## Stage 1 — Hidden States and Priors (Gate: passed, priors hypothetical)

Final state set used in the experiment (4 states, not 5 — merged mild/severe degradation and
excluded input-distribution-shift from formal state modeling per below):

| State | Prior | Source |
|---|---|---|
| STABLE | 0.72 | Hypothetical (pulled from intuition, not counted from data) |
| DEGRADED | 0.12 | Hypothetical |
| TRANSIENT | 0.08 | Hypothetical |
| DISTRIBUTION_SHIFT | 0.08 | Hypothetical |
| **Total** | **1.00** | |

**Known limitation:** `DISTRIBUTION_SHIFT` is not independently generated or validated in the
simulator — it has a prior and receives Bayesian updates, but there is no ground-truth signal
confirming those updates are *correct*. Decision made: keep it in the model, but do **not** use
it to claim detection performance. State this explicitly in the paper's limitations section.

Earlier draft (superseded): a 5-state version existed with `DEGRADED` split into
`MILDLY_DEGRADED` / `SEVERELY_DEGRADED`, but the simulator only supports 4 states in the
current experiment.

---

## Stage 2 — Evidence and Likelihoods (Gate: passed — sourced from `src/model.py`)

Five usable evidence sources (a sixth, input-distribution shift as an *observable signal*,
was identified as missing from the simulator — see Open Items):

- Output/task quality
- Semantic drift
- Formatting / structural anomaly
- Safety shift
- Latency
- API error rate

Likelihood table — `P(evidence reads "bad" | state)`:

| Evidence | STABLE | DEGRADED | TRANSIENT | DISTRIBUTION_SHIFT |
|---|---:|---:|---:|---:|
| Low output quality | 0.08 | 0.78 | 0.60 | 0.35 |
| Semantic drift | 0.10 | 0.72 | 0.58 | 0.70 |
| Formatting failure | 0.04 | 0.55 | 0.35 | 0.22 |
| Safety shift | 0.03 | 0.38 | 0.18 | 0.30 |
| High latency | 0.10 | 0.33 | 0.72 | 0.15 |
| High API error | 0.04 | 0.45 | 0.55 | 0.12 |

**Note on independence:** the update below multiplies these six likelihoods together, which
assumes the six evidence signals are conditionally independent given the true state. This is
an assumption of the model, not something demonstrated — document this explicitly rather than
implying it was tested.

---

## Stage 3 — Worked Bayes Update and Entropy (Gate: passed)

**Observed evidence for this worked example:**
low quality, semantic drift, no formatting failure, no safety shift, normal latency, no API error.

**Per-state joint likelihood (product of the six terms, using complements for "no X" evidence):**

| State | Prior | Joint contribution (prior × ∏ likelihoods) |
|---|---:|---:|
| STABLE | 0.72 | 0.004634 |
| DEGRADED | 0.12 | 0.006929 |
| TRANSIENT | 0.08 | 0.001870 |
| DISTRIBUTION_SHIFT | 0.08 | 0.008005 |
| **P(E) = sum** | | **0.021437** |

**Worked column shown in full (DEGRADED):**
```
0.12 × 0.78  = 0.093600      (prior × low-quality likelihood)
0.093600 × 0.72 = 0.067392   (× semantic-drift likelihood)
0.067392 × 0.45 = 0.030326   (× no-formatting-failure = 1 − 0.55)
0.030326 × 0.62 = 0.018802   (× no-safety-shift = 1 − 0.38)
0.018802 × 0.67 = 0.012598   (× normal-latency = 1 − 0.33)
0.012598 × 0.55 = 0.006929   (× no-API-error = 1 − 0.45)
```

**Posterior (each contribution ÷ P(E) = 0.021437):**

| State | Posterior |
|---|---:|
| STABLE | 21.6% |
| DEGRADED | 32.3% |
| TRANSIENT | 8.7% |
| DISTRIBUTION_SHIFT | 37.3% |
| **Total** | **100.0%** ✓ |

**Entropy:**
- H_before (on the 0.72/0.12/0.08/0.08 prior) = 1.291 bits
- H_after (on the posterior above) = 1.842 bits
- **ΔH = H_after − H_before = 1.842 − 1.291 = +0.551 bits — entropy increased.**

**Interpretation:** the most likely state flips from STABLE (72% prior) to
DISTRIBUTION_SHIFT (37.3% posterior), but the evidence doesn't cleanly point at one
explanation — it knocks STABLE down hard while leaving DEGRADED, TRANSIENT, and
DISTRIBUTION_SHIFT all plausible. Belief spreads out rather than sharpening. This is a
legitimate and interesting finding, not an error: **evidence does not automatically reduce
uncertainty.**

---

## Cost Table (feeds Stage 4 — not yet started)

| Error / action | Cost |
|---|---:|
| Correct ACCEPT | 0 |
| Correct REJECT | 0 |
| Unnecessary INVESTIGATE | 1 |
| False REJECT | 3 |
| False ACCEPT of degradation | 10 |

*Hypothetical — no real organizational cost data available yet. Label as such in the paper.*

---

## Open Items / Known Gaps (for Limitations section)

- [ ] Priors (0.72/0.12/0.08/0.08) are hypothetical, not counted from data — label accordingly.
- [ ] `DISTRIBUTION_SHIFT` is not independently generated/validated in the simulator — belief
      is computed but not checked against ground truth. Do not use for detection-performance claims.
- [ ] Conditional independence of the six evidence signals given state is assumed, not tested.
- [ ] Stage 4 (information value vs. cost, decision threshold) — not started.
- [ ] Stages 5–11 (thresholds, umbrella problem, extensions, experiment, failure analysis,
      paper, social posts) — not started.

---

## Revision Log

- Entropy direction was initially mislabeled as a decrease (−0.551) in an earlier draft; the
  correct direction, given H_before = 1.291 and H_after = 1.842, is an increase (+0.551).
- The DEGRADED likelihood column was independently re-derived term by term to confirm the
  joint contribution of 0.006929 (see worked column above).