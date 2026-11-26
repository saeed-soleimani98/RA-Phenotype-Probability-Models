# Privacy and data-governance rules

## Content intentionally excluded

1. Raw, cleaned, imputed, or derived participant-level datasets.
2. VisitID values or any direct or indirect patient identifiers.
3. Out-of-fold prediction files, fold assignments, row-level bootstrap results, and patient-level stability tables.
4. Signed or unsigned patient-level SHAP tables and local explanation exports.
5. Serialized models, preprocessors, calibration objects, and binaries that could disclose training information.
6. Cell outputs that may contain dataframe previews, counts for rare combinations, local paths, or embedded figures generated from restricted data.
7. Credentials, access tokens, cloud links with embedded authorization, and private email addresses.

## Permitted public content

Analytical source code, output-free notebooks, package specifications, prespecified protocols, aggregate manuscript results already approved for publication, and non-sensitive figure-generation logic may be public after human review.

## Required pre-publication checks

- Scan every tracked file and the complete Git history for secrets and participant-level content.
- Reject common data and model formats by default in `.gitignore` and CI.
- Confirm that notebook outputs remain empty.
- Confirm that no absolute local or cloud paths expose private account details.
- Use synthetic data only when explicitly labeled and generated without fitting to or reproducing identifiable records.
- Keep the repository private until the project owner completes the final ethical and institutional review.
