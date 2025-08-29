import pandas as pd
from jstrisk.analysis import run_analysis

def test_run_analysis_minimal(tmp_path):
    # Create small CSVs
    p = tmp_path / "psp.csv"
    a = tmp_path / "alcohol.csv"
    pop = tmp_path / "pop.csv"
    area = tmp_path / "area.csv"

    pd.DataFrame({
        "JST": ["1234567", "1234567", "7654321"],
        "Rok": [2020, 2021, 2020],
        "Interwencje": [10, 12, 5],
    }).to_csv(p, index=False)

    pd.DataFrame({
        "Kod": ["1234567", "7654321"],
        "Rok": [2020, 2020],
        "Zezwolenia": [100, 50],
    }).to_csv(a, index=False)

    pd.DataFrame({
        "jst_code": ["1234567", "7654321"],
        "year": [2020, 2020],
        "population": [10000, 5000],
    }).to_csv(pop, index=False)

    pd.DataFrame({
        "TERYT": ["1234567", "7654321"],
        "Area_km2": [50, 25],
    }).to_csv(area, index=False)

    summary, merged = run_analysis(str(p), str(a), str(pop), str(area), jst_code_length=7)
    assert "stats" in summary and "correlations" in summary
    assert len(merged) >= 1
