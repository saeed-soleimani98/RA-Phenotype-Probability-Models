# Stage 3B run instructions

## Required placement

```text
the authorized RA_PROJECT_DIR\
├── 03B_modeling_validation.ipynb
├── stage3b_requirements.txt
├── config\
│   ├── analysis_decisions.yaml
│   ├── sensitivity_analysis_plan.csv
│   └── stage3_modeling_decisions.yaml
├── cleaned_data\cleaned_master_data.csv
├── derived_data\
│   ├── dataset_registry.csv
│   ├── NegRFandACCP__primary_eligible.csv
│   ├── NoHandJointInvolvement__primary_eligible.csv
│   ├── AsymmetricArthritis__primary_eligible.csv
│   └── the three predictor manifests
├── preprocessing_outputs\tables\stage2_validation_audit.csv
└── modeling_feasibility\tables\stage3a_validation_audit.csv
```

## Install and run

```powershell
cd the authorized RA_PROJECT_DIR
python -m pip install -r stage3b_requirements.txt
python -m jupyter lab
```

Open `03B_modeling_validation.ipynb` and run all cells in order.

## Runtime

The full scientific analysis performs repeated nested cross-validation for 3 outcomes and 4 models. Runtime depends strongly on CPU capacity and can exceed one hour. The notebook saves a signed checkpoint after each outcome. If execution is interrupted, restart the notebook and run all cells again; valid completed outcomes are loaded rather than refitted.

Do not set `RA_STAGE3B_QUICK_TEST` for scientific results. Quick mode is only for software testing.

## HTML report

After all three full checkpoints complete, run the final cell. It cleanly re-executes the notebook, loads the signed checkpoints, regenerates metrics and figures, and writes:

```text
the authorized RA_PROJECT_DIR\modeling_results\report\Stage3B_modeling_validation_report.html
```

Share that HTML report for scientific interpretation.

## Main outputs

```text
modeling_results\
├── checkpoints\
├── tables\
│   ├── patient_averaged_oof_predictions.csv
│   ├── performance_with_bootstrap_ci.csv
│   ├── paired_model_differences.csv
│   ├── threshold_grid_metrics.csv
│   ├── selected_hyperparameters.csv
│   ├── global_oof_shap_summary.csv
│   ├── coefficient_sign_selection_stability.csv
│   └── stage3b_validation_audit.csv
├── figures\
└── report\Stage3B_modeling_validation_report.html
```
