# Stage 4M.1 Tie-Preserving Correction — Final Review

## Final verdict

The missingness-burden correction completed successfully and resolves the previously identified row-order tie-splitting defect.

- Notebook correction audit: **20/20 PASS**.
- Independent reconstruction: **20/20 PASS**.
- All 2,460 patient–outcome strata were present with no duplicate patients.
- Every identical missingness fraction mapped to exactly one group.
- Corrected prevalence counts reconstructed exactly.
- All locked-model and sensitivity-model subgroup counts, suppression decisions, and point metrics reconstructed to numerical precision.
- Every evaluable subgroup used 2,000 bootstrap resamples.
- All five uploaded registered correction artifacts matched their SHA-256 hashes.
- No model was refitted or reselected.

The prior rank-based low/middle/high burden results are superseded and must not be used. All overall model results remain unchanged.

## Corrected outcome prevalence

| Outcome | Complete | >0–5% missing | >5% missing |
|---|---:|---:|---:|
| NegRFandACCP | 104/374 (27.8%) | 51/257 (19.8%) | 9/189 (4.8%) |
| NoHandJointInvolvement | 78/274 (28.5%) | 95/347 (27.4%) | 18/199 (9.0%) |
| AsymmetricArthritis | 48/274 (17.5%) | 70/347 (20.2%) | 72/199 (36.2%) |

These categories are post hoc corrective descriptions aligned with the already frozen 5% near-complete threshold. They are not model-selection strata.

## Corrected locked-model heterogeneity

### NegRFandACCP

The >5% group had only nine events, so all performance metrics were correctly suppressed.

For refined broad ridge:

- complete: AUROC 0.577 (95% CI 0.513–0.639), calibration intercept −0.265, slope 0.626;
- >0–5%: AUROC 0.663 (0.587–0.738), calibration intercept 0.108, slope 1.089.

The nested selector showed the same qualitative pattern and did not improve upon ridge. The result indicates performance and calibration heterogeneity between complete and mildly incomplete records, while the high-missingness group cannot be assessed reliably.

This supports a transportability warning but does not invalidate the overall model. The no-indicator and near-complete analyses still show that explicit missingness handling contributes only modestly to overall proper-score performance.

### NoHandJointInvolvement

The >5% group had 18 events and was correctly suppressed.

Among evaluable groups:

- refined ridge AUROC: 0.739 complete and 0.750 in >0–5%;
- XGBoost AUROC: 0.758 complete and 0.783 in >0–5%;
- nested selector AUROC: 0.750 complete and 0.787 in >0–5%.

Intervals overlap substantially, and calibration slopes are close to one. The strong NoHand result is reasonably stable across complete and mildly incomplete records. The principal limitation remains dependence on contemporaneous joint/anatomy information, not missingness.

### AsymmetricArthritis

All corrected groups were evaluable. For refined broad ridge, AUROCs were:

- complete: 0.678 (0.590–0.763);
- >0–5%: 0.586 (0.517–0.653);
- >5%: 0.607 (0.528–0.687).

XGBoost and the nested selector showed similar patterns, with overlapping intervals. There is no robust evidence of subgroup-specific superiority.

Calibration varied more than discrimination: complete records had slopes around 1.56, while incomplete groups generally had slopes below one. This reinforces that external recalibration may be necessary even when overall discrimination is retained.

## Important interpretation note for the missingness-only model

Do not report within-group performance of the missingness-only model in the manuscript. In the complete-record group, every missingness predictor is identically zero. Residual patient-level prediction differences arise from fold-specific fitted intercepts after repeated OOF averaging, so within-group AUROC and extreme calibration slopes are not clinically interpretable.

The **overall** missingness-only results remain valid and useful:

- NegRFandACCP AUROC 0.629;
- NoHandJointInvolvement AUROC 0.559;
- AsymmetricArthritis AUROC 0.535.

## Publication use

### Use

- the corrected prevalence table;
- corrected locked-model subgroup results, clearly labeled post hoc exploratory;
- overall missingness-only, no-indicator, and near-complete analyses;
- the conclusion that missingness dependence is most consequential for NegRFandACCP;
- the conclusion that NoHand and Asymmetric findings are robust to tested missingness handling.

### Do not use

- any earlier low/middle/high missingness-tertile values;
- any earlier missingness-tertile subgroup metrics;
- within-group missingness-only AUROC or calibration estimates;
- performance estimates from the suppressed high-missingness NegRFandACCP and NoHand groups.

## Analysis stop decision

Internal analysis is now complete. No further tuning, algorithm comparison, predictor search, or subgroup fitting is justified.

The next phase is manuscript assembly:

1. freeze the final hierarchy of analyses;
2. prepare manuscript Methods and Results from Stage 3B through the corrected robustness analyses;
3. create the main and supplementary tables;
4. complete TRIPOD+AI reporting;
5. document PROBAST+AI risks and applicability limitations;
6. specify the fixed models intended for future external validation.
