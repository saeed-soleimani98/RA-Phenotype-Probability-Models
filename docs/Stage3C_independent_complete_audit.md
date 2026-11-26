# Independent Stage 3C Numerical, Methodological, and Publication Audit

**Audit date:** 2026-10-20  
**Primary materials audited:** full Stage 3C HTML report; all 19 Stage 3C result tables; repeated and patient-averaged OOF predictions; Stage 3B split assignments and reference predictions; predictor manifests; outcome-specific analytic datasets; exclusion rules; protocol; and environment metadata.

## Executive verdict

The Stage 3C results are **authentic, internally coherent, and numerically reproducible from the uploaded prediction files**. The exact Stage 3B outer splits were reused, every patient received the required ten out-of-fold predictions for every model, the analytic labels match the outcome-specific datasets, direct target components were excluded as specified, and all uploaded registered Stage 3C artifacts matched their recorded SHA-256 hashes.

There is no evidence of test-fold contamination, missing predictions, duplicate patient records, outcome-column leakage, use of prohibited sampling, or silent overwriting of Stage 3B. The uploaded evidence supports the technical claim that Stage 3C was run as a full 5-fold × 10-repeat nested benchmark.

The scientific interpretation remains deliberately narrower:

- **NoHandJointInvolvement:** a promising internal result. XGBoost provides a modest but reasonably consistent improvement over broad ridge in AUROC, log loss, and Brier score, with acceptable internal calibration.
- **NegRFandACCP:** no credible complex-model advantage. Broad ridge remains preferable on simplicity and average precision.
- **AsymmetricArthritis:** XGBoost provides small improvements in log loss and Brier score, but discrimination gains remain uncertain and the result is vulnerable to model-selection and multiplicity effects.

This is publishable as a **Stage 3B-led, internally validated study with a post hoc exploratory algorithm comparison**. It is not sufficient for clinical deployment or a claim that a selected complex model is externally validated.

## 1. Materials and environment

The uploaded environment records:

- Python 3.11.15
- NumPy 1.26.4
- pandas 2.2.3
- SciPy 1.13.1
- scikit-learn 1.9.0
- XGBoost 2.1.4
- Matplotlib 3.8.4
- seaborn 0.13.2

The frozen Stage 3 protocol prespecified Stage 3B common-core ridge as the confirmatory model and broad penalized models as exploratory. Stage 3C appropriately remains a later post hoc extension rather than a reinterpretation of the primary model.

## 2. Independent integrity checks

### OOF prediction structure

Independently verified:

- Repeated Stage 3C prediction rows: **221,400**, exactly `3 outcomes × 9 models × 820 patients × 10 repeats`.
- Patient-averaged prediction rows: **22,140**, exactly `3 × 9 × 820`.
- Every outcome/model combination contained exactly **820 unique patients**.
- Every patient/outcome/model combination had exactly **10 OOF predictions**.
- No duplicate outcome/model/patient/repeat rows were present.
- Every probability was finite and within [0,1].
- Outcome labels were invariant within patient and outcome.
- Averaged probabilities and across-repeat standard deviations reproduced from the repeated predictions to machine precision.

### Exact split reuse

Every one of the 221,400 Stage 3C prediction rows was merged back to the uploaded Stage 3B split assignment using outcome, VisitID, and repeat. There were:

- zero missing split matches;
- zero fold disagreements;
- 820 patients per outcome and repeat;
- exactly five folds per repeat.

This independently confirms use of the exact Stage 3B outer design.

### Analytic-data agreement

For all three outcomes:

- N=820 and VisitID was unique;
- the target contained no missing values;
- OOF patient IDs exactly matched the outcome-specific analytic dataset;
- every OOF label exactly matched the analytic target;
- no exact duplicate rows or feature-identical duplicate patients were detected.

### Predictor-manifest agreement

For every outcome, the columns in `__primary_eligible.csv` exactly equaled:

