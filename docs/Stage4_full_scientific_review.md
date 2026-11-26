# Stage 4 Full Scientific Review

**Reviewed materials:** full Stage 4 HTML report; all Stage 4 tables; selector predictions and choices; domain-removal repeated and averaged OOF predictions; diagnostics; calibration curves; subgroup table; protocol-linked artifact registry.  
**Execution:** full mode, 5 outer folds × 10 repeats, 5-fold inner tuning, 2,000 patient bootstraps, 500 calibration-band bootstraps.  
**Scientific hierarchy:** Stage 3B remains confirmatory primary; Stage 3C and Stage 4 remain post hoc exploratory robustness analyses.

## Executive conclusion

Stage 4 completed successfully and materially clarifies the scientific meaning of Stage 3C.

1. **The nested family-selection procedure confirms a modest nonlinear gain only for `NoHandJointInvolvement`.** It improves AUROC, log loss, and Brier score over refined broad ridge, while AP improvement remains borderline.
2. **There is no benefit from algorithm-family selection for `NegRFandACCP`.** The selector significantly worsens AP and does not improve other metrics.
3. **There is no robust selector benefit for `AsymmetricArthritis`.** All paired intervals include no improvement.
4. **The NoHand result depends strongly on contemporaneous joint/anatomy information.** Removing that domain reduces AUROC by 0.10 for ridge and 0.13 for XGBoost, with large deterioration in every principal metric.
5. **The Asymmetric result also depends on the joint/anatomy domain, but less completely.** XGBoost loses more than ridge after domain removal, and the ablated ridge and XGBoost perform similarly.
6. **Missingness heterogeneity is now the main unresolved methodological issue, especially for `NegRFandACCP`.** Outcome prevalence varies from 1.1% to 47.6% across missingness-burden tertiles. This suggests strong data-collection/workflow information that may not transport.

The project remains publishable as an internally validated development and robustness study. Before manuscript submission, a small locked missingness-mechanism addendum is scientifically necessary. More algorithm tuning is not.

## 1. Integrity and independent reproduction

### Report-level audit

- Full rather than quick mode was used.
- All 28 Stage 4 automated checks passed.
- There were 150 selector decisions, one per outcome and outer split.
- There were 24,600 untouched selector OOF prediction rows.
- There were 200 completed domain-removal outer-fold fits.
- All domain fits reported zero convergence warnings.
- Natural prevalence was retained; there was no resampling or class weighting.
- Every patient had ten selector and ten ablation OOF predictions.
- All publication figures were saved in 400-DPI PNG and vector SVG.
- Stage 3B remained explicitly primary.

### Independent numerical audit

Twenty-six additional checks were performed from the uploaded CSVs:

- every saved selector family exactly equaled the family with minimum inner-CV log loss for that outer training split;
- all selector probabilities reconstructed exactly from untouched Stage 3C repeated predictions;
- selector patient averages reproduced exactly;
- all selector metrics and calibration estimates reproduced exactly;
- all domain-removal patient averages reproduced exactly from 32,800 repeated OOF predictions;
- all domain-removal metrics and calibration estimates reproduced exactly;
- there were no duplicate patient/repeat ablation predictions;
- all 16 uploaded registered Stage 4 artifacts matched their SHA-256 hashes;
- all 200 domain fits had the intended candidate counts: 21 ridge values or 50 XGBoost candidates.

No numerical inconsistency was found.

## 2. Fully nested family-selector findings

The selector chooses a family using only inner-CV log loss inside each outer training split, then uses that family’s untouched outer-test predictions. This correctly evaluates the model-family selection procedure and avoids reporting only the optimistic maximum across externally compared families.

### Family selection frequencies

| Outcome | Most frequently selected families |
|---|---|
| NegRFandACCP | Random forest 80%; ridge/elastic net 16%; XGBoost 4% |
| NoHandJointInvolvement | XGBoost 66%; random forest 30%; ridge 4% |
| AsymmetricArthritis | Random forest 50%; XGBoost 42%; ridge/elastic net 8% |

No SVC, lasso, or AdaBoost model was selected in any full outer split. This supports excluding them from future development.

### NegRFandACCP

Selector performance:

- AUROC 0.688 (95% CI 0.651–0.726)
- AP 0.289 (0.259–0.338)
- log loss 0.460 (0.449–0.473)
- Brier 0.150 (0.146–0.154)
- calibration intercept 0.253 (−0.095 to 0.656)
- calibration slope 1.222 (0.946–1.556)

Versus refined broad ridge:

- AUROC difference −0.0030 (−0.0191 to 0.0131)
- AP difference **−0.0201 (−0.0432 to −0.0010)**
- log-loss improvement +0.0025 (−0.0027 to 0.0078)
- Brier difference −0.00004 (−0.00194 to 0.00190)

Although inner log loss selected random forest in 80% of folds, the selector did not improve external OOF proper scores and significantly worsened AP. This is a useful negative result: family selection adds complexity without dependable benefit.

