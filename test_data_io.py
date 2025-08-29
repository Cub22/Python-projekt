import pandas as pd
from jstrisk.data_io import normalize_columns

def test_normalize_columns_psp():
    df = pd.DataFrame({"JST": ["1"], "Rok": [2020], "Interwencje": [5]})
    out = normalize_columns(df, "psp")
    assert set(["jst_code","year","fires"]).issubset(out.columns)
