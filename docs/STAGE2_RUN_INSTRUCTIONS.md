# Stage 2 run instructions

Place these files in:

```text
the authorized RA_PROJECT_DIR\
├── 02_data_cleaning_and_preprocessing.ipynb
├── stage2_requirements.txt
└── Atypical_presentations_RA_predictors_valid_c_exclusions_final_population.csv
```

From PowerShell or Anaconda Prompt:

```powershell
cd the authorized RA_PROJECT_DIR
python -m pip install -r stage2_requirements.txt
python -m jupyter lab
```

Open `02_data_cleaning_and_preprocessing.ipynb`, save it, and run all cells in order.

The notebook will create:

```text
the authorized RA_PROJECT_DIR\
├── config\analysis_decisions.yaml
├── cleaned_data\
│   ├── source_fingerprint.csv
│   ├── correction_log.csv
│   └── cleaned_master_data.csv
├── derived_data\
│   ├── dataset_registry.csv
│   ├── {outcome}__primary_eligible.csv
│   ├── {outcome}__sensitivity_expanded.csv
│   └── {outcome}__predictor_manifest.csv
├── preprocessing\
│   ├── preprocessing_columns.json
│   └── preprocessing_factory.py
└── preprocessing_outputs\
    ├── stage2_run_summary.json
    ├── tables\
    └── report\Stage2_cleaning_preprocessing_report.html
```

The final cell launches a clean execution and creates the HTML report. Share that HTML file for review before choosing and fitting models.