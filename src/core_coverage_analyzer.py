"""
Core Coverage Analyzer V0.2

Analiza la cobertura del motor CORE en la temporada activa
y mantiene un histórico persistente por temporada.

Objetivos:
- Medir cuántos partidos analiza la temporada.
- Medir cuántos partidos activa CORE.
- Calcular el porcentaje de cobertura CORE.
- Analizar la probabilidad P_TOP1 de las señales CORE.
- Analizar los marcadores seleccionados por CORE.
- Guardar histórico de cobertura por temporada.
- Evitar duplicados al volver a ejecutar una temporada.
- Preparar información para análisis multiliga.
- Preparar datos para integración futura en Excel.

Archivo generado:
data/results/core_coverage_history.csv

Este módulo NO modifica:
- Predicciones.
- Selecciones.
- Stakes.
- Resultados.
- Portfolio.

Es exclusivamente un módulo de análisis.
"""

from pathlib import Path

import pandas as pd


# ==========================================================
# ARCHIVO HISTÓRICO
# ==========================================================

HISTORY_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "results"
    / "core_coverage_history.csv"
)


def analyze_core_coverage(
    portfolio_result,
    season_name
):

    print()
    print("=" * 100)
    print("CORE COVERAGE ANALYZER V0.2")
    print("=" * 100)

    # ======================================================
    # VALIDACIÓN
    # ======================================================

    if "portfolio" not in portfolio_result:

        raise ValueError(
            "portfolio_result no contiene la clave 'portfolio'."
        )

    portfolio = (
        portfolio_result["portfolio"]
        .copy()
    )

    required_columns = [
        "CORE_ACTIVE",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in portfolio.columns
    ]

    if missing_columns:

        raise ValueError(
            "Faltan columnas para Core Coverage Analyzer: "
            f"{missing_columns}"
        )

    # ======================================================
    # IDENTIFICAR LIGA
    #
    # Ejemplo:
    # ESP_2021 -> ESP
    # FRA_2021 -> FRA
    # GER_2021 -> GER
    # ======================================================

    league = str(
        season_name
    ).split("_")[0]

    # ======================================================
    # DATOS GENERALES
    # ======================================================

    total_matches = len(
        portfolio
    )

    core = portfolio[
        portfolio["CORE_ACTIVE"] == True
    ].copy()

    core_matches = len(
        core
    )

    coverage = (
        core_matches
        /
        total_matches
        if total_matches > 0
        else 0
    )

    # ======================================================
    # PROBABILIDAD CORE
    # ======================================================

    if (
        "P_TOP1" in core.columns
        and core_matches > 0
    ):

        average_p = core[
            "P_TOP1"
        ].mean()

        min_p = core[
            "P_TOP1"
        ].min()

        max_p = core[
            "P_TOP1"
        ].max()

    else:

        average_p = 0
        min_p = 0
        max_p = 0

    # ======================================================
    # RESULTADOS CORE
    # ======================================================

    core_summary = portfolio_result.get(
        "core",
        {}
    )

    core_stake = core_summary.get(
        "stake",
        0
    )

    core_return = core_summary.get(
        "return",
        0
    )

    core_profit = core_summary.get(
        "profit",
        0
    )

    core_roi = core_summary.get(
        "roi",
        0
    )

    # ======================================================
    # MARCADORES CORE
    # ======================================================

    score_distribution = pd.DataFrame(
        columns=[
            "MARCADOR",
            "SEÑALES",
            "PORCENTAJE",
        ]
    )

    if (
        "TOP1" in core.columns
        and core_matches > 0
    ):

        score_distribution = (
            core["TOP1"]
            .value_counts()
            .rename_axis("MARCADOR")
            .reset_index(name="SEÑALES")
        )

        score_distribution[
            "PORCENTAJE"
        ] = (
            score_distribution["SEÑALES"]
            /
            core_matches
        )

    # ======================================================
    # RESUMEN TEMPORADA
    # ======================================================

    summary = pd.DataFrame(
        [
            {
                "TEMPORADA":
                    season_name,

                "LIGA":
                    league,

                "PARTIDOS":
                    total_matches,

                "CORE_SEÑALES":
                    core_matches,

                "CORE_COBERTURA":
                    coverage,

                "CORE_P_MEDIA":
                    average_p,

                "CORE_P_MIN":
                    min_p,

                "CORE_P_MAX":
                    max_p,

                "CORE_STAKE":
                    core_stake,

                "CORE_RETURN":
                    core_return,

                "CORE_PROFIT":
                    core_profit,

                "CORE_ROI":
                    core_roi,
            }
        ]
    )

    # ======================================================
    # CREAR DIRECTORIO
    # ======================================================

    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ======================================================
    # CARGAR HISTÓRICO
    # ======================================================

    if HISTORY_FILE.exists():

        history = pd.read_csv(
            HISTORY_FILE
        )

        # Eliminar registro anterior de la misma temporada.
        # Así podemos ejecutar varias veces sin duplicar.

        if "TEMPORADA" in history.columns:

            history = history[
                history["TEMPORADA"]
                != season_name
            ].copy()

        history = pd.concat(
            [
                history,
                summary,
            ],
            ignore_index=True
        )

    else:

        history = summary.copy()

    # ======================================================
    # ORDENAR HISTÓRICO
    # ======================================================

    history = history.sort_values(
        [
            "LIGA",
            "TEMPORADA",
        ]
    ).reset_index(
        drop=True
    )

    # ======================================================
    # GUARDAR HISTÓRICO
    # ======================================================

    history.to_csv(
        HISTORY_FILE,
        index=False
    )

    # ======================================================
    # SALIDA CONSOLA
    # ======================================================

    print()
    print(f"Temporada       : {season_name}")
    print(f"Liga            : {league}")
    print(f"Partidos        : {total_matches}")
    print(f"Señales CORE    : {core_matches}")
    print(f"Cobertura CORE  : {coverage:.2%}")

    print()

    print(
        f"P media CORE    : "
        f"{average_p:.2%}"
    )

    print(
        f"P mínima CORE   : "
        f"{min_p:.2%}"
    )

    print(
        f"P máxima CORE   : "
        f"{max_p:.2%}"
    )

    print()

    print(
        f"Stake CORE      : "
        f"{core_stake:.2f}"
    )

    print(
        f"Retorno CORE    : "
        f"{core_return:.2f}"
    )

    print(
        f"Profit CORE     : "
        f"{core_profit:+.2f}"
    )

    print(
        f"ROI CORE        : "
        f"{core_roi:+.2%}"
    )

    # ======================================================
    # MARCADORES CORE
    # ======================================================

    if len(score_distribution) > 0:

        print()
        print("MARCADORES CORE")
        print("-" * 50)

        for _, row in score_distribution.iterrows():

            print(
                f"{row['MARCADOR']:8} "
                f"{int(row['SEÑALES']):4} "
                f"{row['PORCENTAJE']:8.2%}"
            )

    # ======================================================
    # HISTÓRICO CORE
    # ======================================================

    print()
    print("HISTÓRICO CORE COVERAGE")
    print("-" * 100)

    print(
        f"{'TEMPORADA':12}"
        f"{'LIGA':8}"
        f"{'PARTIDOS':>10}"
        f"{'CORE':>8}"
        f"{'COVERAGE':>12}"
        f"{'P MEDIA':>12}"
        f"{'PROFIT':>12}"
        f"{'ROI':>12}"
    )

    print("-" * 100)

    for _, row in history.iterrows():

        print(
            f"{row['TEMPORADA']:12}"
            f"{row['LIGA']:8}"
            f"{int(row['PARTIDOS']):>10}"
            f"{int(row['CORE_SEÑALES']):>8}"
            f"{row['CORE_COBERTURA']:>11.2%}"
            f"{row['CORE_P_MEDIA']:>11.2%}"
            f"{row['CORE_PROFIT']:>+12.2f}"
            f"{row['CORE_ROI']:>11.2%}"
        )

    print()
    print(
        f"Histórico guardado en:\n"
        f"{HISTORY_FILE}"
    )

    # ======================================================
    # RETURN
    # ======================================================

    return {
        "summary":
            summary,

        "scores":
            score_distribution,

        "core_matches":
            core,

        "history":
            history,
    }