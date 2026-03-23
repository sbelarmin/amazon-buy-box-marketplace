from pathlib import Path
from datetime import datetime
import pandas as pd

def save_df(df, filepath: str, filetype: str = "csv", timestamp: bool = False):
    if timestamp:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"{filepath}_{ts}"
    
    path = Path(f"{filepath}.{filetype}")
    path.parent.mkdir(parents=True, exist_ok=True)

    if filetype == "csv":
        df.to_csv(path, index=False)
    elif filetype == "parquet":
        df.to_parquet(path, index=False)
    elif filetype == "xlsx":
        df.to_excel(path, index=False)
    else:
        raise ValueError(f"Unsupported filetype: {filetype}")

    print(f"Saved to: {path}")
