import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent

PROBES_FILE = BASE_DIR / "probes.csv"
CURRENT_FILE = BASE_DIR / "current_responses.csv"
OUTPUT_FILE = BASE_DIR / "agent_results.csv"


# Load the probe definitions and baseline responses
def load_probes():

    probes = {}

    with open(PROBES_FILE, "r", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:
            probes[row["probe_id"]] = row

    return probes


# Load the responses produced by the current API
def load_current_responses():

    responses = {}

    with open(CURRENT_FILE, "r", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:
            responses[row["probe_id"]] = row["current_response"]

    return responses


# Normalize simple formatting differences
def normalize_response(response):

    if response is None:
        return ""

    response = response.strip()

    # Try to normalize JSON responses
    try:
        data = json.loads(response)
        return json.dumps(data, sort_keys=True)
    except (json.JSONDecodeError, TypeError):
        pass

    return response.lower()


# Determine how serious a change is
def classify_change(probe, current_response):

    baseline = probe["baseline_response"]

    if current_response is None or current_response.strip() == "":
        return "missing"

    old = normalize_response(baseline)
    new = normalize_response(current_response)

    if old == new:
        return "none"

    if probe["severity"] == "major":
        return "major"

    return "minor"


# Calculate the agent's belief
def update_belief(major, minor, missing, total):

    # Major changes are strong evidence of behavior change
    if major >= 2:
        return {
            "stable": 0.05,
            "changed": 0.90,
            "unknown": 0.05
        }

    # One major change is suspicious
    if major == 1:
        return {
            "stable": 0.20,
            "changed": 0.55,
            "unknown": 0.25
        }

    # Missing evidence means the agent cannot be confident
    if missing > 0:
        return {
            "stable": 0.30,
            "changed": 0.20,
            "unknown": 0.50
        }

    # No changes
    if minor == 0:
        return {
            "stable": 0.95,
            "changed": 0.03,
            "unknown": 0.02
        }

    # One or more minor changes
    change_rate = minor / total

    if change_rate <= 0.25:
        return {
            "stable": 0.45,
            "changed": 0.20,
            "unknown": 0.35
        }

    return {
        "stable": 0.15,
        "changed": 0.55,
        "unknown": 0.30
    }


# Decide what the agent should do
def choose_action(belief):

    if belief["changed"] >= 0.80:
        return "REJECT"

    if belief["stable"] >= 0.80:
        return "ACCEPT"

    return "INVESTIGATE"


# Run the investigation
def investigate(probes, current_responses):

    results = []

    major = 0
    minor = 0
    missing = 0

    for probe_id, probe in probes.items():

        current = current_responses.get(probe_id)

        change_type = classify_change(
            probe,
            current
        )

        if change_type == "major":
            major += 1

        elif change_type == "minor":
            minor += 1

        elif change_type == "missing":
            missing += 1

        results.append({
            "probe_id": probe_id,
            "category": probe["category"],
            "purpose": probe["purpose"],
            "baseline_response": probe["baseline_response"],
            "current_response": current or "",
            "change_type": change_type,
        })

    total = len(probes)

    belief = update_belief(
        major,
        minor,
        missing,
        total
    )

    action = choose_action(belief)

    return results, belief, action


# Export everything into a CSV
def export_results(results, belief, action):

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:

        fieldnames = [
            "probe_id",
            "category",
            "purpose",
            "baseline_response",
            "current_response",
            "change_type",
            "stable_belief",
            "changed_belief",
            "unknown_belief",
            "agent_action"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for result in results:

            result["stable_belief"] = belief["stable"]
            result["changed_belief"] = belief["changed"]
            result["unknown_belief"] = belief["unknown"]
            result["agent_action"] = action

            writer.writerow(result)


# Main program
def main():

    print("AI MODEL BEHAVIOR INVESTIGATOR")
    print("-" * 40)

    probes = load_probes()

    current_responses = load_current_responses()

    results, belief, action = investigate(
        probes,
        current_responses
    )

    print("\nInvestigation complete.")

    print("\nBelief:")

    print(
        f"Stable:   {belief['stable']:.2f}"
    )

    print(
        f"Changed:  {belief['changed']:.2f}"
    )

    print(
        f"Unknown:  {belief['unknown']:.2f}"
    )

    print("\nAgent action:", action)

    export_results(
        results,
        belief,
        action
    )

    print(
        f"\nResults exported to {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()