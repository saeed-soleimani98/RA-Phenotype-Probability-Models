from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PRIMARY_ROLES = {'primary_predictor'}
EXPANDED_ROLES = {
    'primary_predictor',
    'direct_target_component_sensitivity',
    'high_missingness_sensitivity',
    'pattern_variable_sensitivity',
}


def load_column_groups(manifest_path: str, scope: str = 'primary') -> dict[str, list[str]]:
    manifest = pd.read_csv(manifest_path)
    roles = PRIMARY_ROLES if scope == 'primary' else EXPANDED_ROLES
    if scope not in {'primary', 'expanded'}:
        raise ValueError("scope must be 'primary' or 'expanded'")
    selected = manifest[manifest['role'].isin(roles)]
    return {
        'numeric': selected.loc[selected['semantic_type'].eq('numeric'), 'column'].tolist(),
        'binary': selected.loc[selected['semantic_type'].eq('binary'), 'column'].tolist(),
        'categorical': selected.loc[selected['semantic_type'].eq('categorical'), 'column'].tolist(),
    }


def make_preprocessor(column_groups: dict[str, list[str]]) -> ColumnTransformer:
    numeric = Pipeline([
        ('imputer', SimpleImputer(strategy='median', add_indicator=True, keep_empty_features=True)),
        ('scaler', StandardScaler()),
    ])
    binary = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent', add_indicator=True, keep_empty_features=True)),
    ])
    categorical = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown', keep_empty_features=True)),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=True)),
    ])
    return ColumnTransformer([
        ('numeric', numeric, column_groups['numeric']),
        ('binary', binary, column_groups['binary']),
        ('categorical', categorical, column_groups['categorical']),
    ], remainder='drop', verbose_feature_names_out=True)