- `VisitID`;
- the relevant target;
- all and only variables labeled `primary_predictor` in its manifest.

Direct target components were absent:

- `NegRFandACCP`: anti-CCP and RF status excluded;
- `NoHandJointInvolvement`: DIP, hand PIP, MCP, and wrist involvement excluded;
- `AsymmetricArthritis`: joint-involvement pattern excluded.

Other study outcomes and `OnlyLargeJoints` were absent from the predictor matrices. `VisitID` was not declared a predictor. `OnlyLargeJoints` was absent from all Stage 3C modeling outputs.

### Artifact integrity

All **18 uploaded files that were listed in the Stage 3C artifact registry matched their recorded SHA-256 hashes exactly**. All seven uploaded Stage 3B registered artifacts also matched their Stage 3B hashes exactly.

This is strong evidence that the uploaded CSVs are the original run artifacts rather than subsequently edited summaries.

## 3. Independent numerical reproduction

### Point estimates

N, event counts, log loss, Brier score, calibration intercept, and calibration slope reproduced from the patient-averaged OOF predictions to machine precision.

All AUROC and average-precision values also reproduced except for a negligible rank-tie discrepancy for `NegRFandACCP` AdaBoost after CSV round-tripping:

- maximum AUROC difference: **0.0000558**;
- maximum AP difference: **0.0000075**.

AdaBoost produces many tied or nearly tied probabilities. Tiny floating-point differences can change tie handling for rank metrics while leaving log loss and Brier score unchanged. This has no substantive effect on any interpretation.

### Outer-fold metrics

All 1,350 outcome/model/fold metric records were independently recalculated. AUROC, AP, calibration intercept, and calibration slope reproduced to numerical precision. The largest discrepancies were:

- log loss: < **8.2 × 10⁻⁸**;
- Brier score: < **2.7 × 10⁻⁸**.

These occurred for XGBoost and are consistent with float32 prediction arithmetic versus CSV-read float64 arithmetic. They are scientifically irrelevant.

### Bootstrap intervals

The 2,000-resample stratified patient bootstrap was independently recreated for AUROC, AP, log loss, and Brier score using the recorded seeds. All intervals reproduced exactly to floating-point precision except AdaBoost rank-based intervals for `NegRFandACCP`, where the maximum endpoint difference was **0.000092** because of tied probabilities.

The paired Stage 3C-versus-Stage 3B broad-ridge AUROC and log-loss intervals were also independently recreated. The maximum endpoint discrepancy was < **0.000074**, again attributable to the AdaBoost tie case. Proper-scoring-rule comparisons reproduced essentially exactly.

### Paired point comparisons

All **276 saved paired point comparisons** were independently recalculated from matched patient predictions. The maximum difference was 0.0000558 and occurred only in the same AdaBoost/tie-sensitive AUROC comparison.

## 4. Independent performance conclusions

### NegRFandACCP

Events: 164/820 (20.0%).

| Model | AUROC | AP | Log loss | Brier |
|---|---:|---:|---:|---:|
| Refined broad ridge | 0.691 | 0.309 | 0.463 | 0.150 |
| Random forest | 0.693 | 0.291 | 0.458 | 0.149 |
| XGBoost | 0.676 | 0.293 | 0.467 | 0.151 |

Random forest versus Stage 3B broad ridge:

- AUROC: +0.0019 (−0.0192 to +0.0223)
- AP: −0.0181 (−0.0460 to +0.0052)
- log-loss improvement: +0.0047 (−0.0031 to +0.0123)
- Brier improvement: +0.0008 (−0.0020 to +0.0035)

No metric provides convincing evidence that random forest improves on broad ridge. XGBoost was numerically worse than broad ridge on all four principal metrics.

Random forest calibration also showed under-dispersion/underprediction: intercept 0.373 (95% CI −0.004 to 0.803), slope 1.327 (1.030 to 1.690). Broad ridge had better AP and more balanced calibration.

