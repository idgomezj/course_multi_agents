# Case 0 — Worked imperfect-data walkthrough

Case 0 exposes a small imperfect raw-data sample through:

```text
GET /v1/teams/team_0/training-source.json
```

The sample exists to demonstrate the **analysis process**. The committed 3,000-row supervised CSVs remain the deterministic reference-model inputs so the instructor demo stays reproducible.

## What is intentionally wrong in the sample

The sample contains examples of:

- missing feature values;
- duplicate uploads;
- whitespace/case inconsistencies in identifiers;
- manual correction notes;
- a suspiciously large volatility observation;
- a suspicious supplier lead-time observation;
- multiple source systems.

The correct response is not "drop every unusual row."

## Worked review decisions

### 1. Normalize identifiers

Trim surrounding whitespace and normalize controlled identifiers such as supplier/source labels before grouping or duplicate detection.

### 2. Duplicate uploads

When two rows have identical model evidence/outcome values and one is explicitly marked as a duplicate upload, keep one canonical observation.

### 3. Missing values

Do not invent future outcomes. For a missing input feature, either use a defensible training-time imputation based only on information available at that point or exclude the affected example and document the choice.

Case 0 keeps the final reference datasets clean so the training pipeline itself is deterministic.

### 4. Suspicious extremes

A large value is not automatically corrupt. Investigate whether surrounding business evidence supports it. The Case 0 sample deliberately includes extremes so students see that outlier handling requires a reason, not a magic z-score rule.

### 5. Leakage

Targets/outcomes remain targets. They are never used as inputs for the same prediction.

### 6. Reproducible result

After the worked review, the instructor uses the committed clean files:

```text
model_a_training.csv
model_b_training.csv
```

This separation is intentional:

```text
imperfect sample -> demonstrate analysis decisions
clean committed reference CSVs -> deterministic platform validation
```

Teams 1–5 must perform the corresponding analysis on their own team-specific raw evidence and produce their own supervised CSVs.
