"""
Excel Output Engine V0.1

Genera el Excel operativo base de CorrectScoreLab V1.

Esta primera versión utiliza datos de BACKTEST para
construir y validar la estructura que posteriormente
utilizará el modo LIVE.

Archivo generado:
data/results/CorrectScoreLab_V1.xlsx
"""

from pathlib import Path

import pandas as pd


OUTPUT_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "results"
    / "CorrectScoreLab_V1.xlsx"
)

VALIDATION_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "results"
    / "multileague_validation.csv"
)


def export_excel_v1(
    odds_result,
    portfolio_result,
    bet_selections,
    season_name
):

    print()
    print("=" * 100)
    print("EXCEL OUTPUT ENGINE V0.1")
    print("=" * 100)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ======================================================
    # DATOS PORTFOLIO
    # ======================================================

    portfolio = (
        portfolio_result["portfolio"]
        .copy()
    )

    active = (
        portfolio_result["active"]
        .copy()
    )

    core_summary = portfolio_result["core"]
    rare_home_summary = portfolio_result["rare_home"]
    rare_away_summary = portfolio_result["rare_away"]
    total_summary = portfolio_result["total"]

    # ======================================================
    # DASHBOARD
    # ======================================================

    dashboard = pd.DataFrame(
        [
            {
                "METRICA": "TEMPORADA",
                "VALOR": season_name,
            },
            {
                "METRICA": "MODO",
                "VALOR": "BACKTEST",
            },
            {
                "METRICA": "PARTIDOS ANALIZADOS",
                "VALOR": len(portfolio),
            },
            {
                "METRICA": "PARTIDOS APOSTADOS",
                "VALOR": total_summary["matches"],
            },
            {
                "METRICA": "STAKE TOTAL",
                "VALOR": total_summary["stake"],
            },
            {
                "METRICA": "RETORNO",
                "VALOR": total_summary["return"],
            },
            {
                "METRICA": "BENEFICIO",
                "VALOR": total_summary["profit"],
            },
            {
                "METRICA": "ROI",
                "VALOR": total_summary["roi"],
            },
            {
                "METRICA": "MAX DRAWDOWN",
                "VALOR": total_summary["max_drawdown"],
            },
            {
                "METRICA": "MAX RACHA NEGATIVA",
                "VALOR": total_summary["max_losing_streak"],
            },
        ]
    )

    # ======================================================
    # JORNADA
    # Todos los partidos analizados
    # ======================================================

    jornada_columns = [
        "FECHA",
        "LOCAL",
        "VISITANTE",
        "REAL_SCORE",
        "TOP1",
        "P_TOP1",
        "CORE_ACTIVE",
        "RARE_HOME_ACTIVE",
        "RARE_AWAY_ACTIVE",
        "ACTIVE_ENGINES",
        "TOTAL_STAKE",
        "TOTAL_RETURN",
        "TOTAL_PROFIT",
    ]

    jornada_columns = [
        column
        for column in jornada_columns
        if column in portfolio.columns
    ]

    jornada = portfolio[
        jornada_columns
    ].copy()

    # ======================================================
    # SELECCIONES
    # Una fila = una apuesta real
    # ======================================================

    selections = (
         bet_selections
        .copy()
    )

    # ======================================================
    # CORE
    # ======================================================

    core = portfolio[
        portfolio["CORE_ACTIVE"]
        == True
    ].copy()

    # ======================================================
    # RARE
    # ======================================================

    rare = portfolio[
        (
            portfolio["RARE_HOME_ACTIVE"]
            == True
        )
        |
        (
            portfolio["RARE_AWAY_ACTIVE"]
            == True
        )
    ].copy()

    # ======================================================
    # HISTÓRICO
    # Primera versión basada en backtest
    # ======================================================

    historico = active.copy()

    historico["BANK"] = (
        historico["TOTAL_PROFIT"]
        .cumsum()
    )

    historico["CUM_STAKE"] = (
        historico["TOTAL_STAKE"]
        .cumsum()
    )

    historico["CUM_RETURN"] = (
        historico["TOTAL_RETURN"]
        .cumsum()
    )

    historico["CUM_PROFIT"] = (
        historico["TOTAL_PROFIT"]
        .cumsum()
    )

    historico["CUM_ROI"] = (
        historico["CUM_PROFIT"]
        /
        historico["CUM_STAKE"]
    )

    # ======================================================
    # VALIDACIÓN MULTILIGA
    # ======================================================

    if VALIDATION_FILE.exists():

        validation = pd.read_csv(
            VALIDATION_FILE
        )

    else:

        validation = pd.DataFrame(
            columns=[
                "SEASON",
                "SAMPLE_TYPE",
                "CORE_ROI",
                "RARE_HOME_ROI",
                "RARE_AWAY_ROI",
                "PORTFOLIO_ROI",
                "PORTFOLIO_PROFIT",
                "MAX_DRAWDOWN",
            ]
        )

    # ======================================================
    # CONFIG
    # ======================================================

    config = pd.DataFrame(
        [
            {
                "PARAMETRO": "VERSION",
                "VALOR": "V1.0 DEVELOPMENT",
            },
            {
                "PARAMETRO": "MODE",
                "VALOR": "BACKTEST",
            },
            {
                "PARAMETRO": "ACTIVE_SEASON",
                "VALOR": season_name,
            },
            {
                "PARAMETRO": "CORE_MIN_P",
                "VALOR": 0.16,
            },
            {
                "PARAMETRO": "CORE_STAKE",
                "VALOR": 1.0,
            },
            {
                "PARAMETRO": "RARE_STAKE",
                "VALOR": 0.5,
            },
            {
                "PARAMETRO": "RARE_HOME_SCORES",
                "VALOR": "4-0 | 4-1",
            },
            {
                "PARAMETRO": "RARE_AWAY_SCORES",
                "VALOR": "0-3 | 1-4",
            },
        ]
    )

    # ======================================================
    # RESUMEN MOTORES
    # ======================================================

    engine_summary = pd.DataFrame(
        [
            {
                "ENGINE": "CORE",
                "SIGNALS": core_summary["signals"],
                "STAKE": core_summary["stake"],
                "RETURN": core_summary["return"],
                "PROFIT": core_summary["profit"],
                "ROI": core_summary["roi"],
            },
            {
                "ENGINE": "RARE HOME",
                "SIGNALS": rare_home_summary["signals"],
                "STAKE": rare_home_summary["stake"],
                "RETURN": rare_home_summary["return"],
                "PROFIT": rare_home_summary["profit"],
                "ROI": rare_home_summary["roi"],
            },
            {
                "ENGINE": "RARE AWAY",
                "SIGNALS": rare_away_summary["signals"],
                "STAKE": rare_away_summary["stake"],
                "RETURN": rare_away_summary["return"],
                "PROFIT": rare_away_summary["profit"],
                "ROI": rare_away_summary["roi"],
            },
        ]
    )

    # ======================================================
    # EXPORTAR EXCEL
    # ======================================================

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl"
    ) as writer:

        dashboard.to_excel(
            writer,
            sheet_name="DASHBOARD",
            index=False
        )

        engine_summary.to_excel(
            writer,
            sheet_name="DASHBOARD",
            index=False,
            startrow=len(dashboard) + 3
        )

        jornada.to_excel(
            writer,
            sheet_name="JORNADA",
            index=False
        )

        selections.to_excel(
            writer,
            sheet_name="SELECCIONES",
            index=False
        )

        core.to_excel(
            writer,
            sheet_name="CORE",
            index=False
        )

        rare.to_excel(
            writer,
            sheet_name="RARE",
            index=False
        )

        historico.to_excel(
            writer,
            sheet_name="HISTORICO",
            index=False
        )

        validation.to_excel(
            writer,
            sheet_name="VALIDACION",
            index=False
        )

        config.to_excel(
            writer,
            sheet_name="CONFIG",
            index=False
        )

    print()
    print("Excel CorrectScoreLab V1 creado correctamente.")
    print()
    print(f"Archivo:")
    print(OUTPUT_FILE)

    print()
    print(f"Temporada          : {season_name}")
    print(f"Partidos analizados: {len(portfolio)}")
    print(f"Selecciones        : {len(active)}")
    print(f"CORE               : {core_summary['signals']}")
    print(f"RARE HOME          : {rare_home_summary['signals']}")
    print(f"RARE AWAY          : {rare_away_summary['signals']}")

    return OUTPUT_FILE