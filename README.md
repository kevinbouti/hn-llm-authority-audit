# Show HN: LLM Authority Citation Audit

A small but fully runnable benchmark that measures whether LLM-generated authority references are valid and resolvable.

## Why this exists

Citation reliability is often discussed with anecdotes. This repo gives a reproducible baseline with explicit failure categories.

## What is included

- `data/authorities.json`: authority records (canonical labels + aliases)
- `data/model_outputs.jsonl`: model-produced references to evaluate
- `scripts/evaluate.py`: deterministic evaluator
- `results/summary.json`: generated metrics

## Current results (real run)

Computed with:

`python3 scripts/evaluate.py`

- Valid citation rate: **57.14%** (4/7)
- Non-resolving references: **28.57%** (2/7)
- High-severity failures: **42.86%** (3/7)
- Top failure mode: **invented_or_unknown_id**

## Evaluation logic

Each reference is scored with deterministic rules:

1. **Unknown authority ID** -> `invented_or_unknown_id` (high severity)
2. **Known ID but wrong entity name** -> `entity_name_mismatch` (high severity)
3. **Known ID + accepted canonical/alias name** -> valid

## Run locally

```bash
python3 scripts/evaluate.py
cat results/summary.json
```

## Extend this benchmark

- Swap `data/model_outputs.jsonl` with your own outputs
- Add records to `data/authorities.json`
- Compare multiple models by adding a `model` field per sample

## Limits

- This is a minimal reference-reliability benchmark, not full factuality evaluation.
- The included dataset is intentionally small for transparent inspection.

## HN post package

Suggested title:

`Show HN: We built a reproducible audit for LLM authority citation failures`

Suggested first comment:

This repo is intentionally small and fully inspectable.  
If there is interest, I can publish a larger multilingual dataset and per-model breakdown.
