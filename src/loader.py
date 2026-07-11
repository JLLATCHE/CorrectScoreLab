from pathlib import Path
import pandas as pd

DATA_PATH = Path("data/raw")


def load_data():

    files = sorted(DATA_PATH.glob("*.csv"))

    if not files:
        raise FileNotFoundError("No hay archivos CSV en data/raw")

    dfs = []

    for file in files:

        df = pd.read_csv(file, encoding="utf-8").copy()

        league, season = file.stem.split("_")

        df = df.assign(
            LEAGUE=league,
            SEASON=season,
            SOURCE_FILE=file.name
        )

        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    df["Date"] = pd.to_datetime(
        df["Date"],
        dayfirst=True,
        errors="coerce"
    )

    df = df.sort_values("Date").reset_index(drop=True)

    return df