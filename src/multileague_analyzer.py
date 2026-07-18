"""
MultiLeague Analyzer V0.1

Analiza los resultados históricos registrados por
MultiLeague Validation Engine.

Objetivos:
- Comparar rendimiento por temporada.
- Comparar rendimiento agregado por liga.
- Analizar CORE, RARE HOME y RARE AWAY.
- Separar DEVELOPMENT de VALIDATION.
- Preparar el análisis futuro de múltiples temporadas.
"""

from pathlib import Path

import pandas as pd


RESULTS_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "results"
    / "multileague_validation.csv"
)


def analyze_multileague():

    print()
    print("=" * 100)
    print("MULTILEAGUE ANALYZER V0.1")
    print("=" * 100)

    # ======================================================
    # VALIDAR ARCHIVO
    # ======================================================

    if not RESULTS_FILE.exists():

        print()
        print(
            "No existe todavía histórico multiliga."
        )

        return None

    df = pd.read_csv(
        RESULTS_FILE
    )

    if df.empty:

        print()
        print(
            "El histórico multiliga está vacío."
        )

        return None

    # ======================================================
    # EXTRAER LIGA Y AÑO
    #
    # Ejemplo:
    # ESP_2021 -> LIGA ESP / AÑO 2021
    # ======================================================

    df["LEAGUE"] = (
        df["SEASON"]
        .astype(str)
        .str.split("_")
        .str[0]
    )

    df["YEAR"] = (
        df["SEASON"]
        .astype(str)
        .str.split("_")
        .str[-1]
    )

    # ======================================================
    # RESUMEN POR TEMPORADA
    # ======================================================

    season_summary = df[
        [
            "SEASON",
            "LEAGUE",
            "YEAR",
            "SAMPLE_TYPE",

            "CORE_SIGNALS",
            "CORE_PROFIT",
            "CORE_ROI",

            "RARE_HOME_SIGNALS",
            "RARE_HOME_PROFIT",
            "RARE_HOME_ROI",

            "RARE_AWAY_SIGNALS",
            "RARE_AWAY_PROFIT",
            "RARE_AWAY_ROI",

            "PORTFOLIO_MATCHES",
            "PORTFOLIO_STAKE",
            "PORTFOLIO_RETURN",
            "PORTFOLIO_PROFIT",
            "PORTFOLIO_ROI",

            "MAX_DRAWDOWN",
            "MAX_LOSING_STREAK",
        ]
    ].copy()

    # ======================================================
    # RESUMEN POR LIGA
    #
    # IMPORTANTE:
    # ROI agregado = Profit total / Stake total
    # No utilizamos media simple de ROI.
    # ======================================================

    league_rows = []

    for league, group in df.groupby(
        "LEAGUE"
    ):

        core_stake = group[
            "CORE_STAKE"
        ].sum()

        core_profit = group[
            "CORE_PROFIT"
        ].sum()

        rare_home_stake = group[
            "RARE_HOME_STAKE"
        ].sum()

        rare_home_profit = group[
            "RARE_HOME_PROFIT"
        ].sum()

        rare_away_stake = group[
            "RARE_AWAY_STAKE"
        ].sum()

        rare_away_profit = group[
            "RARE_AWAY_PROFIT"
        ].sum()

        portfolio_stake = group[
            "PORTFOLIO_STAKE"
        ].sum()

        portfolio_profit = group[
            "PORTFOLIO_PROFIT"
        ].sum()

        league_rows.append(
            {
                "LEAGUE":
                    league,

                "SEASONS":
                    len(group),

                "CORE_SIGNALS":
                    group[
                        "CORE_SIGNALS"
                    ].sum(),

                "CORE_STAKE":
                    core_stake,

                "CORE_PROFIT":
                    core_profit,

                "CORE_ROI":
                    (
                        core_profit
                        /
                        core_stake
                        if core_stake > 0
                        else 0
                    ),

                "RARE_HOME_SIGNALS":
                    group[
                        "RARE_HOME_SIGNALS"
                    ].sum(),

                "RARE_HOME_STAKE":
                    rare_home_stake,

                "RARE_HOME_PROFIT":
                    rare_home_profit,

                "RARE_HOME_ROI":
                    (
                        rare_home_profit
                        /
                        rare_home_stake
                        if rare_home_stake > 0
                        else 0
                    ),

                "RARE_AWAY_SIGNALS":
                    group[
                        "RARE_AWAY_SIGNALS"
                    ].sum(),

                "RARE_AWAY_STAKE":
                    rare_away_stake,

                "RARE_AWAY_PROFIT":
                    rare_away_profit,

                "RARE_AWAY_ROI":
                    (
                        rare_away_profit
                        /
                        rare_away_stake
                        if rare_away_stake > 0
                        else 0
                    ),

                "PORTFOLIO_STAKE":
                    portfolio_stake,

                "PORTFOLIO_PROFIT":
                    portfolio_profit,

                "PORTFOLIO_ROI":
                    (
                        portfolio_profit
                        /
                        portfolio_stake
                        if portfolio_stake > 0
                        else 0
                    ),

                "AVG_MAX_DRAWDOWN":
                    group[
                        "MAX_DRAWDOWN"
                    ].mean(),

                "WORST_MAX_DRAWDOWN":
                    group[
                        "MAX_DRAWDOWN"
                    ].max(),
            }
        )

    league_summary = pd.DataFrame(
        league_rows
    )

    league_summary = (
        league_summary
        .sort_values(
            "PORTFOLIO_ROI",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    # ======================================================
    # VALIDACIÓN EXTERNA GLOBAL
    # ======================================================

    validation = df[
        df["SAMPLE_TYPE"]
        ==
        "VALIDATION"
    ].copy()

    validation_summary = None

    if not validation.empty:

        total_stake = validation[
            "PORTFOLIO_STAKE"
        ].sum()

        total_profit = validation[
            "PORTFOLIO_PROFIT"
        ].sum()

        validation_summary = {
            "SEASONS":
                len(validation),

            "LEAGUES":
                validation[
                    "LEAGUE"
                ].nunique(),

            "STAKE":
                total_stake,

            "PROFIT":
                total_profit,

            "ROI":
                (
                    total_profit
                    /
                    total_stake
                    if total_stake > 0
                    else 0
                ),

            "POSITIVE_SEASONS":
                (
                    validation[
                        "PORTFOLIO_PROFIT"
                    ]
                    > 0
                ).sum(),
        }

    # ======================================================
    # MOSTRAR RESUMEN POR LIGA
    # ======================================================

    print()
    print("RENDIMIENTO AGREGADO POR LIGA")
    print("-" * 100)

    print(
        f"{'LIGA':8}"
        f"{'TEMP':>7}"
        f"{'CORE SIG':>11}"
        f"{'CORE ROI':>12}"
        f"{'RH SIG':>10}"
        f"{'RH ROI':>12}"
        f"{'RA SIG':>10}"
        f"{'RA ROI':>12}"
        f"{'PORT ROI':>12}"
        f"{'PROFIT':>12}"
    )

    print("-" * 100)

    for _, row in (
        league_summary.iterrows()
    ):

        print(
            f"{row['LEAGUE']:8}"

            f"{int(row['SEASONS']):>7}"

            f"{int(row['CORE_SIGNALS']):>11}"

            f"{row['CORE_ROI']:>11.2%}"

            f"{int(row['RARE_HOME_SIGNALS']):>10}"

            f"{row['RARE_HOME_ROI']:>11.2%}"

            f"{int(row['RARE_AWAY_SIGNALS']):>10}"

            f"{row['RARE_AWAY_ROI']:>11.2%}"

            f"{row['PORTFOLIO_ROI']:>11.2%}"

            f"{row['PORTFOLIO_PROFIT']:>+12.2f}"
        )

    # ======================================================
    # MOSTRAR VALIDACIÓN GLOBAL
    # ======================================================

    if validation_summary:

        print()
        print("=" * 100)
        print("VALIDACIÓN EXTERNA GLOBAL")
        print("=" * 100)

        print(
            f"Ligas               : "
            f"{validation_summary['LEAGUES']}"
        )

        print(
            f"Temporadas          : "
            f"{validation_summary['SEASONS']}"
        )

        print(
            f"Temporadas positivas: "
            f"{validation_summary['POSITIVE_SEASONS']}"
            f"/"
            f"{validation_summary['SEASONS']}"
        )

        print(
            f"Stake               : "
            f"{validation_summary['STAKE']:.2f}"
        )

        print(
            f"Profit              : "
            f"{validation_summary['PROFIT']:+.2f}"
        )

        print(
            f"ROI                 : "
            f"{validation_summary['ROI']:+.2%}"
        )

    return {
        "season_summary":
            season_summary,

        "league_summary":
            league_summary,

        "validation_summary":
            validation_summary,
    }