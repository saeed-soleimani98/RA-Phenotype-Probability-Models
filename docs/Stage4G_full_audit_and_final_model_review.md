# Stage 4G Full Audit and Final-Model Review

## Verdict

The full Stage 4G execution is valid at the report and tabular level and has produced the intended eight-model research package.

- Full mode is confirmed.
- The notebook audit passed 30/30 checks.
- The independent tabular audit passed 22/22 checks.
- Eight final model records were created from all 820 development patients.
- The primary/secondary/exploratory hierarchy was preserved.
- All selected candidates satisfy the frozen one-standard-error rules.
- Selected registry hyperparameters exactly match the tuning records.
- All in-process serialization/reload tests passed exactly.
- All fresh-process command-line prediction tests passed within 1×10⁻⁸; the maximum difference was 9.12×10⁻¹⁰.
- Prior OOF performance references exactly match the immutable Stage 3B and Stage 3C tables.
- Eleven available uploaded artifact-registry entries matched their SHA-256 hashes.
- No apparent full-cohort performance was calculated or presented as validation evidence.
- The report contains no traceback.

The actual pipeline binaries, metadata files, and model cards were not included in the current upload. Their existence and reload behavior are documented by the report and internal checks, but independent binary deserialization and file-level inspection require the uniquely named files from `modeling_results_stage4g/audit_upload`.

## Final model registry

### Primary models

| Outcome | Model | Raw predictors | Transformed features | Final C |
|---|---|---:|---:|---:|
| NegRFandACCP | Core ridge | 7 | 9 | 0.046416 |
| NoHandJointInvolvement | Core ridge | 7 | 9 | 0.046416 |
| AsymmetricArthritis | Core ridge | 7 | 9 | 0.002154 |

These are the prespecified primary models. The very small final C for AsymmetricArthritis reflects the one-standard-error preference for strong regularization and is consistent with the weak common-core signal.

### Secondary broad ridge models

| Outcome | Raw predictors | Transformed features | Final C |
|---|---:|---:|---:|
| NegRFandACCP | 68 | 96 | 0.013921 |
| NoHandJointInvolvement | 66 | 95 | 0.029988 |
| AsymmetricArthritis | 70 | 99 | 0.023220 |

All three selected C values are deliberately more regularized than the minimum-loss candidate when permitted by the one-standard-error rule. This is appropriate for final transportable artifacts given the sample size and broad feature counts.

### Exploratory XGBoost challengers

**NoHandJointInvolvement**

- depth 2
- learning rate 0.05
- 300 trees
- minimum child weight 10
- subsample 0.85
- column sample 0.75
- L1 regularization 1
- L2 regularization 10

**AsymmetricArthritis**

- depth 2
- learning rate 0.03
- 600 trees
- minimum child weight 10
- subsample 0.85
- column sample 0.50
- L1 regularization 0.1
- L2 regularization 10

Both are shallow, regularized configurations. They remain exploratory challengers and do not replace the Stage 3B primary models.

## Hyperparameter-selection audit

The final tuning file contains exactly 202 candidates:

- 13 candidates for each of three core ridge models;
- 21 candidates for each of three broad ridge models;
- 50 candidates for each of two XGBoost models.

Each model has exactly one selected candidate, every selected candidate lies within one standard error of the minimum mean repeated-CV log loss, every ridge selection is the smallest eligible C, and both XGBoost selections reproduce the frozen deterministic simplicity ordering.

The final-tuning CV values are used only to select full-cohort artifact hyperparameters. They are not unbiased performance estimates and should not appear in the manuscript as model performance.

## OOF evidence retained correctly

The final package references, but does not recompute, the prior repeated nested OOF estimates:

| Outcome | Model | AUROC | AP | Log loss | Brier |
|---|---|---:|---:|---:|---:|
| NegRFandACCP | Core ridge, primary | 0.613 | 0.244 | 0.488 | 0.157 |
| NegRFandACCP | Broad ridge, secondary | 0.691 | 0.309 | 0.463 | 0.150 |
| NoHandJointInvolvement | Core ridge, primary | 0.718 | 0.383 | 0.492 | 0.162 |
| NoHandJointInvolvement | Broad ridge, secondary | 0.774 | 0.484 | 0.457 | 0.149 |
| NoHandJointInvolvement | XGBoost, exploratory | 0.796 | 0.523 | 0.440 | 0.143 |
| AsymmetricArthritis | Core ridge, primary | 0.567 | 0.287 | 0.539 | 0.177 |
| AsymmetricArthritis | Broad ridge, secondary | 0.657 | 0.354 | 0.514 | 0.168 |
| AsymmetricArthritis | XGBoost, exploratory | 0.675 | 0.382 | 0.506 | 0.165 |

These values match the original Stage 3B/3C tables exactly. The nested selector and semantic-removal analyses remain necessary context when interpreting the exploratory XGBoost values.

## Scientific interpretation

1. **Primary status is methodological, not rank-based.** The core ridge models remain primary because they were prespecified and supportable under the formal complexity assessment. Their lower apparent predictive performance does not permit retrospective replacement.
2. **Broad ridge provides the most defensible secondary model for NegRFandACCP.** The family selector did not improve performance and worsened AP.
3. **NoHand XGBoost is a credible exploratory challenger, not a universal winner.** Its modest gain survived nested selection, but performance depends strongly on contemporaneous joint/anatomy variables.
4. **Asymmetric XGBoost remains secondary and fragile.** The nested selector did not show a conclusive advantage, and its nonlinear gain weakened after joint/anatomy removal.
5. **The artifacts are not deployable clinical devices.** They are research-use final development models awaiting external validation, recalibration assessment, threshold definition, and clinical-impact evaluation.

## Remaining artifact-level verification

For a fully independent portability audit, provide the uniquely named files from `modeling_results_stage4g/audit_upload`:

- eight `__pipeline.joblib` files;
- eight `__metadata.json` files;
- eight `__MODEL_CARD.md` files.

The tuning CSVs are already consolidated in the uploaded table and need not be uploaded again unless desired. With the binaries and component module, an independent environment can reload each pipeline, inspect feature schemas, reproduce synthetic predictions, and verify each binary checksum.

## Stage completion

Stage 4G is scientifically complete. Binary-level independent verification is the only optional final technical check. No additional model development should occur.

The next substantive stage is Stage 4H: manuscript and reporting-package assembly.
