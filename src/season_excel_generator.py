"""
Season Excel Generator

Convierte automáticamente los CSV históricos
al formato utilizado por CorrectScoreLab.

Genera los Excel de las temporadas configuradas con:

FECHA
LIGA
LOCAL
VISITANTE
MARCADOR
CUOTA
"""

from pathlib import Path

import pandas as pd


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = (
    BASE_DIR
    / "data"
    / "raw"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "generated"
)


# ==========================================================
# TEMPORADAS A GENERAR
# ==========================================================

SEASONS = [

    {
        "input_file": "ENG_2022.csv",
        "league": "INGLATERRA",
        "season": "2022_23",
    },

    {
        "input_file": "ITA_2022.csv",
        "league": "ITALIA",
        "season": "2022_23",
    },

    {
        "input_file": "GER_2022.csv",
        "league": "ALEMANIA",
        "season": "2022_23",
    },

    {
        "input_file": "FRA_2022.csv",
        "league": "FRANCIA",
        "season": "2022_23",
    },

]


# ==========================================================
# GENERADOR INDIVIDUAL
# ==========================================================

def generate_season_excel(
    input_file,
    league,
    season
):

    print()
    print("=" * 60)
    print("SEASON EXCEL GENERATOR")
    print("=" * 60)

    input_path = (
        INPUT_DIR
        / input_file
    )

    if not input_path.exists():

        print(
            f"ERROR - No se encuentra:"
        )

        print(
            input_path
        )

        return None

    # ======================================================
    # CARGAR CSV
    # ======================================================

    df = pd.read_csv(
        input_path
    )

    required_columns = [

        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG",

    ]

    missing = [

        column

        for column in required_columns

        if column not in df.columns

    ]

    if missing:

        print(
            f"ERROR - Faltan columnas: "
            f"{missing}"
        )

        return None

    # ======================================================
    # CREAR DATASET
    # ======================================================

    result = pd.DataFrame()

    # FECHA

    result["FECHA"] = pd.to_datetime(

        df["Date"],

        dayfirst=True,

        errors="coerce"

    )

    # LIGA

    result["LIGA"] = league

    # LOCAL

    result["LOCAL"] = (

        df["HomeTeam"]
        .astype(str)
        .str.strip()
        .str.upper()

    )

    # VISITANTE

    result["VISITANTE"] = (

        df["AwayTeam"]
        .astype(str)
        .str.strip()
        .str.upper()

    )

    # ======================================================
    # MARCADOR
    # ======================================================

    result["MARCADOR"] = (

        df["FTHG"]
        .astype("Int64")
        .astype(str)

        +

        "-"

        +

        df["FTAG"]
        .astype("Int64")
        .astype(str)

    )

    # ======================================================
    # CUOTA
    # ======================================================

    result["CUOTA"] = None

    # ======================================================
    # VALIDACIÓN
    # ======================================================

    invalid_dates = (
        result["FECHA"].isna().sum()
    )

    invalid_scores = (

        df["FTHG"].isna()

        |

        df["FTAG"].isna()

    ).sum()

    duplicates = result.duplicated(

        subset=[

            "FECHA",
            "LOCAL",
            "VISITANTE",

        ]

    ).sum()

    # ======================================================
    # ORDENAR
    # ======================================================

    result = result.sort_values(

        by="FECHA"

    ).reset_index(

        drop=True

    )

    # ======================================================
    # CREAR CARPETA
    # ======================================================

    OUTPUT_DIR.mkdir(

        parents=True,

        exist_ok=True

    )

    # ======================================================
    # ARCHIVO DE SALIDA
    # ======================================================

    output_file = (

        OUTPUT_DIR

        /

        f"{league}_{season}.xlsx"

    )

    # ======================================================
    # EXPORTAR
    # ======================================================

    result.to_excel(

        output_file,

        index=False

    )

    # ======================================================
    # RESULTADOS
    # ======================================================

    print(
        f"Liga             : "
        f"{league}"
    )

    print(
        f"Temporada        : "
        f"{season}"
    )

    print(
        f"Partidos         : "
        f"{len(result):,}"
    )

    print(
        f"Fechas inválidas : "
        f"{invalid_dates:,}"
    )

    print(
        f"Marcadores inv.  : "
        f"{invalid_scores:,}"
    )

    print(
        f"Duplicados       : "
        f"{duplicates:,}"
    )

    print()

    print(
        "Archivo creado:"
    )

    print(
        output_file
    )

    return result


# ==========================================================
# GENERADOR MÚLTIPLE
# ==========================================================

def generate_all_seasons():

    print()
    print("=" * 60)
    print("GENERANDO TEMPORADAS")
    print("=" * 60)

    total_matches = 0

    generated = 0

    failed = 0

    for config in SEASONS:

        result = generate_season_excel(

            input_file=config["input_file"],

            league=config["league"],

            season=config["season"]

        )

        if result is not None:

            generated += 1

            total_matches += len(result)

        else:

            failed += 1

    # ======================================================
    # RESUMEN FINAL
    # ======================================================

    print()
    print("=" * 60)
    print("RESUMEN GENERACIÓN")
    print("=" * 60)

    print(
        f"Temporadas generadas : "
        f"{generated}"
    )

    print(
        f"Temporadas fallidas  : "
        f"{failed}"
    )

    print(
        f"Partidos totales     : "
        f"{total_matches:,}"
    )

    print()
    print(
        f"Carpeta:"
    )

    print(
        OUTPUT_DIR
    )


# ==========================================================
# EJECUCIÓN
# ==========================================================

if __name__ == "__main__":

    generate_all_seasons()