# Stage 4 Scientific Plan When External Data Are Not Yet Available

## Decision

The next scientific step is **not another algorithm search**. It is a locked robustness, semantic-validity, and publication-readiness stage using the existing cohort, followed by submission as a development/internal-validation study. External validation remains a future Stage 5.

## Scientific objective

Determine whether the current conclusions survive:

1. model-family selection performed entirely inside the validation hierarchy;
2. removal of outcome-proximal predictor domains;
3. missingness and subgroup heterogeneity;
4. stricter calibration and stability presentation.

No analysis in Stage 4 may redefine the Stage 3B primary result or be used to search for a more favorable algorithm.

## Stage 4A — Freeze and register

Before any additional analysis:

- freeze Stage 3B and Stage 3C artifacts and hashes;
- state that Stage 3B is confirmatory and Stage 3C/4 are post hoc exploratory;
- lock outcomes, candidate families, splits, metrics, and sensitivity analyses;
- prohibit new algorithms, new seeds, favorable exclusions, and tuning-grid expansion;
- define the intended prediction time and use case.

If predictors and outcomes are measured during the same encounter, use the term **contemporaneous phenotype classification**, not future prognosis.

## Stage 4B — Fully nested model-family-selection audit

The current nested CV gives internally valid estimates for each family, but choosing the best family after reviewing all OOF results creates winner’s optimism.

Use the existing outer folds and inner log-loss records:

1. Within each outer-training split, identify the family with the lowest inner-CV log loss.
2. Use only that already-fitted family’s prediction for the untouched outer-test fold.
3. Repeat across all 50 outer splits.
4. Average each patient’s ten selector predictions.
5. Evaluate AUROC, AP, log loss, Brier score, calibration intercept/slope, and fold stability.
6. Report how often each family was selected.
7. Compare the selector procedure with broad ridge using paired patient bootstrap intervals.

This estimates the performance of the **algorithm-selection procedure**, rather than reporting the optimistic maximum among eight externally compared families. It requires no new tuning and no new algorithm.

Interpretation rule: if the selector does not clearly improve log loss and calibration over broad ridge, the manuscript should conclude that routine algorithm selection adds no reliable value.

## Stage 4C — Locked semantic/domain-removal sensitivities

### NoHandJointInvolvement

Using the same outer splits, rerun only broad ridge and XGBoost after excluding:

- DAS tender and swollen joint counts;
- grip strength;
- all individual joint-location variables;
- other clinician-reviewed anatomy variables judged contemporaneously proximal to the target.

Purpose: determine whether performance reflects general patient information or reconstruction of the hand-involvement phenotype from the same examination.

### AsymmetricArthritis

Using the same outer splits, rerun only broad ridge and XGBoost after excluding:

- joint counts;
- individual joint-location variables;
- pattern/laterality-proximal variables;
- any variable used directly or indirectly in the clinical definition.

### NegRFandACCP

No new algorithm comparison is needed. Confirm and document that RF and anti-CCP components and derived serology proxies remain absent. Broad ridge remains the exploratory candidate.

Report absolute performance after domain removal and paired change from the original model. Do not use the sensitivity result to select a new predictor subset.

## Stage 4D — Missingness robustness

Do not replace the primary fold-contained imputation strategy. Add descriptive robustness checks:

- report missingness by outcome status;
- evaluate OOF performance by prespecified patient missingness-burden groups;
- inspect whether predictions or errors are associated with missingness burden;
- repeat principal comparisons excluding the highest-missingness predictor domains, if clinically defensible;
- document that unknown/not assessed values were not recoded as absence.

Avoid complete-case analysis as a new primary analysis. It can be reported only as a limited sensitivity because it may introduce selection bias and lose information.

## Stage 4E — Subgroup and heterogeneity audit

Evaluate the already generated OOF predictions—do not refit subgroup-specific models—within a small prespecified set:

- sex;
- clinically defined age groups;
- recruitment time or site, if available;
- missingness-burden group.

For each sufficiently sized subgroup, report N, events, AUROC, Brier score, calibration-in-the-large, calibration slope, and wide confidence intervals. Treat this as heterogeneity/applicability assessment, not a search for favorable subgroups. Do not interpret very small subgroups.

