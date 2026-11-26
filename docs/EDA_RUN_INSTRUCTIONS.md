# Running the RA EDA notebook on Windows

## 1. Required file placement

Place these two files in:

```text
the authorized RA_PROJECT_DIR\
├── RA_EDA.ipynb
└── Atypical_presentations_RA_predictors_valid_c_exclusions_final_population.csv
```

Do not rename the CSV unless you also update `CSV_NAME` in the configuration cell.

## 2. Environment

From Anaconda Prompt or PowerShell:

```powershell
cd the authorized RA_PROJECT_DIR
python -m pip install -r eda_requirements.txt
python -m jupyter lab
```

Open `RA_EDA.ipynb` and run all cells in order.

## 3. Generated directories

The notebook creates:

```text
the authorized RA_PROJECT_DIR\
├── derived_data\
│   ├── README.md
│   ├── target_specific_exclusion_rules.json
│   ├── NegRFandACCP__primary_leakage_controlled.csv
│   ├── NegRFandACCP__sensitivity_expanded.csv
│   ├── NegRFandACCP__predictor_manifest.csv
│   └── corresponding files for the other three outcomes
└── eda_outputs\
    ├── tables\
    ├── figures\
    ├── report\
    │   └── RA_EDA_report.html
    └── eda_run_summary.json
```

Each derived CSV retains `VisitID` only for traceability. The manifests mark it as `identifier_DO_NOT_MODEL`.

## 4. HTML export

Before using the final cell, save the notebook as:

```text
the authorized RA_PROJECT_DIR\RA_EDA.ipynb
```

Run the final cell. It executes a clean copy of the entire notebook and writes all executed outputs and embedded plots to:

```text
the authorized RA_PROJECT_DIR\eda_outputs\report\RA_EDA_report.html
```

If the final cell reports an error, share the complete traceback rather than editing the analysis logic.

## 5. Files to share for interpretation

Share at least:

1. `RA_EDA_report.html`
2. `eda_outputs/eda_run_summary.json`
3. `eda_outputs/tables/20_outcome_specific_dataset_registry.csv`

The HTML normally contains all information needed for the next discussion.