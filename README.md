# Show HN: LLM Authority Citation Audit v2

A runnable benchmark to measure whether LLM-generated authority references are valid, resolvable, and entity-consistent.

## Why this exists

Most citation-hallucination discussions are anecdotal. This repository turns the problem into reproducible metrics with explicit failure classes and per-model breakdowns.

## What's inside

- `data/authorities.json` -> authority records (canonical labels + aliases)
- `data/model_outputs.jsonl` -> model outputs to evaluate
- `scripts/evaluate.py` -> deterministic evaluator
- `results/summary.json` -> global metrics + model ranking
- `results/per_model.json` -> per-model metrics
- `results/errors.csv` -> row-level failures (ready for analysis)

## Current benchmark results (real run)

Run command:

`python3 scripts/evaluate.py`

Global:

- Valid citation rate: **75.00%** (18/24)
- Non-resolving references: **16.67%** (4/24)
- High-severity failures: **25.00%** (6/24)
- Top failure mode: **invented_or_unknown_id**

Model ranking by valid rate:

1. `model-alpha` -> **100.0%** valid, **0.0%** high severity
2. `model-beta` -> **62.5%** valid, **37.5%** high severity
3. `model-gamma` -> **62.5%** valid, **37.5%** high severity

## Scoring rules

Each reference is classified with deterministic logic:

1. Unknown authority ID -> `invented_or_unknown_id` (high severity)
2. Known ID but wrong entity name -> `entity_name_mismatch` (high severity)
3. Known ID + accepted canonical/alias name -> valid

## Run locally

```bash
python3 scripts/evaluate.py
cat results/summary.json
cat results/per_model.json
cat results/errors.csv
```

## Data format

Each JSONL sample in `data/model_outputs.jsonl` contains:

- `sample_id`
- `model`
- `prompt`
- `references`: list of `{ "name": "...", "authority_id": "..." }`

## How to adapt to your own model outputs

1. Replace or append rows in `data/model_outputs.jsonl`
2. Extend `data/authorities.json` with your target entity set
3. Re-run evaluator
4. Compare `results/per_model.json` and inspect `results/errors.csv`

## Limits

- This benchmark isolates authority-reference reliability only.
- It does not evaluate full answer factuality, reasoning quality, or citation completeness.
- Included data is intentionally compact for transparency and fast iteration.

## HN launch package

Suggested title:

`Show HN: LLMs invent authority IDs — reproducible benchmark + error-level outputs`

Suggested first comment:

Small but fully inspectable benchmark: deterministic evaluator, per-model metrics, and row-level error CSV are included.  
If useful, I can expand to a larger multilingual dataset and add stricter normalization profiles.
