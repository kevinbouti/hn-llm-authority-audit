# Show HN: LLM Authority Citation Audit

Public landing page for a high-impact Hacker News launch.

## Claim

We evaluated LLM outputs against authority-oriented references and measured citation reliability failures at reproducible scale.

## Why it matters

If citations and authority references are wrong, trust collapses in research, compliance, and knowledge workflows.

## Scope

- Citation validity across sampled outputs
- Reference resolution success (authority IDs / linked references)
- Hallucination categories (invented identifiers, mismatched entities)
- Severity and downstream risk

## Method

1. Build a benchmark set of authority-linked records.
2. Generate model outputs with fixed prompts.
3. Validate references against authoritative targets.
4. Score outputs with deterministic rules.
5. Publish scripts, schema, and reproducibility instructions.

## Results (replace with your numbers)

- Valid citation rate: **XX.X%**
- Non-resolving references: **YY.Y%**
- High-severity hallucinations: **ZZ.Z%**
- Most frequent failure mode: **<mode>**

## Reproducibility

- Code: `<repo-url>`
- Data schema: `<schema-url>`
- Evaluation script: `<script-url>`
- Repro guide: `<repro-url>`

## Limits

- Current focus is authority/citation-style references.
- Results vary by model, prompt, and decoding configuration.
- This is not a full factuality benchmark; it isolates reference reliability.

## Ready-to-post HN title

`Show HN: We measured LLM authority citation errors on real records`

## Ready-to-post first comment

Happy to share raw failure cases and evaluation scripts in-thread.  
If useful, I can also publish a model-by-model breakdown and a stricter validator profile.
