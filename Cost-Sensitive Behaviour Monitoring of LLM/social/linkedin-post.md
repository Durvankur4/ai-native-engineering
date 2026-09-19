I built a small active monitor for a black-box LLM that can silently change behavior.

The agent observes external signals—task quality, semantic drift, formatting/safety changes, latency and error rates—and reasons over hidden states instead of treating one score as ground truth.

The key design is an `ACCEPT / INVESTIGATE / REJECT` policy. `INVESTIGATE` has a fixed probe budget and is only justified when additional evidence has enough estimated value to offset its cost.

The first experiment uses 50 reproducible cases and compares a static threshold baseline, a binary policy, and the active policy. The current results are simulation results, not production evidence.

The design was changed after public feedback to add historical incident replay, score history, and a fixed investigation budget.

Largest limitation: the belief model and costs still need calibration against human labels and real production traces.

The technical question I’m testing next: does active evidence collection actually reduce false acceptance at acceptable investigation cost?
