"""
Core Profile Summary V0.1

Resume automáticamente el histórico generado por
Core Profile Analyzer.

Objetivos:
- Comparar perfiles entre temporadas.
- Medir estabilidad.
- Medir volumen.
- Medir rentabilidad agregada.
- Detectar candidatos para CORE V1.

Fuente:
data/results/core_profile_history.csv
"""


from pathlib import Path

import pandas as pd


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

HISTORY_FILE = (
    BASE_DIR
    / "data"
    / "results"
    / "core_profile_history.csv"
)


# ==========================================================
# FORMATO
# ==========================================================

def _format_percent(value):

    if pd.isna(value):
        return "0.00%"

    return f"{value:.2%}"


# ==========================================================
# RESUMEN POR NIVEL
# ==========================================================

def _print_level_summary(
    df,
    level
):

    level_df = df[
        df["LEVEL"] == level
    ].copy()

    if level_df.empty:
        return

    print()
    print("=" * 110)
    print(level)
    print("=" * 110)

    print(
        f"{'PROFILE':22}"
        f"{'TEMP':>7}"
        f"{'POS':>8}"
        f"{'SIGNALS':>10}"
        f"{'HITS':>8}"
        f"{'HIT%':>10}"
        f"{'RETURN':>12}"
        f"{'PROFIT':>12}"
        f"{'ROI':>12}"
    )

    print("-" * 110)

    profiles = (
        level_df["PROFILE"]
        .dropna()
        .unique()
    )

    summary_rows = []

    for profile in profiles:

        profile_df = level_df[
            level_df["PROFILE"] == profile
        ].copy()

        seasons = len(
            profile_df
        )

        positive_seasons = int(
            (
                profile_df["PROFIT"] > 0
            ).sum()
        )

        signals = float(
            profile_df["SIGNALS"].sum()
        )

        hits = float(
            profile_df["HITS"].sum()
        )

        total_return = float(
            profile_df["RETURN"].sum()
        )

        total_profit = float(
            profile_df["PROFIT"].sum()
        )

        hit_rate = (
            hits
            /
            signals
            if signals > 0
            else 0.0
        )

        roi = (
            total_profit
            /
            signals
            if signals > 0
            else 0.0
        )

        summary_rows.append({

            "PROFILE":
                profile,

            "TEMP":
                seasons,

            "POS":
                positive_seasons,

            "SIGNALS":
                signals,

            "HITS":
                hits,

            "HIT_RATE":
                hit_rate,

            "RETURN":
                total_return,

            "PROFIT":
                total_profit,

            "ROI":
                roi,

        })

    summary = pd.DataFrame(
        summary_rows
    )

    # ======================================================
    # ORDENAR
    # ======================================================
    #
    # Primero estabilidad.
    # Después ROI.
    # Después volumen.
    #
    # ======================================================

    summary["POS_RATE"] = (

        summary["POS"]

        /

        summary["TEMP"]

    )

    summary = summary.sort_values(

        by=[

            "POS_RATE",
            "ROI",
            "SIGNALS",

        ],

        ascending=[

            False,
            False,
            False,

        ]

    )

    # ======================================================
    # MOSTRAR
    # ======================================================

    for _, row in summary.iterrows():

        positive_text = (

            f"{int(row['POS'])}/"
            f"{int(row['TEMP'])}"

        )

        print(

            f"{row['PROFILE']:22}"

            f"{int(row['TEMP']):>7}"

            f"{positive_text:>8}"

            f"{int(row['SIGNALS']):>10}"

            f"{int(row['HITS']):>8}"

            f"{row['HIT_RATE']:>9.2%}"

            f"{row['RETURN']:>12.2f}"

            f"{row['PROFIT']:>+12.2f}"

            f"{row['ROI']:>11.2%}"

        )


# ==========================================================
# DETALLE DE CANDIDATO
# ==========================================================

def _print_candidate_detail(
    df,
    level,
    profile
):

    candidate = df[

        (df["LEVEL"] == level)

        &

        (df["PROFILE"] == profile)

    ].copy()

    if candidate.empty:
        return

    candidate = candidate.sort_values(
        "SEASON"
    )

    print()
    print("=" * 110)

    print(
        f"CANDIDATO: {level} / {profile}"
    )

    print("=" * 110)

    print(

        f"{'SEASON':15}"

        f"{'SIGNALS':>10}"

        f"{'HITS':>8}"

        f"{'HIT%':>10}"

        f"{'AVG ODDS':>12}"

        f"{'PROFIT':>12}"

        f"{'ROI':>12}"

    )

    print("-" * 110)

    for _, row in candidate.iterrows():

        print(

            f"{row['SEASON']:15}"

            f"{int(row['SIGNALS']):>10}"

            f"{int(row['HITS']):>8}"

            f"{row['HIT_RATE']:>9.2%}"

            f"{row['AVG_ODDS']:>12.2f}"

            f"{row['PROFIT']:>+12.2f}"

            f"{row['ROI']:>11.2%}"

        )


# ==========================================================
# ANALIZADOR PRINCIPAL
# ==========================================================

def analyze_core_profile_summary():

    print()
    print("=" * 110)
    print("CORE PROFILE SUMMARY V0.1")
    print("=" * 110)

    # ======================================================
    # VALIDAR HISTÓRICO
    # ======================================================

    if not HISTORY_FILE.exists():

        print()
        print(
            "No existe histórico CORE PROFILE."
        )

        print(
            HISTORY_FILE
        )

        return None

    # ======================================================
    # CARGAR HISTÓRICO
    # ======================================================

    df = pd.read_csv(
        HISTORY_FILE
    )

    if df.empty:

        print()
        print(
            "El histórico CORE PROFILE está vacío."
        )

        return None

    # ======================================================
    # CONVERTIR COLUMNAS NUMÉRICAS
    # ======================================================

    numeric_columns = [

        "SIGNALS",
        "HITS",
        "HIT_RATE",
        "AVG_ODDS",
        "STAKE",
        "RETURN",
        "PROFIT",
        "ROI",

    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).fillna(0.0)

    # ======================================================
    # INFORMACIÓN GENERAL
    # ======================================================

    seasons = sorted(
        df["SEASON"]
        .dropna()
        .unique()
        .tolist()
    )

    print()
    print(
        f"Temporadas analizadas : "
        f"{len(seasons)}"
    )

    print(
        f"Temporadas             : "
        f"{', '.join(seasons)}"
    )

    # ======================================================
    # RESUMEN POR NIVEL
    # ======================================================

    for level in [

        "CORE_A",
        "CORE_B",
        "CORE_C",

    ]:

        _print_level_summary(
            df=df,
            level=level
        )

    # ======================================================
    # CANDIDATO CORE B ACTUAL
    # ======================================================

    _print_candidate_detail(

        df=df,

        level="CORE_B",

        profile="DOM50_AWAY100",

    )

    print()
    print("=" * 110)
    print(
        "FIN CORE PROFILE SUMMARY V0.1"
    )
    print("=" * 110)

    return df


# ==========================================================
# EJECUCIÓN INDEPENDIENTE
# ==========================================================

if __name__ == "__main__":

    analyze_core_profile_summary()