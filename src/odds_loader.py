"""
Odds Loader

Carga y valida el dataset de cuotas
de CorrectScoreLab.

Permite seleccionar la temporada mediante
el nombre de la pestaña del Excel.

Formato esperado:
ESP_2021
ITA_2021
ENG_2021
GER_2021
FRA_2021
etc.
"""

from pathlib import Path

import pandas as pd


ODDS_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "correct_score_odds.xlsx"
)


# ==========================================================
# TEMPORADA ACTIVA
# ==========================================================

ODDS_SHEET = "ITA_2021"


def load_odds(sheet_name=None):

    print()
    print("=" * 60)
    print("ODDS LOADER")
    print("=" * 60)

    # Si no se especifica una pestaña,
    # utiliza la temporada activa configurada arriba.

    if sheet_name is None:
        sheet_name = ODDS_SHEET

    print(f"Temporada activa : {sheet_name}")

    # ======================================================
    # COMPROBAR ARCHIVO
    # ======================================================

    if not ODDS_FILE.exists():

        raise FileNotFoundError(
            f"No se encuentra el archivo de cuotas:\n{ODDS_FILE}"
        )

    # ======================================================
    # COMPROBAR PESTAÑA
    # ======================================================

    excel_file = pd.ExcelFile(ODDS_FILE)

    if sheet_name not in excel_file.sheet_names:

        raise ValueError(
            f"No existe la pestaña '{sheet_name}' "
            f"en el archivo de cuotas.\n"
            f"Pestañas disponibles: {excel_file.sheet_names}"
        )

    # ======================================================
    # CARGAR TEMPORADA
    # ======================================================

    df = pd.read_excel(
        ODDS_FILE,
        sheet_name=sheet_name
    )

    required_columns = [

        "FECHA",
        "LIGA",
        "LOCAL",
        "VISITANTE",
        "MARCADOR",
        "CUOTA",

    ]

    missing = [

        column

        for column in required_columns

        if column not in df.columns

    ]

    if missing:

        raise ValueError(
            f"Faltan columnas obligatorias: {missing}"
        )

    # ======================================================
    # NORMALIZACIÓN
    # ======================================================

    df["FECHA"] = pd.to_datetime(
        df["FECHA"],
        errors="coerce"
    )

    df["LOCAL"] = (
        df["LOCAL"]
        .astype(str)
        .str.strip()
    )

    df["VISITANTE"] = (
        df["VISITANTE"]
        .astype(str)
        .str.strip()
    )

    df["MARCADOR"] = (
        df["MARCADOR"]
        .astype(str)
        .str.strip()
    )

    df["CUOTA"] = pd.to_numeric(
        df["CUOTA"],
        errors="coerce"
    )

    # ======================================================
    # VALIDACIÓN
    # ======================================================

    invalid_dates = df["FECHA"].isna().sum()

    invalid_odds = df["CUOTA"].isna().sum()

    duplicates = df.duplicated(
        subset=[
            "FECHA",
            "LOCAL",
            "VISITANTE"
        ]
    ).sum()

    print()
    print(f"Partidos        : {len(df):,}")
    print(f"Fechas inválidas: {invalid_dates}")
    print(f"Cuotas inválidas: {invalid_odds}")
    print(f"Duplicados      : {duplicates}")

    if invalid_dates > 0:

        raise ValueError(
            "Existen fechas inválidas en el dataset de cuotas."
        )

    if invalid_odds > 0:

        raise ValueError(
            "Existen cuotas inválidas en el dataset de cuotas."
        )

    if duplicates > 0:

        raise ValueError(
            "Existen partidos duplicados en el dataset de cuotas."
        )

    print()
    print("Odds dataset OK")

    return df