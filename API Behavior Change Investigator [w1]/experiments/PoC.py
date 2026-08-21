# Known good responses from the API
baseline = {
    "probe_1": "4",
    "probe_2": "Paris",
    "probe_3": '{"status": "ok"}',
    "probe_4": "positive"
}

# Simulated current API responses
# Change these to test different situations
current_api = {
    "probe_1": "4",
    "probe_2": "London",
    "probe_3": '{"status": "ok"}',
    "probe_4": "positive"
}


# Send probes to the API
def run_probes():
    results = {}

    for probe in baseline:
        results[probe] = current_api[probe]

    return results



# Compare current responses with the baseline
def compare_results(results):
    changed = 0

    for probe in baseline:
        if results[probe] != baseline[probe]:
            changed += 1

    return changed / len(baseline)


# Update belief based on the evidence
def update_belief(change_rate):

    if change_rate == 0:
        return {
            "stable": 0.95,
            "changed": 0.03,
            "unknown": 0.02
        }

    if change_rate >= 0.5:
        return {
            "stable": 0.05,
            "changed": 0.90,
            "unknown": 0.05
        }

    return {
        "stable": 0.40,
        "changed": 0.40,
        "unknown": 0.20
    }


# Choose the agent action
def choose_action(belief):

    if belief["changed"] >= 0.80:
        return "REJECT"

    if belief["stable"] >= 0.80:
        return "ACCEPT"

    return "INVESTIGATE"


# Main agent
def main():

    print("Running probes...")

    results = run_probes()

    change_rate = compare_results(results)

    belief = update_belief(change_rate)

    action = choose_action(belief)

    print("\nChange rate:", change_rate)

    print("\nBelief:")
    for state, probability in belief.items():
        print(f"{state}: {probability:.2f}")

    print("\nAgent action:", action)


if __name__ == "__main__":
    main()