# Probability Decision Record

## Decision context

The monitor operates with a hidden state and incomplete evidence. The state prior is hypothetical and is used only to construct a reproducible synthetic decision surface.

## Prior

| Hidden state | Prior |
|---|---:|
| `STABLE` | 72% |
| `DEGRADED` | 12% |
| `TRANSIENT` | 8% |
| `DISTRIBUTION_SHIFT` | 8% |
| **Total** | **100%** |

## Direct decision threshold

The current cost table is:

| Outcome | Cost |
|---|---:|
| False `ACCEPT` | 10.0 |
| False `REJECT` | 3.0 |
| `INVESTIGATE` | 0.8 |

For `p = P(DEGRADED | E)`:

`C_ACCEPT = 10p`

`C_REJECT = 3(1-p)`

Break-even occurs at:

`p = 3 / 13 = 0.2308`

Therefore:

- `p <= 0.2308` -> `ACCEPT`
- `p > 0.2308` -> `REJECT`

## Correct investigation rule

The previous implementation mixed gross and net value of information and reported an inconsistent expected investigation cost. The revised rule is:

`gross_VOI = current_direct_cost - expected_post_probe_direct_cost`

`net_VOI = gross_VOI - investigation_cost`

Discretionary investigation is selected only when:

`gross_VOI > investigation_cost`

The expected cost stored for an investigation is:

`expected_post_probe_direct_cost + investigation_cost`

This makes the investigation threshold explicitly cost-sensitive.

## Coverage audit

Failure analysis found that aggregate quality could remain healthy while a capability degraded. A bounded capability-coverage audit was added as a separate design mechanism.

Every fourth observation within each task category triggers a `capability_issue` probe, with a maximum of two investigation rounds. The audit is not represented as positive VOI unless it independently satisfies the VOI rule; it is an explicit coverage budget intended to prevent persistent blind spots in the observation layer.

## Evidence likelihoods for the capability probe

| State | `P(capability_issue)` |
|---|---:|
| `STABLE` | 0.01 |
| `DEGRADED` | 0.95 |
| `TRANSIENT` | 0.10 |
| `DISTRIBUTION_SHIFT` | 0.20 |

These numbers are synthetic hypotheses.

## Human-control boundary

The prototype is a monitoring gate, not an autonomous incident commander. High-impact real-world actions should remain subject to human review, historical incident context, and operational safeguards that are unavailable to a black-box monitor.
