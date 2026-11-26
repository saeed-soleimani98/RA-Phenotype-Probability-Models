# Stage 3B Full Scientific Review

**Reviewed artifact:** `Stage3B_modeling_validation_report.html`  
**Execution represented in report:** full scientific mode; Python 3.11.15; scikit-learn 1.9.0; Windows local execution; 5-fold outer CV × 10 repetitions; 5-fold inner CV; 2,000 patient-level bootstrap resamples.

## Executive conclusion

The report is technically complete and internally coherent. All 20 prespecified software and protocol audits passed, all three outcomes and four prespecified models completed, every patient received the expected repeated out-of-fold predictions, and no external-validation, causal, threshold-selection, or net-benefit claim was made.

The prespecified **common-core ridge model remains the confirmatory analysis**. Its usefulness differs materially by outcome:

- **NoHandJointInvolvement:** moderate internal discrimination with good apparent calibration; the strongest confirmatory result.
- **NegRFandACCP:** weak-to-modest discrimination, with calibration close to ideal but only a small gain over prevalence-only prediction.
- **AsymmetricArthritis:** weak discrimination and almost no improvement over prevalence-only prediction; the common core is inadequate for useful prediction of this outcome.

The exploratory broad ridge and elastic-net models improved discrimination and overall prediction error for all three outcomes. Broad ridge was marginally best numerically in each outcome, but ridge and elastic net were very similar. These broad results are hypothesis-generating, not confirmatory, because Stage 3A showed that their approximately 95–99 effective parameters are not supported by N=820 and 164–191 events. They require external validation and likely predictor reduction or a larger development sample before clinical use.

## Integrity and reproducibility audit

### Strengths

- Full rather than quick mode was used.
- The report records 820 patients for every outcome-model combination.
- Outcomes were modeled separately: `NegRFandACCP`, `NoHandJointInvolvement`, and `AsymmetricArthritis`.
- `OnlyLargeJoints` was not modeled.
- Repeated nested stratified CV was used: outer 5-fold × 10 repetitions, inner 5-fold.
- Hyperparameters were tuned by log loss.
- Preprocessing was fitted within training folds.
- Performance predictions and SHAP values were generated out of fold.
- Comparisons used identical outer splits and paired patient-level differences.
- Natural outcome prevalence was retained; there was no SMOTE, undersampling, or class weighting.
- No primary decision threshold was selected without a clinical action/cost specification.
- No decision-curve or net-benefit claim was made without a defined clinical decision.
- All 20 final audit checks passed.
- Broad-model tuning did not show systematic grid-boundary problems. Only the AsymmetricArthritis core ridge model had a small boundary-hit fraction (0.06), which does not indicate a pervasive tuning-grid failure.

### Important limitations

1. **Internal validation only.** The results estimate performance in data similar to the development population. Transportability is unknown.
2. **Broad-model sample-size deficit.** Penalization reduces overfitting but does not make the broad analyses confirmatory or erase the formal sample-size shortfall.
3. **Contemporaneous predictors.** Some broad predictors may be close clinical proxies for the outcomes. Their performance is appropriate only as the prespecified broader contemporaneous sensitivity analysis, not automatically as an early prognostic model.
4. **Bootstrap scope.** The patient bootstrap operates on already-generated averaged OOF predictions. It quantifies patient-sampling uncertainty conditional on the fitted repeated-CV procedure, but does not fully rerun model development and tuning in every bootstrap sample.
5. **Calibration uncertainty.** Calibration intercept and slope are much less precisely estimated than discrimination and prediction-error metrics, particularly for the weak AsymmetricArthritis core models.
6. **Explainability is not causality.** SHAP importance describes contribution to these fitted prediction models. It does not establish etiologic, mechanistic, or treatment effects.

## Outcome-specific findings

### 1. NegRFandACCP

Prevalence was **20.0%** (164/820). A prevalence-only model has approximate log loss 0.5004 and Brier score 0.1600.

#### Confirmatory common-core ridge

