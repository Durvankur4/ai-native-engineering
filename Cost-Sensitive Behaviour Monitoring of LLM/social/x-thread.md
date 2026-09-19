1/ I built a black-box LLM monitor for silent behavioral change.

The agent sees outputs, evaluation signals, and runtime evidence—but not the provider's true model state.

2/ It maintains beliefs over STABLE / DEGRADED / TRANSIENT / DISTRIBUTION_SHIFT and chooses ACCEPT / INVESTIGATE / REJECT.

3/ The experiment compares a static threshold, a binary belief policy, and an active policy with a fixed investigation budget.

4/ The current 50-case benchmark is deterministic simulation. It is deliberately labeled as simulation, not production evidence.

5/ The next step is replaying historical LLM generations such as the public LLMDrift data and calibrating the likelihoods against human labels.

6/ Open question: when is one more probe worth its latency and compute cost?
