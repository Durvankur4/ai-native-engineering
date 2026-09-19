# Reviewer Weakness Response Audit

## Technical limitations

1. Conditional independence among initial evidence channels
   - Status: addressed in the main design.
   - Change: the initial likelihood is a joint distribution over all six binary evidence indicators, fit from 6,000 synthetic training cases with Laplace smoothing.
   - Validation: the simulator includes a shared latent failure-pressure variable. Mean absolute pairwise correlation is 0.265 for STABLE and 0.319 for DEGRADED, with maximum absolute correlations 0.728 and 0.936.
   - Remaining gap: repeated probe outcomes remain conditionally independent given hidden state.

2. Myopic one-step acquisition
   - Status: addressed within a bounded finite horizon.
   - Change: the main policy performs two-step decision-aware VOI planning and forbids reusing a probe within one episode.
   - Validation: 20 held-out seeds compare one-step VOI with two-step VOI.
   - Remaining gap: this is not a general infinite-horizon POMDP solver.

3. Binary DEGRADED-only decision objective
   - Status: addressed.
   - Change: the main policy uses explicit state-aware costs for STABLE, DEGRADED, TRANSIENT, and DISTRIBUTION_SHIFT.
   - Validation: all main-policy decisions minimize expected four-state loss.
   - Remaining gap: cost values are synthetic and require deployment calibration.

## Experimental gaps

4. Synthetic benchmark only
   - Status: explicitly retained as a limitation.
   - The paper does not claim production validity and specifies a real replay study with human labels and measured probe costs as the next decisive experiment.

5. Limited baselines
   - Status: addressed.
   - Added comparisons: static threshold, binary naive Bayes, binary joint, direct state-aware, random acquisition, always-acquire, one-step EIG, one-step VOI, and two-step VOI.

6. Sparse statistics and underperformance across seeds
   - Status: addressed.
   - Added 20 held-out seeds, seed-level means, 95% t confidence intervals, paired seed-level cost differences, and Brier error.
   - Investigation cost is selected only on five development seeds 100 through 104.

## Clarity issues

7. Four-state to cost mapping
   - Status: addressed.
   - The paper prints the complete action-cost table and defines expected action cost over all four hidden states.

8. Evidence generation details
   - Status: addressed.
   - The paper describes six initial channels, thresholds, task categories, shared latent failure pressure, blind-spot regime, noisy stable regime, training split, development split, and held-out test protocol.
   - Remaining gap: the generator is still synthetic and not a validated model of production covariance.

## Related work

9. Active feature acquisition and POMDP work
   - Status: addressed.
   - The paper discusses active feature acquisition, Li and Oliva's Active-Acquisition POMDP formulation, POMDP surveys, and change-point detection literature.
   - C-DAC/AA-POMDP was not cited by name unless the source identity and primary publication could be verified; AA-POMDP is discussed through the verified Li and Oliva reference.

10. LLM monitoring and evaluator reliability
   - Status: addressed.
   - The paper cites LLM behavior drift and two 2025 evaluator-reliability/checklist studies and explains why the current synthetic benchmark does not substitute for human review.

## Final reproducibility status

- Tests: 7/7 passed.
- Development seeds: 100 through 104.
- Held-out test seeds: 0 through 19.
- Training cases: 6,000, seed 901.
- Cases per held-out seed: 120.
- Investigation cost selected: 0.4.
- Primary active mean decision cost: 81.51 +/- 3.70, 95% t confidence interval.
- One-step VOI: 84.92 +/- 3.97.
- EIG: 92.75 +/- 3.83.
- Always-acquire: 99.60 +/- 4.63.
- Baseline: 231.30 +/- 3.74.
- Active event recall: 0.968 +/- 0.011.
- Active event precision: 0.962 +/- 0.010.
- Active probe calls: 84.90 +/- 1.23 per 120 cases.
- No Unicode em dash, en dash, or minus characters remain in the Markdown manuscript.