- AUROC: **0.613** (95% CI 0.571–0.657)
- Average precision: **0.244** (0.221–0.284), versus prevalence 0.200
- Log loss: **0.488** (0.479–0.497)
- Brier score: **0.157** (0.154–0.160)
- Calibration intercept: **0.024** (−0.488 to 0.597)
- Calibration slope: **1.019** (0.645–1.449)

Interpretation: discrimination is weak-to-modest. Calibration point estimates are close to ideal, but uncertainty is substantial. Improvement over prevalence-only prediction is small.

Ordinary core logistic regression did not improve performance over ridge. Its slope estimate was lower (0.707), supporting retention of ridge as the prespecified confirmatory model.

#### Exploratory broad models

Broad ridge achieved AUROC **0.691**, average precision **0.309**, log loss **0.463**, and Brier **0.150**. Compared with core ridge, paired improvements were:

- AUROC: **+0.0778** (0.0364 to 0.1210)
- Average precision: **+0.0655** (0.0250 to 0.1140)
- Log-loss reduction: **0.0249** (0.0117 to 0.0384)
- Brier reduction: **0.0069** (0.0026 to 0.0115)

Broad elastic net was very similar but slightly weaker numerically. Broad ridge calibration was close to ideal: intercept 0.022 and slope 1.014.

#### Explainability

The most stable high-importance core feature was RA duration, followed by tender and swollen joint counts, patient global assessment, and age. In broad models, RA duration and TyG were the two most consistently high-ranked variables; vitamin D deficiency, constitutional symptoms, tender/swollen joint counts, and cardiovascular symptoms followed. These are predictive associations only.

### 2. NoHandJointInvolvement

Prevalence was **23.3%** (191/820). A prevalence-only model has approximate log loss 0.5428 and Brier score 0.1787.

#### Confirmatory common-core ridge

- AUROC: **0.718** (95% CI 0.677–0.757)
- Average precision: **0.383** (0.341–0.444), versus prevalence 0.233
- Log loss: **0.492** (0.472–0.512)
- Brier score: **0.162** (0.155–0.170)
- Calibration intercept: **−0.015** (−0.246 to 0.249)
- Calibration slope: **0.988** (0.780–1.232)

Interpretation: this is the strongest confirmatory model. It has moderate discrimination, a meaningful average-precision gain over prevalence, improved proper scoring rules relative to prevalence-only prediction, and calibration point estimates close to ideal.

Ordinary core logistic regression was not superior to ridge.

#### Exploratory broad models

Broad ridge achieved AUROC **0.776**, average precision **0.486**, log loss **0.456**, and Brier **0.149**. Compared with core ridge, paired improvements were:

- AUROC: **+0.0584** (0.0291 to 0.0865)
- Average precision: **+0.1033** (0.0462 to 0.1537)
- Log-loss reduction: **0.0358** (0.0190 to 0.0523)
- Brier reduction: **0.0136** (0.0072 to 0.0197)

Calibration remained acceptable, although the broad-ridge slope of 1.138 may indicate slight under-dispersion of predictions; its CI included 1. Broad elastic net was again close but slightly weaker.

#### Explainability

Tender-joint count was dominant and exceptionally stable in both core and broad models. In the core model, abnormal CRP/ESR and RA duration followed. Broad-model high-importance variables included grip strength, sacroiliac involvement, swollen-joint count, knee and ankle involvement, and constitutional symptoms. Because the outcome concerns absence of hand involvement, anatomical and joint-count predictors require careful clinical interpretation and assessment for definitional proximity before deployment.

### 3. AsymmetricArthritis

Prevalence was **23.2%** (190/820). A prevalence-only model has approximate log loss 0.5413 and Brier score 0.1780.

#### Confirmatory common-core ridge

- AUROC: **0.567** (95% CI 0.518–0.613)
- Average precision: **0.287** (0.254–0.338), versus prevalence 0.232
- Log loss: **0.539** (0.534–0.545)
- Brier score: **0.177** (0.175–0.179)
- Calibration intercept: **−0.104** (−1.264 to 1.139)
- Calibration slope: **0.913** (−0.054 to 1.962)

Interpretation: discrimination is weak and proper scoring rules are nearly identical to prevalence-only prediction. The common core does not provide convincing predictive utility for this outcome.

