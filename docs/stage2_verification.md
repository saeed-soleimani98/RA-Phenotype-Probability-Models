# Stage 2 Verification

**Reviewed file:** `Stage2_cleaning_preprocessing_report.html`  
**Status:** PASS — Stage 2 is complete.

## Execution integrity

- HTML contains no execution error or traceback.
- Source path resolved to `the authorized RA_PROJECT_DIR\Atypical_presentations_RA_predictors_valid_c_exclusions_final_population.csv`.
- Source SHA-256: `7a7e0edc576370e0853fd70dc4cc2841507ccf4d95bd53e36d08f0bc782b9ca8`.
- Source shape remained 820 rows × 95 columns.
- `VisitID` remained complete and unique.
- No exact duplicate rows were detected.
- The source checksum remained unchanged after processing.

## Cleaning verification

The six investigator-agreed corrections are applied by the authorized local
correction specification; identifiers and individual values are withheld.

`MeanGripStrength` was created after these corrections. The cleaned master dataset contains 820 rows and 96 columns because the derived grip feature was added.

## Outcome-specific datasets

| Outcome | Rows | Positive | Negative | Primary predictors | Expanded predictors |
|---|---:|---:|---:|---:|---:|
| NegRFandACCP | 820 | 164 | 656 | 68 | 75 |
| NoHandJointInvolvement | 820 | 191 | 629 | 66 | 75 |
| AsymmetricArthritis | 820 | 190 | 630 | 70 | 75 |

`OnlyLargeJoints` is absent from retained outcomes and all predictor matrices.

## Safety checks

All 35 automated checks passed, including:

- no forbidden primary predictors;
- target not used as its own predictor;
- other outcomes excluded;
- target-specific leakage variables excluded;
- TyG retained as the documented missingness exception;
- MeanGripStrength retained;
- Opium retained while IllicitDrug is excluded;
- primary and expanded datasets created;
- complete manifests created;
- preprocessing factory created but not fitted to the complete dataset.

## Preprocessing status

The notebook correctly defines, but does not globally fit:

- numeric median imputation with missingness indicators and scaling;
- binary most-frequent imputation with missingness indicators;
- categorical Unknown handling and one-hot encoding;
- safe handling of unseen categories.

These operations are ready to be placed inside future cross-validation pipelines.

## Remaining decisions before model fitting

1. Primary model family and comparator hierarchy.
2. Hyperparameter grids.
3. Exact primary metric used for tuning.
4. Probability-threshold policy.
5. Calibration procedure.
6. Final out-of-fold SHAP and stability protocol.
7. Bootstrap confidence-interval settings.
8. Multiple-comparison/reporting policy across three outcomes.

No model should be fitted until these choices are frozen in a versioned modeling protocol.
