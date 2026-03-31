#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITIES_PATH = ROOT / "data" / "authorities.json"
OUTPUTS_PATH = ROOT / "data" / "model_outputs.jsonl"
RESULTS_PATH = ROOT / "results" / "summary.json"


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def load_authorities():
    with AUTHORITIES_PATH.open("r", encoding="utf-8") as f:
        rows = json.load(f)
    by_id = {}
    for row in rows:
        canonical = row["label"]
        accepted = {normalize(canonical)}
        for alias in row.get("aliases", []):
            accepted.add(normalize(alias))
        by_id[row["id"]] = {
            "label": canonical,
            "accepted_names": accepted,
        }
    return by_id


def iter_outputs():
    with OUTPUTS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def evaluate():
    authorities = load_authorities()

    total_references = 0
    valid_references = 0
    non_resolving = 0
    high_severity = 0
    failure_modes = Counter()

    for sample in iter_outputs():
        for ref in sample.get("references", []):
            total_references += 1
            name = normalize(ref.get("name", ""))
            authority_id = ref.get("authority_id", "")

            if authority_id not in authorities:
                non_resolving += 1
                high_severity += 1
                failure_modes["invented_or_unknown_id"] += 1
                continue

            if name not in authorities[authority_id]["accepted_names"]:
                high_severity += 1
                failure_modes["entity_name_mismatch"] += 1
                continue

            valid_references += 1

    def pct(value):
        if total_references == 0:
            return 0.0
        return round((value / total_references) * 100, 2)

    summary = {
        "total_references": total_references,
        "valid_references": valid_references,
        "valid_rate_pct": pct(valid_references),
        "non_resolving_references": non_resolving,
        "non_resolving_rate_pct": pct(non_resolving),
        "high_severity_failures": high_severity,
        "high_severity_rate_pct": pct(high_severity),
        "top_failure_mode": failure_modes.most_common(1)[0][0] if failure_modes else "none",
        "failure_mode_counts": dict(failure_modes),
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    evaluate()
