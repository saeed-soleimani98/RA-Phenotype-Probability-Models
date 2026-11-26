"""Centralized, data-free path configuration for the RA phenotype code.

This module reads environment variables only. It never downloads, creates,
looks up, or fabricates clinical data. It is intended to make machine-specific
absolute paths unnecessary while producing explicit errors when an authorized
local location has not been configured.
"""
from __future__ import annotations

import os
from pathlib import Path


class MissingConfiguration(RuntimeError):
    """Raised when a required authorized local path is not configured."""


def _read(name: str) -> Path | None:
    value = os.environ.get(name)
    if not value:
        return None
    path = Path(value).expanduser()
    if str(value).startswith(("$", "<")) or "/path/to/" in str(value):
        raise MissingConfiguration(
            f"{name} contains an unexpanded placeholder ({value!r}). "
            "Copy .env.example to .env and supply an authorized local path."
        )
    return path


def project_dir(required: bool = False) -> Path | None:
    """Authorized workspace holding intermediates from prior stages."""
    path = _read("RA_PROJECT_DIR")
    if path is None and required:
        raise MissingConfiguration(
            "RA_PROJECT_DIR is required. Set it to the authorized local project "
            "directory (see .env.example)."
        )
    return path


def data_path(required: bool = False) -> Path | None:
    """Restricted source CSV; never bundled with this repository."""
    path = _read("RA_DATA_PATH")
    if path is None and required:
        raise MissingConfiguration(
            "RA_DATA_PATH is required. Set it to the authorized restricted "
            "source CSV (see .env.example). Data are not included here."
        )
    return path


def output_dir() -> Path:
    """Local output root; defaults to ./outputs, which is git-ignored."""
    return _read("RA_OUTPUT_DIR") or Path("./outputs")


def artifact_dir(required: bool = False) -> Path | None:
    """Derived model/SHAP artifact root outside version control."""
    path = _read("RA_ARTIFACT_DIR")
    if path is None and required:
        raise MissingConfiguration(
            "RA_ARTIFACT_DIR is required. Set it to a local, git-ignored "
            "artifact directory (see .env.example)."
        )
    return path


def correction_spec_path(required: bool = False) -> Path | None:
    """Authorized local JSON with individual correction records."""
    path = _read("RA_CORRECTIONS_PATH")
    if path is None and required:
        raise MissingConfiguration(
            "RA_CORRECTIONS_PATH is required. The individual correction "
            "records are withheld from this repository; see "
            "config/corrections_template.json and .env.example."
        )
    return path


def candidate_project_roots() -> list[Path]:
    """Portable discovery candidates, with private host paths excluded."""
    roots: list[Path] = []
    for path in (project_dir(), Path.cwd(), Path.cwd() / "ra_analysis",
                 Path.cwd() / "stage2_outputs"):
        if path is not None and path not in roots:
            roots.append(path)
    return roots