**Conclusion:** retain broad ridge as the exploratory broad candidate. A complex model is not justified here.

### NoHandJointInvolvement

Events: 191/820 (23.3%).

| Model | AUROC | AP | Log loss | Brier |
|---|---:|---:|---:|---:|
| Refined broad ridge | 0.774 | 0.484 | 0.457 | 0.149 |
| Random forest | 0.799 | 0.517 | 0.442 | 0.144 |
| XGBoost | 0.796 | 0.523 | 0.440 | 0.143 |

XGBoost versus Stage 3B broad ridge:

- AUROC: +0.0201 (+0.0028 to +0.0381)
- AP: +0.0367 (−0.0012 to +0.0755)
- log-loss improvement: +0.0162 (+0.0042 to +0.0285)
- Brier improvement: +0.0059 (+0.0012 to +0.0108)

Against the Stage 3C refined ridge, XGBoost improved all four metrics, although the AP lower limit was only +0.0003.

XGBoost calibration was acceptable internally:

- intercept 0.078 (−0.098 to 0.279);
- slope 1.075 (0.909 to 1.263).

Random forest had slightly higher AUROC but less favorable calibration: intercept 0.239 (0.026 to 0.471), slope 1.291 (1.075 to 1.518). XGBoost is therefore the more defensible nonlinear challenger when proper scoring rules and calibration are prioritized.

**Conclusion:** this is the strongest Stage 3C result. It is promising but remains an internally selected exploratory model.

### AsymmetricArthritis

Events: 190/820 (23.2%).

| Model | AUROC | AP | Log loss | Brier |
|---|---:|---:|---:|---:|
| Refined broad ridge | 0.657 | 0.354 | 0.514 | 0.168 |
| Random forest | 0.670 | 0.376 | 0.509 | 0.166 |
| XGBoost | 0.675 | 0.382 | 0.506 | 0.165 |

XGBoost versus Stage 3B broad ridge:

- AUROC: +0.0172 (−0.0037 to +0.0397)
- AP: +0.0264 (−0.0010 to +0.0564)
- log-loss improvement: +0.0076 (+0.00008 to +0.0155)
- Brier improvement: +0.0031 (+0.0003 to +0.0061)

XGBoost calibration was internally acceptable: intercept 0.066 (−0.265 to 0.408), slope 1.037 (0.748 to 1.338).

The result is weaker than it first appears. Discrimination intervals include no improvement, the log-loss lower limit is almost zero, many algorithm/metric comparisons were inspected, and fold performance was heterogeneous. XGBoost fold AUROC ranged 0.515–0.798 and fold log loss 0.472–0.606.

**Conclusion:** suggestive nonlinear signal, not a reliable winner. Broad ridge remains the more conservative candidate; XGBoost may be a locked secondary challenger in external validation.

## 5. Overfitting and model instability

### What was done well

- Hyperparameters were selected only in inner folds.
- Evaluation remained in untouched outer folds.
- Preprocessing was inside the outer pipeline.
- Models were tuned by log loss.
- Natural prevalence was retained.
- No SMOTE, undersampling, or class weights were used.
- Direct target components were excluded.
- Exact shared splits enabled paired evaluation.
- OOF calibration and proper scoring rules were assessed.

These choices substantially reduce ordinary training-set overfitting.

### Residual risks

#### 1. Broad-model information deficit

The broad sets contain 66–70 source predictors and approximately 95–99 encoded parameters, while the outcomes contain only 164–191 events. Stage 3A formally supported about nine parameters under its assumptions. Regularization reduces variance but does not remove this information deficit. Broad models therefore remain exploratory regardless of cross-validation quality.

#### 2. Model-family selection is outside the inner loop

Each family’s hyperparameters were nested correctly, but the family was chosen after comparing eight candidate families on the same OOF dataset. The performance of the retrospectively selected “best” family is therefore subject to winner’s optimism. This is especially relevant to the small XGBoost gains.

