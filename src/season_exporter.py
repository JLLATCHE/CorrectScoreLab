"""
Season Exporter

Exporta los resultados individuales de los partidos
con datos de cuotas para su análisis posterior.
"""

from pathlib import Path

import pandas as pd


OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "results"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "season_results.csv"
)


def export_season_results(df):

    print()
    print("=" * 60)
    print("SEASON EXPORTER")
    print("=" * 60)

    data = df.copy()

    # ==========================================================
    # CREAR CARPETA DE RESULTADOS
    # ==========================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ==========================================================
    # COLUMNAS BASE
    # ==========================================================

    base_columns = [

        "FECHA",
        "JORNADA",
        "LIGA",
        "LOCAL",
        "VISITANTE",
        "ODDS_REAL_SCORE",

        "TOP1",
        "TOP2",
        "TOP3",
        "TOP5",

        "P_TOP1",

        "ODDS_TOP1_HIT",
        "ODDS_TOP3_HIT",
        "ODDS_TOP5_HIT",

        "CUOTA",

    ]

    # ==========================================================
    # VARIABLES CS
    # ==========================================================

    cs_columns = sorted([

        column

        for column in data.columns

        if column.startswith("CS")

    ])

    # ==========================================================
    # COLUMNAS DISPONIBLES
    # ==========================================================

    export_columns = [

        column

        for column in base_columns + cs_columns

        if column in data.columns

    ]

    # ==========================================================
    # CREAR DATASET
    # ==========================================================

    result = data[
        export_columns
    ].copy()

    # Orden cronológico

    if "FECHA" in result.columns:

        result = result.sort_values(
            by="FECHA"
        )

    # ==========================================================
    # EXPORTAR
    # ==========================================================

    result.to_csv(

        OUTPUT_FILE,

        index=False,

        encoding="utf-8-sig"

    )

    # ==========================================================
    # RESULTADOS
    # ==========================================================

    print(
        f"Partidos exportados : "
        f"{len(result):,}"
    )

    print(
        f"Variables CS        : "
        f"{len(cs_columns):,}"
    )

    print(
        f"Columnas totales    : "
        f"{len(export_columns):,}"
    )

    print()
    print(
        f"Archivo creado:"
    )

    print(
        OUTPUT_FILE
    )

    return result