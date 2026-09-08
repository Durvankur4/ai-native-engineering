"""Optional loader for public historical LLMDrift generation CSVs.

The project can run fully offline using the bundled synthetic testbed. When network access
or the dataset is available, this module normalizes LLMDrift rows into monitor observations.
"""
from pathlib import Path
import pandas as pd

EXPECTED_HINTS=("model","query","reference","generation","latency")

def load_llmdrift_csv(path: str) -> pd.DataFrame:
    df=pd.read_csv(path)
    cols={c.lower():c for c in df.columns}
    required=[x for x in ("query","reference answer","generated answer") if x in cols]
    if len(required)<3:
        raise ValueError(f"Could not find enough LLMDrift fields. Columns: {list(df.columns)}")
    return df
