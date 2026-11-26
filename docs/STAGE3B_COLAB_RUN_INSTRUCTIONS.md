# Stage 3B v1.1 — Colab/VS Code instructions

## Important performance fact

The notebook uses scikit-learn logistic regression. These models run on CPU, not CUDA. Selecting a Colab GPU does not accelerate `LogisticRegression` or `GridSearchCV`. Prefer a runtime with more CPU cores/high RAM if available. The notebook uses all available CPU cores and limits BLAS threads inside parallel searches to prevent oversubscription.

## Project location in Colab

A remote Colab runtime cannot access `the authorized RA_PROJECT_DIR` on the local Windows computer. Copy the complete project to either:

```text
<RA_PROJECT_DIR>
```

or upload it to the temporary runtime at:

```text
<RA_PROJECT_DIR>
```

Google Drive is recommended because checkpoints survive a runtime disconnection. The notebook mounts Drive automatically only when the project is not already found.

The project must include:

```text
<RA_PROJECT_DIR>/
├── 03B_modeling_validation.ipynb
├── config/stage3_modeling_decisions.yaml
├── cleaned_data/cleaned_master_data.csv
├── derived_data/
├── preprocessing_outputs/tables/stage2_validation_audit.csv
└── modeling_feasibility/tables/stage3a_validation_audit.csv
```

## Install dependencies in the Colab kernel

Run in a notebook cell:

```python
%pip install -q "pandas>=2,<3" "numpy>=1.24,<3" "scipy>=1.10,<2" \
    "scikit-learn>=1.6,<1.10" "matplotlib>=3.7,<4" "seaborn>=0.13,<1" \
    "PyYAML>=6,<7" "packaging>=23,<27" "threadpoolctl>=3.1,<4"
```

Restart the kernel if pip asks you to do so, then run the notebook from the beginning.

## Optional explicit path

If the project is elsewhere, set this before running the path-configuration cell:

```python
import os
os.environ["RA_PROJECT_DIR"] = "<RA_PROJECT_DIR>"
```

## Old checkpoints

Version 1.1 has a new signed pipeline identifier. Checkpoints produced by the older notebook are automatically rejected. They may be deleted or archived. New checkpoints are saved after each completed outcome.

## Runtime and resume

The full 3-outcome, 4-model, repeated nested analysis can take a long time even in Colab because it performs tens of thousands of CPU fits. If interrupted, reconnect, reopen the same project, and run all cells again. Completed outcomes with a matching v1.1 signature are loaded rather than refitted.

Do not set `RA_STAGE3B_QUICK_TEST` for scientific results.

## Final report

After all outcomes finish, the final cell creates:

```text
modeling_results/report/Stage3B_modeling_validation_report.html
```

Upload that HTML report for review.