The ordinary core logistic model was not superior and had unstable calibration estimation: intercept −1.015 with a numerically extreme lower confidence limit, and slope 0.149 with wide uncertainty. This supports avoiding unpenalized estimation here.

#### Exploratory broad models

Broad ridge achieved AUROC **0.658**, average precision **0.355**, log loss **0.514**, and Brier **0.168**. Compared with core ridge, paired improvements were:

- AUROC: **+0.0911** (0.0431 to 0.1376)
- Average precision: **+0.0681** (0.0156 to 0.1209)
- Log-loss reduction: **0.0252** (0.0112 to 0.0390)
- Brier reduction: **0.0089** (0.0035 to 0.0142)

Broad ridge calibration was close to ideal: intercept −0.013 and slope 0.984. Broad elastic net produced nearly identical results.

#### Explainability

Tender-joint count was the most stable broad-model feature. Initial soft-tissue presentation, elbow involvement, rheumatoid-factor positivity, grip strength, and vitamin D deficiency were also highly ranked. In the core model, RA duration and tender-joint count ranked highest. These broad associations should be treated as exploratory and checked for clinical plausibility, measurement timing, and outcome-definition overlap.

## Cross-outcome synthesis

- **Best confirmatory outcome:** NoHandJointInvolvement.
- **Weak confirmatory outcome:** NegRFandACCP.
- **Confirmatory model close to non-informative:** AsymmetricArthritis.
- **Best exploratory model family:** broad ridge numerically, although broad ridge and broad elastic net were essentially tied.
- **Regularization finding:** ordinary logistic regression did not improve any outcome and showed the clearest instability for AsymmetricArthritis. Ridge remains the defensible primary model.
- **Broad-model signal:** all three outcomes contain information beyond the common core, but the available sample is insufficient to turn that broad signal into a stable confirmatory model.

## Report-presentation issues

These do not invalidate the saved analysis, but they should be corrected in a publication-facing report:

1. The displayed threshold table contains only the first 20 rows, which happen to be the two AsymmetricArthritis broad models. The complete CSV contains all models and outcomes.
2. The displayed coefficient-stability table uses a globally sorted `head(40)`, so all shown rows come from the first alphabetical outcome/model group. It is not a balanced cross-outcome summary. The complete CSV should be summarized separately by outcome and model.
3. Extreme calibration bootstrap values for the AsymmetricArthritis core logistic model should be explicitly marked as numerically unstable rather than presented as ordinary precise intervals.
4. A publication table should include prevalence/null-model benchmarks beside log loss, Brier score, and average precision.
5. A concise model card should clearly separate confirmatory common-core results from exploratory broad-model results.

## Recommended next steps

1. **Do not select a clinical threshold yet.** Define the clinical action, relative cost of false positives and false negatives, and intended setting first.
2. **Do not promote the broad model to confirmatory status.** First obtain external or temporal validation, preferably with geographic/site diversity.
3. **Prioritize NoHandJointInvolvement for external validation.** It has the strongest confirmatory evidence.
4. **For AsymmetricArthritis, revisit predictor design rather than tuning harder.** The common core contains little useful signal; clinically motivated predictors and improved measurement may matter more than another algorithm.
5. **For broad-model development, obtain a larger sample or prespecify a much smaller predictor subset.** Avoid data-driven winner selection from the current dataset.
6. **Audit timing and definitional overlap** for all broad predictors, especially joint-location and joint-count variables.
7. **Externally assess calibration-in-the-large, calibration slope, discrimination, and clinical utility.** Recalibration should be considered only in an external target population, not automatically on the development data.
8. **Retain the full reproducibility artifacts**: split assignments, OOF predictions, selected hyperparameters, coefficients, SHAP summaries, run signature, and checkpoints.

## Final scientific status

**Stage 3B is complete and passes its internal technical audit.** The common-core ridge findings can be reported as internally validated confirmatory analyses, with outcome-specific limitations. The broad-model findings should remain explicitly exploratory. None of the models is ready for clinical deployment without external validation and a prespecified clinical-use framework.
