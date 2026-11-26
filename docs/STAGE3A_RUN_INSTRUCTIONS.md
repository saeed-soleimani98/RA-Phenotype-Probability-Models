# Stage 3A run instructions

Place the notebook in the existing project directory after Stage 2 has completed:

```text
the authorized RA_PROJECT_DIR\03A_sample_size_complexity_feasibility.ipynb
```

Required Stage 2 products:

```text
cleaned_data\cleaned_master_data.csv
derived_data\dataset_registry.csv
derived_data\{outcome}__predictor_manifest.csv
preprocessing_outputs\tables\stage2_validation_audit.csv
```

Run all cells in order. The notebook does not fit a prediction model. It creates:

```text
the authorized RA_PROJECT_DIR\modeling_feasibility\
├── complexity_recommendation.yaml
├── tables\
├── figures\
└── report\Stage3A_feasibility_report.html
```

The final cell performs a fresh execution and HTML export. Share the resulting HTML report before selecting the confirmatory core predictor set.