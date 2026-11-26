"""Portable components used by Stage 4G serialized RA prediction pipelines."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class RADurationLogTransformer(BaseEstimator, TransformerMixin):
    """Replace raw RADurationDays with RADurationDays_log1p in a pandas frame."""
    def fit(self, X, y=None):
        if not isinstance(X, pd.DataFrame):
            raise TypeError("RADurationLogTransformer requires a pandas DataFrame")
        if "RADurationDays" not in X.columns:
            raise ValueError("Required column RADurationDays is missing")
        self.feature_names_in_ = np.asarray(X.columns, dtype=object)
        return self

    def transform(self, X):
        if not isinstance(X, pd.DataFrame):
            raise TypeError("RADurationLogTransformer requires a pandas DataFrame")
        z = X.copy()
        values = pd.to_numeric(z["RADurationDays"], errors="coerce")
        if (values.dropna() < 0).any():
            raise ValueError("RADurationDays must be nonnegative")
        insert_at = z.columns.get_loc("RADurationDays")
        z = z.drop(columns=["RADurationDays"])
        z.insert(insert_at, "RADurationDays_log1p", np.log1p(values))
        return z

    def get_feature_names_out(self, input_features=None):
        names = list(self.feature_names_in_ if input_features is None else input_features)
        return np.asarray(["RADurationDays_log1p" if x == "RADurationDays" else x for x in names], dtype=object)

class MissingnessFlags(BaseEstimator, TransformerMixin):
    """Return one float indicator per input column: 1 if missing, otherwise 0."""
    def fit(self, X, y=None):
        self.n_features_in_ = X.shape[1]
        return self

    def transform(self, X):
        if hasattr(X, "to_numpy"):
            return pd.isna(X).astype(float).to_numpy()
        return np.isnan(X).astype(float)

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            input_features = [f"x{i}" for i in range(self.n_features_in_)]
        return np.asarray([f"{x}__missing" for x in input_features], dtype=object)
