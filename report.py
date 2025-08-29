from __future__ import annotations
import json
import pandas as pd
from typing import Optional

def write_report(summary: dict, merged: pd.DataFrame, output_path: str, save_merged: Optional[str] = None) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    if save_merged:
        merged.to_csv(save_merged, index=False)