#### 3. Conditional bootstrap

The bootstrap resampled already generated OOF predictions. It did not rerun imputation, preprocessing, tuning, fitting, and family selection. The intervals correctly quantify patient-sampling variation conditional on the saved prediction procedure, but they do not include all development uncertainty.

#### 4. Inner train-test gaps

Median inner log-loss generalization gaps were substantially larger for complex models:

- random forest: roughly −0.12 to −0.17;
- XGBoost: roughly −0.04 to −0.11;
- RBF SVC: roughly −0.20 to −0.29;
- broad ridge: roughly −0.04 to −0.05.

The negative sign reflects worse inner-validation than inner-training performance. This is direct evidence that the complex families fit training data much more aggressively. Outer evaluation controls the reported performance bias, but it reinforces concern about transportability.

#### 5. Patient-level prediction instability

Across-repeat probability variability was highest for XGBoost and RBF SVC. For XGBoost:

- NegRFandACCP: mean SD 0.038, maximum 0.110;
- NoHandJointInvolvement: mean SD 0.050, maximum 0.155;
- AsymmetricArthritis: mean SD 0.047, maximum 0.136.

Broad ridge was more stable, with mean SDs around 0.023–0.030. This means some individual risk estimates changed materially depending on which training folds were used, even when aggregate metrics were acceptable.

#### 6. Hyperparameter instability

XGBoost’s exact selected parameter vector was almost always unique across the 50 outer fits. This partly reflects sampling a different randomized candidate set in each fold, but it also means there is no single clearly dominant configuration. Selected learning rates, depths, regularization, and subsampling varied widely.

RBF SVC showed a boundary pattern for NegRFandACCP: gamma=0.1 was selected in 47/50 outer fits. The model was nevertheless inferior, so widening that grid would amount to further post hoc tuning without a strong scientific rationale.

#### 7. Convergence audit scope

All 1,200 saved convergence records were marked successful. This is reassuring, but the generic diagnostic cannot deeply inspect every internal estimator inside `CalibratedClassifierCV`, random forest, or XGBoost. Complete predictions, absence of recorded failures, and stable proper-score calculations provide additional practical assurance, but “all convergence diagnostics passed” should not be interpreted as a mathematical guarantee for every internal fit.

## 6. Semantic leakage and outcome proximity

No direct target component was present, and a univariate screen found no low-cardinality predictor that deterministically reconstructed any target.

Highest oriented single-predictor AUROCs were:

- NegRFandACCP: RA duration, approximately 0.616;
- NoHandJointInvolvement: 28-joint tender count, approximately 0.705;
- AsymmetricArthritis: initial soft-tissue presentation, approximately 0.597.

Thus, there is no evidence of a hidden exact label proxy. However, `NoHandJointInvolvement` depends strongly on joint-count and anatomy variables: 28-joint tender count was the dominant permutation feature for ridge, random forest, and XGBoost, with positive importance in all 50 outer folds. Its strength may be clinically legitimate, but it also makes the intended prediction time and use case essential.

A publication should distinguish:

- predicting the phenotype before a detailed joint examination;
- classifying the phenotype using the same contemporaneous examination;
- predicting a future phenotype.

The current design supports contemporaneous classification most directly. It should not be described as future prognosis unless predictor timing establishes that interpretation.

## 7. Prevalence-null technical note

The pooled prevalence-null AUROC was slightly below 0.5 for outcomes whose event counts were not evenly divisible across five stratified folds. Each test-fold probability used its corresponding training-fold prevalence. Small differences in fold event counts can therefore produce a weak inverse rank association when pooled. This is an expected OOF-fold artifact, not evidence that the null model contains information. Proper scoring rules remain the more meaningful null comparison.

## 8. Publication-readiness judgment

### Publishable claims

The project can support a manuscript stating that:

