# Rheumatoid arthritis cross-sectional phenotype probability models: code package

This package contains code and documentation prepared for a public, data-free reproducibility repository. It includes the complete analytical notebooks with all cell outputs removed, reusable Python modules, analysis protocols, environment files, and selected audit documentation.

## Ethical and data-governance boundary

No participant-level data, derived patient-level tables, trained model binaries, serialized preprocessors, patient identifiers, or row-level SHAP values are included. The original clinical dataset cannot be redistributed through this repository. Reviewers can inspect the complete analytical logic, but execution requiring the restricted cohort needs authorized access to the source data.

Do not commit files from the original `uploads`, `stage2_outputs/cleaned_data`, `stage2_outputs/derived_data`, model-artifact, prediction, or patient-level explanation directories. Before publication, run an automated secret and data-leak scan and inspect the full Git history.

## Included materials

- `notebooks/`: all analytical notebooks, sanitized by removing outputs and execution state
- `src/`: reusable preprocessing and final-model components
- `scripts/`: report, SHAP, figure, and manuscript-generation utilities
- `config/`: prespecified analysis and robustness protocols
- `environment/`: available requirements files from the executed workflow
- `docs/`: run instructions, protocols, and scientific audit notes
- `FILE_MANIFEST.tsv`: file list with SHA-256 checksums
- `PRIVACY_AND_DATA_GOVERNANCE.md`: explicit exclusion rules

## Important scientific boundary

The project estimates cross-sectional probabilities of three rheumatoid arthritis phenotype definitions. It does not provide diagnosis, prognosis, causal effects, or treatment recommendations. Internally validated out-of-fold performance must remain distinct from descriptive final-fit explanations.

## Before making a GitHub repository public

The repository-building agent should standardize paths and environment documentation without changing the analytical estimands or reported results. It should create a clear execution order, add a synthetic-schema or data-dictionary template only if it cannot reveal individual records, configure CI for static notebook and code checks, and ask the project owner to choose an open-source license before adding one.
