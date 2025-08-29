from __future__ import annotations
import re
import pandas as pd

def unify_jst_codes(df: pd.DataFrame, code_col: str = "jst_code", length: int = 7) -> pd.DataFrame:
    df = df.copy()
    def norm(v):
        s = "" if pd.isna(v) else re.sub(r"\D", "", str(v))
        return s[:length] if s else None
    df[code_col] = df[code_col].map(norm)
    return df

def coerce_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def merge_all(psp: pd.DataFrame, alcohol: pd.DataFrame, population: pd.DataFrame, area: pd.DataFrame | None) -> tuple[pd.DataFrame, dict]:
    """Inner-join on (jst_code, year). Attach static 'area_km2' by 'jst_code' if year missing."""
    meta = {}
    def count_rows(name, df): meta[f"rows_{name}"] = len(df)

    count_rows("psp_raw", psp); count_rows("alcohol_raw", alcohol); count_rows("population_raw", population)
    keys = ["jst_code", "year"]
    merged = psp.merge(alcohol, on=keys, how="inner", validate="many_to_many")
    merged = merged.merge(population, on=keys, how="inner", validate="many_to_many")
    if area is not None:
        if "year" in area.columns and area["year"].notna().any():
            merged = merged.merge(area, on=keys, how="left")
        else:
            merged = merged.merge(area.drop(columns=[c for c in area.columns if c not in ["jst_code","area_km2"]]).drop_duplicates("jst_code"),
                                  on="jst_code", how="left")
    meta["rows_merged"] = len(merged)

    for col in ["fires","alcohol_outlets","population","area_km2"]:
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")

    # Drops summary
    for name, df in [("psp", psp), ("alcohol", alcohol), ("population", population)]:
        # how many unique (code,year) pairs exist
        pairs = df[["jst_code","year"]].dropna().drop_duplicates()
        meta[f"unique_pairs_{name}"] = len(pairs)
    meta["unique_pairs_intersection"] = len(merged[["jst_code","year"]].drop_duplicates())

    return merged, meta