1. Stage 3B common-core ridge was the prespecified internally validated primary analysis.
2. Broad predictor models improved on the parsimonious core but exceeded formal event-supported complexity.
3. Complex ML did not consistently outperform broad regularized regression.
4. XGBoost provided a modest exploratory gain for NoHandJointInvolvement.
5. Complex-model gains were absent for NegRFandACCP and fragile for AsymmetricArthritis.
6. All results require external validation before clinical use.

### Claims that are not supported

Do not claim:

- that XGBoost is definitively superior;
- that the models are externally validated;
- that AUROC around 0.80 proves clinical usefulness;
- that permutation importance identifies causal disease mechanisms;
- that a clinical threshold has been validated;
- that the model is ready for bedside use;
- that Stage 3C replaces the Stage 3B primary result.

### Likely risk-of-bias assessment

- Participants/data integrity: low-to-moderate concern based on uploaded data.
- Direct target leakage: low concern.
- Internal evaluation: low concern for ordinary tuning bias.
- Broad-model development quality: moderate-to-high concern because of sample-size deficit and family selection.
- Applicability/transportability: high concern until the intended use and external setting are defined.
- Overall broad-model PROBAST+AI judgment: unlikely to be low risk without external evaluation and resolution of development-complexity concerns.

## 9. Required next steps

### Step 1 — Freeze this cohort

Do not test more algorithms, seeds, or tuning grids on these outcomes. The current evidence is sufficient. Additional searches would increase winner’s optimism.

### Step 2 — Perform two locked semantic sensitivity analyses

Using the same splits and no model reselection:

1. `NoHandJointInvolvement`: remove joint counts, grip strength, and all joint-anatomy variables; compare locked broad ridge and locked XGBoost.
2. `AsymmetricArthritis`: remove joint counts and joint-anatomy/pattern-related variables; compare locked broad ridge and locked XGBoost.

These analyses answer whether performance reflects general clinical information or contemporaneous reconstruction of the phenotype. They must be labeled post hoc sensitivity analyses.

### Step 3 — Define the final model recipes

The fold checkpoints are validation fits, not one deployable model. Before external data are inspected, lock:

- common-core ridge for all primary external validations;
- broad ridge for NegRFandACCP;
- XGBoost plus broad ridge for NoHandJointInvolvement;
- broad ridge as the stable AsymmetricArthritis challenger, with XGBoost secondary.

Specify how full-data hyperparameters will be selected and how missing values/categories will be handled.

### Step 4 — External validation

Obtain a temporally, geographically, or institutionally distinct RA cohort. Prespecify predictor mapping and outcome reconstruction before examining results. Use a formal external-validation sample-size calculation.

Report:

- calibration-in-the-large and calibration slope with intervals;
- calibration curves;
- AUROC and AP;
- log loss and Brier score;
- site/time heterogeneity;
- missingness and subgroup performance.

Recalibration should occur only after reporting the original locked model’s external performance.

### Step 5 — Publication package

- Follow TRIPOD+AI.
- Complete a PROBAST+AI self-assessment.
- Include the frozen Stage 3 protocol and clearly date Stage 3C as post hoc.
- Include participant flow, missingness, outcome definitions, predictor timing, and a complete model card.
- Share code, environment, split assignments, manifests, and OOF predictions where permitted.
- Lead with calibration and proper scoring rules, not accuracy alone.

## 10. Final conclusion

The uploaded Stage 3C results pass a detailed independent numerical and integrity audit. Small reproduction discrepancies are limited to floating-point and tied-rank effects below 0.0001 and do not alter any conclusion.

The results are good enough for publication as rigorous internal validation with an exploratory benchmark. They are not good enough for deployment. NoHandJointInvolvement is the only outcome with a credible complex-model increment, and even there the gain is modest, the selected model is internally chosen, and individual predictions show meaningful training-split variability. External validation—not more tuning on the current cohort—is now the scientifically correct next step.
