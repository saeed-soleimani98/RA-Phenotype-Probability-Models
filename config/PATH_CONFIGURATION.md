# Path configuration (portable, data-free)

The supplied workflow used machine-specific locations (`G:\Medical-ML\RA`,
`/home/user/ra_analysis`, and Colab Drive folders). Those literals were removed
from all notebooks, scripts and run instructions. They are replaced by
environment variables resolved with `pathlib.Path`.

| Variable | Purpose | Required for |
|:--|:--|:--|
| `RA_PROJECT_DIR` | Authorized local workspace holding prior-stage products and protocol YAML files | All stages after EDA |
| `RA_DATA_PATH` | Exact restricted source CSV | EDA and Stage 2 |
| `RA_OUTPUT_DIR` | Local, git-ignored output root | Report/manuscript utilities |
| `RA_ARTIFACT_DIR` | Local, git-ignored model/SHAP artifact root | Figure/SHAP utilities |
| `RA_CORRECTIONS_PATH` | Authorized JSON list of individual value corrections | Stage 2 |

Copy `.env.example` to `.env`, replace every placeholder with an authorized
local path, and load it into the shell or kernel before execution. The
repository never downloads, synthesizes, or fabricates data. When a required
value is absent, notebooks raise an explicit `FileNotFoundError` or
`RuntimeError` rather than silently falling back to a fabricated input.

`src/ra_paths.py` exposes the same variables as small Python helpers for
scripts and tests. Notebooks keep short inline resolution cells so they remain
self-contained when copied into an authorized project workspace.

The only remaining path-like strings in documentation are explicit placeholders
of the form `<RA_PROJECT_DIR>`; they are not real locations.
