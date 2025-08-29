from __future__ import annotations
import pandas as pd

def check_inconsistencies(df: pd.DataFrame) -> dict:
    """Return counts and examples of potential data issues."""
    res = {}
    for col in ["jst_code","year","fires","alcohol_outlets","population"]:
        if col in df.columns:
            res[f"null_{col}"] = int(df[col].isna().sum())
    # negatives
    for col in ["fires","alcohol_outlets","population","area_km2"]:
        if col in df.columns:
            res[f"negative_{col}"] = int((df[col] < 0).fillna(False).sum())
    # duplicates per key
    if set(["jst_code","year"]).issubset(df.columns):
        dup = df.duplicated(["jst_code","year"]).sum()
        res["duplicate_jst_year_rows"] = int(dup)
    # rows lacking any of the core metrics
    core = [c for c in ["fires","alcohol_outlets","population"] if c in df.columns]
    if core:
        res["rows_with_missing_core_metric"] = int(df[core].isna().any(axis=1).sum())
    return res
