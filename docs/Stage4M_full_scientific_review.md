# Stage 4 Missingness Addendum — Independent Review

## Overall verdict

The full model-fitting execution is technically valid and numerically reproducible. The uploaded notebook reports full mode, 5 outer folds × 10 repeats, 2,000 bootstrap resamples, 500/500 completed outer fits, and 28/28 internal checks passed. Independent reconstruction confirmed the OOF predictions, patient averaging, performance metrics, paired point differences, near-complete feature frequencies, predictor-level missingness summaries, and all 12 uploaded artifacts represented in the registry.

One descriptive error was identified: the reported “missingness-burden tertiles” do not preserve ties. The code uses `pd.qcut(burden.rank(method='first'), 3, ...)`, which splits patients with identical missingness according to row order. Because the source rows are outcome-ordered, this created the previously reported extreme 1.1%, 47.6%, and 11.3% `NegRFandACCP` prevalences. Those tertile results, the corresponding figure, and the earlier Stage 4 missingness-tertile subgroup results must not be used.

This error does **not** affect any fitted model, OOF prediction, primary sensitivity comparison, predictor-level missingness table, or exact missingness-pattern table. It requires a descriptive-table/report correction, not refitting.

## Independent integrity audit

- 500/500 expected fits were present.
- Ten repeats and five outer folds were present for every planned analysis.
- 82,000 repeated OOF prediction rows were present.
- Every patient/model combination had ten OOF predictions.
- There were no duplicated patient/model/repeat predictions.
- All probabilities were finite and bounded.
- No fitting or convergence warning was captured.
- Ridge searches used 21 candidates; the NoHand XGBoost searches used 50.
- Patient-averaged probabilities and across-repeat SDs reconstructed to numerical precision.
- All discrimination, proper-score, and calibration point estimates reconstructed to numerical precision.
- All paired point differences against the original models reconstructed to numerical precision.
- Every reported CI used 2,000 bootstrap resamples.
- Near-complete predictor-selection frequencies reconstructed from the 500 diagnostics.
- Predictor-level case/noncase missingness summaries reconstructed exactly.
- All 12 uploaded registered artifacts matched their SHA-256 values.

The independent audit contains 22 passes and one scientifically important failure: the tie-breaking burden groups.

## Scientific findings

### 1. `NegRFandACCP`

The missingness-only ridge had meaningful but incomplete discrimination:

- AUROC 0.629 (95% CI 0.585–0.670)
- AP 0.256 (0.230–0.300)
- log loss 0.473
- Brier 0.153
- calibration intercept 0.069; slope 1.057

Compared with the original refined broad ridge, the missingness-only model was clearly inferior in AUROC and AP. Missingness therefore carries real outcome information but does not explain the model’s entire performance.

Removing explicit numeric/binary missingness indicators produced:

- AUROC 0.678 versus approximately 0.691 for the original model;
- AUROC change −0.0131 (95% CI −0.0265 to 0.0005);
- AP change −0.0049 (−0.0192 to 0.0111);
- log-loss deterioration 0.00657 (0.00198–0.01078);
- Brier deterioration 0.00165 (0.00021–0.00303).

Thus, explicit missingness flags provide a small but detectable proper-score benefit, while their incremental discrimination is uncertain.

The near-complete model had AUROC 0.675 and AP 0.300. Its log loss was significantly worse than the original by 0.00711 (0.00158–0.01240); AUROC and AP intervals included no difference. Removing higher-missingness predictors modestly weakens probabilistic performance but does not collapse discrimination.

The strongest outcome-associated missingness involved TyG, leukopenia, anemia, thrombocytopenia, and thrombocytosis. Missingness was generally less common among positive cases than noncases, consistent with differential workup/documentation.

**Conclusion:** `NegRFandACCP` is partly dependent on local data-collection patterns, but its full predictive signal is not reducible to missingness. The Stage 3B model remains usable as an internally validated development result, with an explicit transportability warning.

### 2. `NoHandJointInvolvement`

The missingness-only model was weak:

- AUROC 0.559 (0.518–0.599)
- AP 0.254 (0.231–0.296)

Removing explicit indicators from ridge caused no robust change:

- AUROC −0.0067 (−0.0153 to 0.0024)
- AP −0.0018 (−0.0152 to 0.0119)
- log-loss improvement −0.0038 (−0.0085 to 0.0016), where negative means deterioration
- Brier improvement −0.0012 (−0.0029 to 0.0006)

Removing explicit indicators from XGBoost also caused no robust change:

- AUROC −0.0004 (−0.0059 to 0.0053)
- AP +0.0060 (−0.0046 to 0.0184)
- no material proper-score change

The near-complete ridge was effectively unchanged from original ridge across all principal metrics.

**Conclusion:** the strong NoHand result is not materially driven by explicit missingness flags or high-missingness predictors. Its principal limitation remains the Stage 4 finding that performance depends heavily on contemporaneous joint/anatomy information.

### 3. `AsymmetricArthritis`

The missingness-only model was close to chance:

- AUROC 0.535 (0.485–0.587)
- AP 0.277 (0.247–0.323)

Neither removing explicit indicators nor restricting ridge to near-complete predictors materially changed performance. Every paired interval for AUROC, AP, log loss, and Brier included no difference.

**Conclusion:** the Asymmetric model is robust to the tested missing-data modeling choices. Missingness is associated with outcome status descriptively, but it contributes little independent predictive performance.

## Corrected missingness-burden description

A tie-preserving descriptive grouping gives:

| Outcome | Complete data | >0–5% missing | >5% missing |
|---|---:|---:|---:|
| NegRFandACCP | 104/374 = 27.8% | 51/257 = 19.8% | 9/189 = 4.8% |
| NoHandJointInvolvement | 78/274 = 28.5% | 95/347 = 27.4% | 18/199 = 9.0% |
| AsymmetricArthritis | 48/274 = 17.5% | 70/347 = 20.2% | 72/199 = 36.2% |

These results still show meaningful association between missingness burden and outcomes, but not the previously reported `NegRFandACCP` 1.1%/47.6%/11.3% pattern.

The corrected groups are descriptive and were defined after discovering the tie problem. They should be labeled as a correction, not as a newly prespecified inferential analysis. The most defensible evidence about missingness remains the nested missingness-only model, no-indicator sensitivities, near-complete sensitivities, and predictor-level summaries.

## Publication implications

### Findings supported

- Missingness alone has moderate signal for `NegRFandACCP`, but materially less than the full model.
- Explicit missingness indicators make a small contribution to `NegRFandACCP` proper-score performance.
- The `NoHandJointInvolvement` and `AsymmetricArthritis` conclusions are robust to removing explicit missingness flags and higher-missingness predictors.
- No true site, center, calendar-date, or calendar-year field exists to determine the operational origin of missingness patterns.
- External evaluation remains necessary, especially for `NegRFandACCP` calibration and transportability.

### Findings to retract or replace

- Do not report the low/middle/high missingness tertile prevalence values from Stage 4 or this addendum.
- Do not use missingness-tertile subgroup performance estimates generated with `rank(method='first')`.
- Replace the burden figure/table with a tie-preserving descriptive table or omit grouped burden results entirely.

## Required final correction

No model refitting or further model development is needed. The final action is:

1. replace `qcut(rank(method='first'))` with tie-preserving groups;
2. regenerate the burden table and figure;
3. regenerate any missingness-group subgroup metrics without splitting ties;
4. add a correction note to the Stage 4 and missingness-addendum reports;
5. then stop internal analysis and proceed to manuscript preparation.

Stage 3B remains the prespecified primary analysis. Stages 3C, 4, and this addendum remain post hoc robustness work.
