# Knowledge Gaps and Residual Limitations

| Gap | Fixed now? | Treatment in paper |
|---|---|---|
| Correlated initial evidence | Yes | Joint six-channel likelihood and correlation audit |
| Myopic one-step acquisition | Partially | Two-step finite-horizon VOI |
| Binary DEGRADED-only objective | Yes | Four-state cost matrix and expected loss |
| Small single-seed evaluation | Yes | 20 held-out seeds plus development split |
| Limited baselines | Yes | Random, always, EIG, VOI, binary, state-aware baselines |
| Sparse uncertainty reporting | Yes | 95% t intervals and paired seed differences |
| Real monitoring traces | No | Explicit external-validity limitation |
| Human-reviewed labels | No | Explicit evaluator-reliability limitation |
| Measured probe cost and latency | No | 0.4 is a normalized development parameter, not currency |
| Sequential probe dependence | No | Initial evidence is joint; repeated probes remain conditionally independent given state |
| General POMDP planning | No | Two-step finite horizon only |
| Learned RL acquisition | No | Not added because simulator-only RL could learn simulator artifacts |
| Real change-point detection | No | Distribution shift is a synthetic latent state |
| External validation of priors and state costs | No | Priors and costs are explicitly hypothetical |
