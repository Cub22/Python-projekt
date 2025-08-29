from __future__ import annotations
import os
import re
from typing import Optional, List
import pandas as pd

CANDIDATES = {
    "code": [r"^kod", r"jst", r"teryt", r"gmina", r"powiat", r"woj"],
    "year": [r"^rok", r"year"],
    "fires": [r"^po[żz]ar", r"events?", r"interwenc", r"zdarze"],
    "alcohol": [r"alkohol", r"konces", r"zezwol", r"outlet", r"sprzeda"],
    "population": [r"^popul", r"ludno", r"mieszk"],
    "area": [r"powierz", r"area", r"km2", r"km²"],
}

def _find_col(df: pd.DataFrame, keys: List[str]) -> Optional[str]:
    cols = list(df.columns)
    norm = {c: re.sub(r"\s+", "", str(c).strip().lower()) for c in cols}
    for key in keys:
        pat = re.compile(key, flags=re.I)
        for c in cols:
            if pat.search(norm[c]):
                return c
    return None

def _read_any(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in [".xls", ".xlsx"]:
        return pd.read_excel(path)
    # try common CSV separators
    for sep in [",", ";", "\t", "|"]:
        try:
            return pd.read_csv(path, sep=sep)
        except Exception:
            continue
    # fallback
    return pd.read_csv(path)

def load_many(path: str) -> pd.DataFrame:
    """Load CSV/XLSX from a file or all files in a directory and vertically concatenate."""
    if os.path.isdir(path):
        frames = []
        for root, _dirs, files in os.walk(path):
            for f in files:
                if f.lower().endswith((".csv", ".xlsx", ".xls")):
                    frames.append(_read_any(os.path.join(root, f)))
        if not frames:
            raise FileNotFoundError(f"No CSV/XLSX files found under {path}")
        return pd.concat(frames, ignore_index=True, sort=False)
    elif os.path.isfile(path):
        return _read_any(path)
    raise FileNotFoundError(f"{path} is neither a file nor a directory")

def normalize_columns(df: pd.DataFrame, kind: str) -> pd.DataFrame:
    """Standardize to canonical columns for a given dataset kind."""
    df = df.copy()
    m_code = _find_col(df, CANDIDATES["code"])
    m_year = _find_col(df, CANDIDATES["year"])
    if kind == "psp":
        m_val = _find_col(df, CANDIDATES["fires"])
        new = {"jst_code": m_code, "year": m_year, "fires": m_val}
    elif kind == "alcohol":
        m_val = _find_col(df, CANDIDATES["alcohol"])
        new = {"jst_code": m_code, "year": m_year, "alcohol_outlets": m_val}
    elif kind == "population":
        m_val = _find_col(df, CANDIDATES["population"])
        new = {"jst_code": m_code, "year": m_year, "population": m_val}
    elif kind == "area":
        m_val = _find_col(df, CANDIDATES["area"])
        # area may lack 'year'; treat as static if missing
        new = {"jst_code": m_code, "year": m_year, "area_km2": m_val}
    else:
        raise ValueError("Unknown kind")
    for k, v in new.items():
        if v is None and k != "year":  # year is optional for area
            raise KeyError(f"Could not auto-detect column for '{k}' in kind='{kind}'")
    out = pd.DataFrame({k: df[v] if v in df.columns else None for k, v in new.items()})
    return out
