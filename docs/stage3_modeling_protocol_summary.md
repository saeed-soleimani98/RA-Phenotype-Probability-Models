# Frozen Stage 3 modeling protocol

## Confirmatory analysis

For each of the three outcomes, use the same clinical core:

1. Age
2. Gender
3. log1p(RA duration days)
4. Tender joint count
5. Swollen joint count
6. Patient global assessment
7. Abnormal CRP or ESR

With missingness indicators, this is approximately nine independent parameters.

The confirmatory model is ridge logistic regression. Its L2 penalty is tuned inside inner five-fold cross-validation by minimizing log loss. Ordinary logistic regression with the same core is the transparent benchmark.

## Exploratory analyses

- Broad ridge logistic regression using all Stage 2 primary-eligible predictors.
- Broad elastic-net logistic regression using the same eligible pool.
- No boosting, random forests, SVMs, neural networks, or large model zoo.

## Validation

- Outer repeated stratified five-fold CV, repeated 10 times.
- Inner stratified five-fold CV for tuning.
- Identical outer splits for compared models.
- Every performance prediction is out-of-fold.
- Average each patient’s 10 out-of-fold probabilities.
- Use 2,000 stratified patient-level bootstrap resamples for 95% confidence intervals.
- Report split/repetition distributions separately as stability evidence.

## Evaluation

- Log loss is the tuning objective.
- Report AUROC, PR-AUC, Brier score, calibration intercept, calibration slope, and flexible calibration plots.
- No single primary classification threshold.
- Report threshold metrics over a prespecified grid.
- Use decision curves only if a clinical action and plausible threshold range can be stated.

## Calibration

Assess unmodified ridge probabilities first. Training-only logistic recalibration is a sensitivity analysis only if material miscalibration is observed. Never calibrate on the full evaluation dataset.

## Explainability

Use strictly out-of-fold SHAP, averaged per patient across repetitions. Report direction, magnitude, rank stability, sign stability, grouped clinical-domain importance, and standardized ridge coefficients. Keep core and broad explanations separate. Do not make causal claims.

## Model comparisons

Use paired metric differences with bootstrap confidence intervals. Do not perform winner-selection p-value testing. The core ridge model remains confirmatory regardless of small differences favoring exploratory models.

## Scope

This is internally validated contemporaneous classification. External validation is required before clinical use.
