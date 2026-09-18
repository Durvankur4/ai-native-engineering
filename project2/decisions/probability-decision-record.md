# Probability Decision Record

## Case

`case-038` is a distribution-shift example in the Week 1 simulation. The true hidden state is intentionally treated as unknown to the agent at decision time.

## Prior

| Hidden state | Prior |
|---|---:|
| STABLE | 72% |
| DEGRADED | 12% |
| TRANSIENT | 8% |
| DISTRIBUTION_SHIFT | 8% |
| **Total** | **100%** |

## Observed evidence

For the illustrative record, the first probe reports:

- quality below the trusted baseline;
- semantic drift above the trigger level;
- no formatting failure;
- no safety shift;
- normal latency;
- low runtime error rate.

The likelihoods are the explicit hypotheses in `src/model.py`; they are not claimed to be empirically calibrated production probabilities.

## Posterior update

The agent multiplies the prior by the corresponding likelihood for each observed signal and normalizes the resulting state masses to 100%.

## Investigation

The active policy computes a one-step expected value of information for candidate probes. It compares the expected reduction in decision loss against the fixed investigation cost (`1`). The investigation budget is bounded at two rounds.

## Decision rule

For the documented 0/1/3/10 table, let `p = P(DEGRADED | E)`. `ACCEPT` has expected cost `10p`; `REJECT` has expected cost `3(1-p)`. Break-even is `10p = 3(1-p)`, so `p = 3/13 = 23.08%`.

- `p <= 23.08%` → `ACCEPT`
- `p > 23.08%` → `REJECT`

The active policy may choose `INVESTIGATE` first when the estimated value of the next probe is positive after paying the investigation cost. Search stops when value-of-information is no longer positive or the two-round probe budget is exhausted.

The exact threshold is therefore cost-sensitive rather than a generic 0.5 probability cutoff.

## Audit fields

- timestamp: `2026-09-08T14:54:00+05:30` (recording timestamp; not a claim about data collection time)
- data version: `week1-synthetic-v1`
- model version: `belief-policy-v1`
- policy version: `active-voi-v1`
- probe budget: `2`

## Human-control boundary

The agent is a monitoring gate, not an autonomous incident commander. A real deployment should escalate high-impact cases to a human with incident history, business context, and provider communications that are unavailable to the black-box observer.