**Recommendation:** retain broad ridge; do not promote random forest or the selector.

### NoHandJointInvolvement

Selector performance:

- AUROC 0.799 (0.765–0.831)
- AP 0.524 (0.472–0.591)
- log loss 0.439 (0.417–0.461)
- Brier 0.143 (0.134–0.151)
- calibration intercept 0.142 (−0.040 to 0.366)
- calibration slope 1.155 (0.986–1.360)

Versus refined broad ridge:

- AUROC improvement **+0.0240 (+0.0052 to +0.0433)**
- AP improvement +0.0400 (−0.0004 to +0.0790)
- log-loss improvement **+0.0177 (+0.0049 to +0.0301)**
- Brier improvement **+0.0065 (+0.0018 to +0.0112)**

This confirms that nonlinear families add a modest internal advantage for this outcome under a fully nested selection procedure. However, the selected family varies: XGBoost in 66%, random forest in 30%, and ridge in 4%. The result supports nonlinear structure, not one universally stable algorithm.

The selector is an evaluation procedure, not a single deployable model. For future external validation, a fixed XGBoost recipe plus broad ridge comparator remains more reproducible than deploying a fold-dependent family selector.

### AsymmetricArthritis

Selector performance:

- AUROC 0.671 (0.627–0.715)
- AP 0.370 (0.326–0.434)
- log loss 0.508 (0.492–0.524)
- Brier 0.166 (0.160–0.172)
- calibration intercept 0.067 (−0.260 to 0.417)
- calibration slope 1.058 (0.776–1.382)

Versus refined broad ridge, all intervals included no difference:

- AUROC +0.0138 (−0.0067 to +0.0348)
- AP +0.0157 (−0.0077 to +0.0399)
- log-loss improvement +0.0061 (−0.0008 to +0.0136)
- Brier improvement +0.0023 (−0.0002 to +0.0049)

**Recommendation:** do not claim complex-model superiority. Broad ridge remains the stability-oriented model.

## 3. Joint/anatomy-domain removal

The locked removal eliminated joint counts, grip strength, initial joint site, and all variables containing `Involvement`. This tests dependence on contemporaneous examination information rather than searching for a new predictor set.

### NoHandJointInvolvement

After domain removal:

| Model | AUROC | AP | Log loss | Brier | Calibration intercept/slope |
|---|---:|---:|---:|---:|---:|
| Broad ridge | 0.673 | 0.350 | 0.511 | 0.168 | 0.086 / 1.075 |
| XGBoost | 0.663 | 0.361 | 0.513 | 0.168 | 0.003 / 1.012 |

Paired degradation from the original model:

- Ridge AUROC −0.101 (−0.139 to −0.063)
- Ridge AP −0.134 (−0.192 to −0.078)
- Ridge log-loss deterioration 0.054 (0.035 to 0.073)
- XGBoost AUROC −0.133 (−0.176 to −0.090)
- XGBoost AP −0.162 (−0.225 to −0.097)
- XGBoost log-loss deterioration 0.073 (0.049 to 0.096)

Every interval shows material deterioration. Most of the apparent predictive advantage comes from contemporaneous joint/anatomy information. This does not automatically invalidate the model: it depends on the intended use.

- If the task is phenotype classification after a full joint examination, these predictors may be legitimate.
- If the task is early prediction before detailed joint assessment, the original performance is not an appropriate estimate.
- If the task is future prognosis, the current contemporaneous design is insufficient.

The manuscript must state the prediction time explicitly and should use “contemporaneous phenotype classification” unless temporality supports another term.

### AsymmetricArthritis

After domain removal:

| Model | AUROC | AP | Log loss | Brier | Calibration intercept/slope |
|---|---:|---:|---:|---:|---:|
| Broad ridge | 0.637 | 0.323 | 0.523 | 0.172 | −0.012 / 0.987 |
| XGBoost | 0.633 | 0.325 | 0.523 | 0.171 | −0.038 / 0.959 |

Ablated ridge lost AP and proper-score performance, while its AUROC interval narrowly included no change. XGBoost deteriorated on every metric:

- AUROC −0.041 (−0.070 to −0.014)
- AP −0.057 (−0.097 to −0.025)
- log-loss deterioration 0.017 (0.007 to 0.026)
- Brier deterioration 0.0063 (0.0028 to 0.0100)

After removal, XGBoost no longer outperforms ridge. Its apparent nonlinear advantage is therefore concentrated in joint/anatomy information. General non-joint predictors retain only weak-to-modest signal.

## 4. Missingness heterogeneity

This is the most consequential new finding.

### Outcome prevalence by missingness-burden tertile

| Outcome | Low missingness | Middle | High |
|---|---:|---:|---:|
| NegRFandACCP | **1.1%** (3/273) | **47.6%** (130/273) | **11.3%** (31/274) |
| NoHandJointInvolvement | 28.2% | 24.5% | 17.2% |
| AsymmetricArthritis | 17.6% | 19.8% | 32.1% |

