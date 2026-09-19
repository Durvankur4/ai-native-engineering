# Appendix D Submission Checklist

## Provenance note

The supplied project archive and the IJCAI-ECAI-26 formatting package did not contain a literal file named Appendix D or a verbatim 20-question Appendix D checklist. I therefore audited the 20 required gates below against the explicit requirements recorded in `README.md`, `review.md`, `review-record.md`, `decisions/probability-decision-record.md`, the experiment outputs, and the final manuscript. The answers below are the submission audit, not a claim that an unseen original Appendix D was recovered.

| # | Required question | Answer | Evidence / verification |
|---|---|---|---|
| 1 | Is the problem statement a specific black-box LLM monitoring decision problem? | **YES** | The manuscript defines hidden provider state and the `ACCEPT / INVESTIGATE / REJECT` action space. |
| 2 | Is the action space explicit and used consistently? | **YES** | `src/agent.py`, `src/model.py`, and the paper use the same three actions. |
| 3 | Is the hidden state unavailable to the agent at decision time? | **YES** | The simulator retains state labels for evaluation only; the agent consumes observations and belief inputs, not the hidden state label. |
| 4 | Are priors explicit, normalized, and labeled as assumptions? | **YES** | Prior = 0.72 Stable, 0.12 Degraded, 0.08 Transient, 0.08 Distribution Shift; total = 1.00. The paper labels them synthetic. |
| 5 | Are evidence sources and likelihoods printed in the paper? | **YES** | Six base evidence signals and their state-conditional bad-event likelihoods are printed as a table in the manuscript. |
| 6 | Is the probabilistic update fully specified? | **YES** | The paper gives the prior, joint likelihood construction, posterior normalization, and states the conditional-independence assumption. |
| 7 | Is the entropy arithmetic correct and interpreted correctly? | **YES** | `H_before = 1.291`, `H_after = 1.842`, so `Delta H = +0.551 bits`. The paper explicitly says uncertainty increased. |
| 8 | Is expected information gain distinguished from the realized entropy change? | **YES** | The paper separates the worked posterior entropy change from expected information gain used for probe choice. |
| 9 | Is evidence selection based on decision value rather than entropy reduction alone? | **YES** | One-step EIG is computed, then gross VOI compares current direct decision loss with expected post-probe direct loss. |
| 10 | Is the investigation-cost threshold implemented correctly? | **YES** | `gross_VOI = current_direct_cost - expected_post_probe_direct_cost`; investigate only when `gross_VOI > 0.8`; stored investigation cost is expected post-probe direct cost plus 0.8. |
| 11 | Is investigation bounded? | **YES** | The implementation caps investigation at two rounds. Scheduled coverage audits are also bounded by a fixed coverage interval. |
| 12 | Was a concrete design change made because of an observed failure? | **YES** | Aggregate-quality blind spots led to a targeted `capability_issue` probe on every fourth observation per task category. |
| 13 | Is there a primary experiment in the required 30 to 50 case range? | **YES** | The primary deterministic benchmark contains 50 cases with seed 7. |
| 14 | Are simpler baselines included? | **YES** | Static quality baseline, binary belief policy, and active policy are compared. |
| 15 | Are the important metrics printed in the paper itself? | **YES** | False accepts, false rejects, investigations, investigation rate, decision cost, recall, precision, and sensitivity results are printed in tables. |
| 16 | Are at least five failures classified from the new run? | **YES** | Five representative 120-case failures are printed: aggregate-quality blind spot, shift under-detection, probe non-resolution, quality-threshold false alarm, and measurement-noise false alarm. |
| 17 | Was a re-test performed and did a metric move? | **YES** | Active decision cost changed `222.0 -> 136.8`, false accepts `21 -> 10`, recall `0.588 -> 0.804`, and investigations `0 -> 31`. |
| 18 | Was investigation-cost sensitivity tested? | **YES** | Costs 0.4, 0.6, 0.8, 1.0, and 1.2 were run on the same 50-case benchmark; the resulting metrics are printed in the paper. |
| 19 | Are limitations and unresolved knowledge gaps explicit? | **YES** | The paper states synthetic priors/likelihoods, lack of calibration, one-seed evaluation, unmeasured probe latency/cost, causal confounding in the re-test, evaluator noise, and the limited loss model. |
| 20 | Are reproducibility, reference review, human-control, and AI-use requirements satisfied? | **YES** | `pytest -q` passes 6/6; all three experiment scripts were rerun; seven cited primary sources were reviewed; the paper contains a specific AI-use statement; and the project retains a human-control boundary. |

## Final checklist status

**20 / 20 gates answered.**

The only provenance caveat is that the literal Appendix D source was not present in the supplied project archive, so this audit is a reconstruction from the project requirements and review records rather than a verbatim transcription of an unavailable checklist.
