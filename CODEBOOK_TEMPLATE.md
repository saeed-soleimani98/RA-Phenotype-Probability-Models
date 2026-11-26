# Expected data schema (template only)

This is a **schema-level template** for authorized users. It lists column names, broad types and coding conventions. It deliberately contains **no values, frequencies, rare-category counts, prevalence figures, or participant examples**. The restricted source file is not included.

| Column / column family | Broad type | Coding convention | Modeling role |
|:--|:--|:--|:--|
| `VisitID` | identifier (string/integer-like) | Complete and unique in the authorized source | **Alignment key only; never a predictor** |
| `NegRFandACCP` | binary outcome | 1 = named phenotype present, 0 = absent; blanks unknown | Primary outcome |
| `NoHandJointInvolvement` | binary outcome | 1 = named phenotype present, 0 = absent; blanks unknown | Primary outcome |
| `AsymmetricArthritis` | binary outcome | 1 = named phenotype present, 0 = absent; blanks unknown | Primary outcome |
| `OnlyLargeJoints` | binary outcome | 1/0/blanks unknown | **EDA only; never modeled** |
| Demographic predictors (e.g. `Age`, `Gender`) | numeric / binary categorical | Numeric as recorded; gender uses a fixed documented reference level | Core or eligible predictors |
| Disease-duration predictors (e.g. `RADurationDays`) | numeric, nonnegative | `log1p` then training-fold standardization | Core predictor |
| Joint-count and global-assessment predictors | numeric | Training-fold median imputation + standardization | Core/eligible predictors |
| Acute-phase indicator (e.g. `AbnormalCRPorESR`) | binary | Most-frequent training-fold imputation + missingness indicator | Core predictor |
| Other clinical/laboratory predictors | numeric, binary, nominal categorical | Numeric median; binary most-frequent; nominal constant `Unknown` then one-hot inside fold | Stage 2 eligible pool only |
| Outcome-component / direct-proxy columns | binary | Outcome-specific; removed per frozen leakage rules | Never used for their own outcome |
| Comorbidity and binary exposure columns | binary | 1 = recorded present, 0 = recorded absent, blank = **unknown / not assessed** | Blank is never coerced to 0 |
| Reproductive-variable family | mixed | Excluded from all-patient primary models | Not primary predictors |

Rules that must be preserved:

* Blank binary and comorbidity values remain unknown/not assessed; imputation occurs **inside** training folds with missingness indicators where specified.
* `VisitID` aligns rows, folds, predictions and explanations only.
* Outcome columns and direct proxies are excluded per target-specific rules.
* `OnlyLargeJoints`, constant/no-variation fields, and reproductive variables are not primary model predictors.
* Rare binary levels and rare categories follow the frozen Stage 2 rules; no counts are published here.

The exact variable lists and leakage exclusions are defined in the notebooks and `config/stage3_modeling_decisions.yaml`, not in this template.
