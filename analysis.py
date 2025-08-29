from __future__ import annotations
import json
from typing import Optional, Tuple
import numpy as np
import pandas as pd
from .data_io import load_many, normalize_columns
from .clean_merge import unify_jst_codes, coerce_numeric, merge_all
from .inconsistencies import check_inconsistencies

def _basic_stats(df: pd.DataFrame, col: str) -> dict:
    s = pd.to_numeric(df[col], errors="coerce")
    return {
        "count": int(s.notna().sum()),
        "min": float(s.min()) if s.notna().any() else None,
        "mean": float(s.mean()) if s.notna().any() else None,
        "max": float(s.max()) if s.notna().any() else None,
    }

def _corr(x: pd.Series, y: pd.Series) -> dict:
    valid = x.notna() & y.notna()
    if valid.sum() < 2:
        return {"n": int(valid.sum()), "pearson_r": None, "slope": None}
    xv, yv = x[valid].astype(float), y[valid].astype(float)
    r = float(np.corrcoef(xv, yv)[0,1])
    # slope via least squares
    slope = float(np.polyfit(xv, yv, 1)[0])
    return {"n": int(valid.sum()), "pearson_r": r, "slope": slope}

def run_analysis(
    psp_path: str,
    alcohol_path: str,
    population_path: str,
    jst_area_path: Optional[str] = None,
    jst_code_length: int = 7
) -> Tuple[dict, pd.DataFrame]:
    # Load and normalize
    psp = normalize_columns(load_many(psp_path), "psp")
    alcohol = normalize_columns(load_many(alcohol_path), "alcohol")
    population = normalize_columns(load_many(population_path), "population")
    area = normalize_columns(load_many(jst_area_path), "area") if jst_area_path else None

    # Clean
    for df in [psp, alcohol, population]:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
    if area is not None and "year" in area.columns:
        area["year"] = pd.to_numeric(area["year"], errors="coerce")

    psp = unify_jst_codes(psp, length=jst_code_length)
    alcohol = unify_jst_codes(alcohol, length=jst_code_length)
    population = unify_jst_codes(population, length=jst_code_length)
    if area is not None:
        area = unify_jst_codes(area, length=jst_code_length)

    # Merge
    merged, meta = merge_all(psp, alcohol, population, area)

    # Ratios
    if "population" in merged.columns:
        merged["fires_per_1000"] = (merged["fires"] / merged["population"]) * 1000
        merged["outlets_per_1000"] = (merged["alcohol_outlets"] / merged["population"]) * 1000

    # Basic stats
    stats = {
        "psp": _basic_stats(psp, "fires"),
        "alcohol": _basic_stats(alcohol, "alcohol_outlets"),
        "population": _basic_stats(population, "population"),
    }
    if area is not None and "area_km2" in merged.columns:
        stats["area"] = _basic_stats(area, "area_km2")

    # Correlations / hypotheses
    corrs = {
        "population_vs_fires": _corr(merged["population"], merged["fires"]),
        "population_vs_alcohol": _corr(merged["population"], merged["alcohol_outlets"]),
        "alcohol_vs_fires": _corr(merged["alcohol_outlets"], merged["fires"]),
        "per_capita_outlets_vs_per_capita_fires": _corr(merged["outlets_per_1000"], merged["fires_per_1000"]),
    }

    # Inconsistencies
    inconsistencies = check_inconsistencies(merged)

    # Summary
    summary = {
        "meta": meta,
        "stats": stats,
        "correlations": corrs,
        "inconsistencies": inconsistencies,
        "notes": {
            "jst_code_length": jst_code_length,
            "assumptions": [
                "Codes normalized by removing non-digits and truncating to jst_code_length.",
                "Area is attached by jst_code; year-less area treated as static.",
                "Auto-detected column names based on Polish/English heuristics.",
            ],
        },
    }
    return summary, merged
