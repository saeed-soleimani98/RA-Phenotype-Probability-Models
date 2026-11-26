# Stage 3A key findings

The current all-eligible predictor plan is too complex for a confirmatory model under formal Riley sample-size criteria.

| Outcome | Raw predictors | Independent candidate parameters | Events | Descriptive events/parameter |
|---|---:|---:|---:|---:|
| NegRFandACCP | 68 | 96 | 164 | 1.71 |
| NoHandJointInvolvement | 66 | 95 | 191 | 2.01 |
| AsymmetricArthritis | 70 | 99 | 190 | 1.92 |

The parameter totals include reference-coded categorical effects and explicit missingness indicators. The current full one-hot implementation creates 98–102 transformed columns.

Under the prespecified conservative assumption of optimism-adjusted Nagelkerke R² = 0.15 and target shrinkage ≥0.90:

| Outcome | Available N | Required N for current plan | Supported parameters at N=820 |
|---|---:|---:|---:|
| NegRFandACCP | 820 | 8,620 | 9 |
| NoHandJointInvolvement | 820 | 8,123 | 9 |
| AsymmetricArthritis | 820 | 8,478 | 9 |

Even under an optimistic Nagelkerke R² = 0.40 assumption, only 27–28 parameters are supported, far below the current 95–99.

## Scientific conclusion

1. Do not use all eligible variables as the confirmatory journal-primary model.
2. Define a small clinical core model without looking at full-dataset outcome associations.
3. Count parameters, not merely named variables.
4. Evaluate a high-dimensional ridge model only as a secondary/exploratory analysis with repeated nested cross-validation.
5. Treat nonlinear models as exploratory unless a defensible complexity budget is established.
6. The next task is to define the intended clinical use and clinically prespecified core predictor set.