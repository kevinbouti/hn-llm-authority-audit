#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITIES_PATH = ROOT / "data" / "authorities.json"
OUTPUTS_PATH = ROOT / "data" / "model_outputs.jsonl"
RESULTS_PATH = ROOT / "results" / "summary.json"
PER_MODEL_PATH = ROOT / "results" / "per_model.json"
ERRORS_CSV_PATH = ROOT / "results" / "errors.csv"


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


def make_stats():
    return {
        "total_references": 0,
        "valid_references": 0,
        "non_resolving_references": 0,
        "high_severity_failures": 0,
        "failure_modes": Counter(),
    }


def apply_reference(stats, authorities, sample_id, model, prompt, ref):
    stats["total_references"] += 1
    name = normalize(ref.get("name", ""))
    authority_id = ref.get("authority_id", "")
    error_row = None

    if authority_id not in authorities:
        stats["non_resolving_references"] += 1
        stats["high_severity_failures"] += 1
        stats["failure_modes"]["invented_or_unknown_id"] += 1
        error_row = {
            "sample_id": sample_id,
            "model": model,
            "prompt": prompt,
            "name": ref.get("name", ""),
            "authority_id": authority_id,
            "failure_mode": "invented_or_unknown_id",
            "severity": "high",
        }
        return error_row

    if name not in authorities[authority_id]["accepted_names"]:
        stats["high_severity_failures"] += 1
        stats["failure_modes"]["entity_name_mismatch"] += 1
        error_row = {
            "sample_id": sample_id,
            "model": model,
            "prompt": prompt,
            "name": ref.get("name", ""),
            "authority_id": authority_id,
            "failure_mode": "entity_name_mismatch",
            "severity": "high",
        }
        return error_row

    stats["valid_references"] += 1
    return error_row


def finalize_stats(stats):
    total_references = 0
    valid_references = stats["valid_references"]
    non_resolving = stats["non_resolving_references"]
    high_severity = stats["high_severity_failures"]
    failure_modes = stats["failure_modes"]
    total_references = stats["total_references"]

    def pct(value):
        if total_references == 0:
            return 0.0
        return round((value / total_references) * 100, 2)

    return {
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


def evaluate():
    authorities = load_authorities()
    global_stats = make_stats()
    per_model_stats = defaultdict(make_stats)
    error_rows = []

    for sample in iter_outputs():
        sample_id = sample.get("sample_id", "")
        model = sample.get("model", "unknown-model")
        prompt = sample.get("prompt", "")
        for ref in sample.get("references", []):
            err = apply_reference(global_stats, authorities, sample_id, model, prompt, ref)
            apply_reference(per_model_stats[model], authorities, sample_id, model, prompt, ref)
            if err:
                error_rows.append(err)

    summary = finalize_stats(global_stats)
    per_model = {model: finalize_stats(stats) for model, stats in per_model_stats.items()}
    ranked_models = sorted(
        (
            {
                "model": model,
                "valid_rate_pct": stats["valid_rate_pct"],
                "high_severity_rate_pct": stats["high_severity_rate_pct"],
            }
            for model, stats in per_model.items()
        ),
        key=lambda x: (-x["valid_rate_pct"], x["high_severity_rate_pct"], x["model"]),
    )
    summary["model_ranking"] = ranked_models

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    with PER_MODEL_PATH.open("w", encoding="utf-8") as f:
        json.dump(per_model, f, indent=2)
    with ERRORS_CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["sample_id", "model", "prompt", "name", "authority_id", "failure_mode", "severity"],
        )
        writer.writeheader()
        writer.writerows(error_rows)

    output = {
        "summary": summary,
        "per_model": per_model,
        "errors_csv": str(ERRORS_CSV_PATH.relative_to(ROOT)),
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    evaluate()