For `NegRFandACCP`, missingness burden is strongly associated with the target. The low-missingness group has only three events and cannot support performance estimation. The middle group has nearly half positive cases. This pattern is too strong to treat as a routine subgroup fluctuation.

Individual missingness indicators also carry signal. For NegRFandACCP, missingness in TyG, leukopenia, anemia, and platelet variables differs substantially by outcome. The current preprocessing explicitly includes missingness flags, so models can learn local testing and documentation workflows.

This may represent:

- clinically informative testing patterns;
- differential workup by serostatus or disease presentation;
- calendar or workflow effects;
- data-source merging patterns;
- selection or documentation bias.

It is not direct target leakage, but it creates serious transportability risk. Another center may have different testing practices, causing calibration and discrimination to change sharply.

For NoHand and Asymmetric outcomes, missingness heterogeneity is less extreme but still produces meaningful calibration shifts. Missingness-group calibration slopes range from approximately 0.56 to 1.64 in some models.

## 5. Sex and age heterogeneity

- Male strata contain only 120 patients. NegRFandACCP has 16 male events and was appropriately suppressed.
- Age <40 contains only 65 patients and 15–17 events; metrics were appropriately suppressed.
- Most evaluable sex and age intervals overlap substantially.
- Apparent high male NoHand AUROC and male Asymmetric results have wide intervals and should not be promoted.
- There is no robust basis for subgroup-specific models.

The female-only reproductive-variable sensitivity remains unsupported by event counts and should not be added as a primary analysis.

## 6. Stability and overfitting

XGBoost remains less stable at the patient level than ridge or random forest:

- NoHand mean across-repeat probability SD: XGBoost 0.050 versus ridge 0.028;
- Asymmetric: 0.047 versus 0.030;
- NegRFandACCP: 0.038 versus 0.023.

Maximum patient-level SD reached 0.155 for NoHand XGBoost. Thus, aggregate gains coexist with instability in some individual predictions. This matters for any proposed individual-level use.

The domain-removal XGBoost searches also had larger inner train-validation gaps than ridge, especially for NoHand. Outer validation prevents optimistic reporting, but the gap is consistent with greater fitting flexibility and weaker transportability.

## 7. Publication status after Stage 4

### Stronger claims now supported

- The algorithm-family selector confirms a modest nonlinear internal gain for NoHandJointInvolvement.
- There is no complex-model benefit for NegRFandACCP.
- There is no robust complex-family advantage for AsymmetricArthritis.
- Joint/anatomy predictors explain much of the NoHand and XGBoost Asymmetric performance.
- Missingness and data-collection patterns materially affect performance and applicability.

### Claims that remain unsupported

- future prognostic prediction;
- transportability to another clinical workflow;
- deployment readiness;
- a recommended threshold;
- subgroup-specific superiority;
- causal interpretation;
- universal superiority of XGBoost or random forest.

### Manuscript framing

A defensible title/aim should emphasize:

> Development and repeated nested internal validation of models for contemporaneous atypical rheumatoid-arthritis phenotype classification, with locked robustness analyses of algorithm selection, predictor-domain proximity, and missingness heterogeneity.

The mixed and negative findings improve scientific credibility. The paper should not be framed as an “AI model achieving high accuracy.”

## 8. Required next analysis before submission

Freeze a short **missingness-mechanism addendum** before running it. No new algorithms are needed.

### A. Missingness-only benchmark

Using the exact saved outer splits, fit a simple ridge logistic model using only missingness indicators from primary-eligible predictors. This quantifies how much outcome information is carried by the data-collection process alone.

### B. No-missingness-indicator sensitivity

Repeat locked broad ridge and, only for NoHand, XGBoost with the same imputation but without explicit missingness flags. Compare paired OOF performance with the original models.

### C. Near-complete-predictor sensitivity

Repeat broad ridge using only predictors below a frozen missingness threshold, recommended ≤5%, while retaining the same preprocessing and splits. The threshold must be frozen before outcome-specific results are examined.

### D. Missingness pattern table

Report, by outcome status:

- missing count and percentage for every modeled predictor;
- standardized difference or absolute percentage difference;
- calendar/site association if such variables exist;
- prevalence across common missingness patterns.

### Stop rule

After this addendum, stop internal model development. Do not use the results to search for another model. Proceed to manuscript preparation and defer external validation to future data.

## Final verdict

Stage 4 passed technical and numerical audit. It strengthens the conclusion that complexity is selectively useful rather than universally superior. It also reveals two clinically important limitations: NoHand performance is largely driven by contemporaneous joint/anatomy information, and NegRFandACCP is strongly entangled with missingness patterns.

The study remains publishable, but the missingness mechanism must be characterized before submission. Once that targeted addendum is complete, further internal tuning would reduce rather than improve scientific credibility.
