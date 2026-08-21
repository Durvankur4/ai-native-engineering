import csv
import json
from pathlib import Path


BASE_DIR = Path(__file__).parent

PROBES_FILE = BASE_DIR / "probes.csv"
CURRENT_FILE = BASE_DIR / "current_responses.csv"
OUTPUT_FILE = BASE_DIR / "agent_results.csv"


def load_probes():

    probes = {}

    with open(
        PROBES_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            probes[row["probe_id"]] = row

    return probes


def load_scenarios():

    scenarios = []

    with open(
        CURRENT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            scenarios.append(row)

    return scenarios


def normalize_response(response):

    if response is None:
        return ""

    response = response.strip()

    try:

        data = json.loads(response)

        return json.dumps(
            data,
            sort_keys=True
        )

    except (json.JSONDecodeError, TypeError):

        return response.lower()


def classify_change(probe, current):

    if current is None or current.strip() == "":
        return "missing"

    baseline = normalize_response(
        probe["baseline_response"]
    )

    current = normalize_response(
        current
    )

    if baseline == current:
        return "none"

    if probe["severity"] == "major":
        return "major"

    return "minor"


def calculate_belief(probes, results):

    stable_score = 0.0
    changed_score = 0.0
    unknown_score = 0.0

    for result in results:

        probe = probes[result["probe_id"]]

        severity = probe["severity"]
        change = result["change_type"]

        if severity == "major":
            weight = 2.0
        else:
            weight = 1.0

        if change == "none":

            stable_score += weight

        elif change == "major":

            changed_score += weight * 2

        elif change == "minor":

            changed_score += weight
            unknown_score += weight * 0.5

        elif change == "missing":

            unknown_score += weight * 2

    total = (
        stable_score
        + changed_score
        + unknown_score
    )

    if total == 0:

        return {
            "stable": 0.0,
            "changed": 0.0,
            "unknown": 1.0
        }

    return {
        "stable": stable_score / total,
        "changed": changed_score / total,
        "unknown": unknown_score / total
    }


def choose_action(belief):

    if belief["changed"] >= 0.60:
        return "REJECT"

    if belief["stable"] >= 0.80:
        return "ACCEPT"

    return "INVESTIGATE"


def investigate(probes, scenario):

    results = []

    for probe_id, probe in probes.items():

        current = scenario.get(probe_id, "")

        change_type = classify_change(
            probe,
            current
        )

        if change_type == "none":
            probe_action = "ACCEPT"

        else:
            probe_action = "INVESTIGATE"

        results.append({
            "probe_id": probe_id,
            "category": probe["category"],
            "change_type": change_type,
            "probe_action": probe_action,
            "severity": probe["severity"]
        })

    belief = calculate_belief(
        probes,
        results
    )

    overall_action = choose_action(
        belief
    )

    return results, belief, overall_action


def export_results(scenario_results):

    fields = [
        "scenario_id",
        "description",
        "stable_belief",
        "changed_belief",
        "unknown_belief",
        "overall_action"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        for result in scenario_results:
            writer.writerow(result)


def main():

    print("AI MODEL BEHAVIOR INVESTIGATOR")
    print("=" * 70)

    probes = load_probes()
    scenarios = load_scenarios()

    scenario_results = []

    for scenario in scenarios:

        scenario_id = scenario["scenario_id"]
        description = scenario["description"]

        results, belief, action = investigate(
            probes,
            scenario
        )

        print(f"\n{scenario_id} - {description}")

        print(f"Stable:   {belief['stable']:.2f}")
        print(f"Changed:  {belief['changed']:.2f}")
        print(f"Unknown:  {belief['unknown']:.2f}")
        print(f"Action:   {action}")

        scenario_results.append({
            "scenario_id": scenario_id,
            "description": description,
            "stable_belief": round(
                belief["stable"], 3
            ),
            "changed_belief": round(
                belief["changed"], 3
            ),
            "unknown_belief": round(
                belief["unknown"], 3
            ),
            "overall_action": action
        })

    export_results(scenario_results)

    print("\n" + "=" * 70)
    print(f"Completed {len(scenarios)} scenarios.")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()