A female-only reproductive-variable model should not be added unless a separate formal sample-size assessment supports it.

## Stage 4F — Publication-grade calibration and stability

For the primary Stage 3B model and locked Stage 3C challengers:

- show flexible smoothed calibration curves rather than deciles alone;
- add bootstrap confidence bands;
- show calibration intercept and slope intervals;
- show predicted-probability distributions by outcome;
- report patient-level across-repeat prediction SD;
- show outer-fold metric distributions, explicitly noting that 50 folds are correlated;
- report hyperparameter-selection frequencies and inner train-validation gaps.

Do not add decision-curve analysis until a real clinical action and plausible threshold range are specified. A decision curve cannot determine the appropriate threshold by itself.

## Stage 4G — Final model specification

For reproducibility—not for claiming new validation—fit and archive final full-cohort pipelines for the locked candidates:

- Stage 3B common-core ridge for all outcomes;
- broad ridge for NegRFandACCP;
- broad ridge and XGBoost for NoHandJointInvolvement;
- broad ridge, with XGBoost secondary, for AsymmetricArthritis.

For each final model, save:

- exact predictor list and definitions;
- preprocessing and missingness rules;
- fitted pipeline/model object;
- hyperparameter-selection rule;
- software versions and random seeds;
- model card and intended-use statement;
- checksum;
- example input and output.

Do not report apparent full-data performance as validated performance. Retain repeated nested-CV estimates as the internal-validation results.

## Stage 4H — Manuscript and reproducibility package

Frame the paper as:

> Development and repeated nested internal validation of models for three atypical rheumatoid-arthritis phenotypes, with a post hoc comparison of regularized regression and nonlinear machine-learning algorithms.

Use TRIPOD+AI and provide a completed checklist. Complete a PROBAST+AI self-assessment covering participants/data, predictors, outcome, and analysis.

Minimum manuscript package:

- protocol chronology showing Stage 3B was frozen before Stage 3C;
- participant-flow diagram;
- outcome definitions and prevalence;
- predictor timing/availability table;
- missingness table;
- formal sample-size/complexity assessment;
- complete nested-CV and preprocessing description;
- discrimination, calibration, proper scores, and uncertainty;
- model-family selector analysis;
- semantic domain-removal analyses;
- limitations and future external-validation plan;
- code, environment, split assignments, OOF predictions, manifests, and data dictionary where permitted.

## Claims permitted without external data

Permitted:

- internally validated performance in this source population;
- internally observed model comparisons;
- evidence that complexity did or did not add value under repeated nested CV;
- exploratory phenotype associations and permutation importance;
- need for future external validation.

Not permitted:

- externally validated;
- generalizable or transportable;
- clinically useful or implementation-ready;
- recommended clinical threshold;
- causal predictor interpretation;
- universal superiority of XGBoost or another family.

## Recommended final sequence

1. Freeze and register Stage 4 protocol.
2. Run the fully nested family-selector audit.
3. Run the two locked domain-removal sensitivities.
4. Complete missingness and subgroup heterogeneity audits.
5. Produce publication-grade calibration/stability figures.
6. Fit and archive final full-cohort model objects without reporting apparent performance.
7. Complete TRIPOD+AI and PROBAST+AI checklists.
8. Write and submit the internal-validation manuscript.
9. When external data become available, conduct a separately registered Stage 5 validation without changing the locked models.

## Publication judgment

Absence of external data does not invalidate a development/internal-validation paper. Repeated nested CV using all available data is preferable to creating a small holdout set. However, external validation is strongly preferred for claims about transportability and clinical use.

A Q1 specialty or clinical-prediction journal submission is scientifically defensible if the manuscript emphasizes the prespecified primary analysis, complete calibration, formal sample-size limitations, semantic sensitivities, model stability, and reproducibility. Acceptance cannot be guaranteed, and top general medical/AI journals may expect multicenter or external evaluation. The paper should therefore compete on methodological rigor, transparent negative/mixed findings, and clinical novelty—not on an unsupported claim of deployment readiness.
