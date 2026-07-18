"""
Excel Output Engine V0.2

Genera el Excel operativo base de CorrectScoreLab V1.

Utiliza datos de BACKTEST para construir y validar
la estructura que posteriormente utilizará el modo LIVE.

Incluye:
- Dashboard operativo
- Jornada
- Selecciones
- CORE
- RARE
- Histórico
- Validación multiliga
- CORE Coverage histórico
- Configuración

Archivo generado:
data/results/CorrectScoreLab_V1.xlsx
"""

from excel_formatter import format_excel

from pathlib import Path

import pandas as pd


# ==========================================================
# ARCHIVOS
# ==========================================================

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

CORE_COVERAGE_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "results"
    / "core_coverage_history.csv"
)


def export_excel_v1(
    odds_result,
    portfolio_result,
    bet_selections,
    historical,
    performance,
    season_name
):

    print()
    print("=" * 100)
    print("EXCEL OUTPUT ENGINE V0.2")
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
    # DASHBOARD V0.2
    #
    # Fuente operativa:
    # Historical Engine -> Performance Engine
    #
    # Riesgo principal:
    # Portfolio por partido
    # ======================================================

    global_perf = performance["global"]
    risk_perf = performance["risk"]

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
                "METRICA": "APUESTAS INDIVIDUALES",
                "VALOR": global_perf["BETS"],
            },
            {
                "METRICA": "APUESTAS GANADAS",
                "VALOR": global_perf["WINS"],
            },
            {
                "METRICA": "APUESTAS PERDIDAS",
                "VALOR": global_perf["LOSSES"],
            },
            {
                "METRICA": "APUESTAS PENDIENTES",
                "VALOR": global_perf["PENDING"],
            },
            {
                "METRICA": "HIT RATE APUESTAS",
                "VALOR": global_perf["HIT_RATE"] / 100,
            },
            {
                "METRICA": "STAKE TOTAL",
                "VALOR": global_perf["STAKE"],
            },
            {
                "METRICA": "RETORNO",
                "VALOR": global_perf["RETURN"],
            },
            {
                "METRICA": "BENEFICIO",
                "VALOR": global_perf["PROFIT"],
            },
            {
                "METRICA": "ROI",
                "VALOR": global_perf["ROI"] / 100,
            },
            {
                "METRICA": "BANK INICIAL",
                "VALOR": risk_perf["INITIAL_BANK"],
            },
            {
                "METRICA": "BANK FINAL",
                "VALOR": risk_perf["FINAL_BANK"],
            },
            {
                "METRICA": "BANK PEAK",
                "VALOR": risk_perf["BANK_PEAK"],
            },
            {
                "METRICA": "MAX DD PORTFOLIO",
                "VALOR": total_summary["max_drawdown"],
            },
            {
                "METRICA": "MAX DD APUESTAS",
                "VALOR": risk_perf["MAX_DRAWDOWN"],
            },
            {
                "METRICA": "MAX RACHA NEGATIVA PORTFOLIO",
                "VALOR": total_summary["max_losing_streak"],
            },
            {
                "METRICA": "MAX RACHA APUESTAS PERDIDAS",
                "VALOR": risk_perf["MAX_LOSING_STREAK"],
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
    # Una fila = una apuesta liquidada
    # Fuente: Historical Engine V0.1
    # ======================================================

    historico = historical.copy()

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
    # CORE COVERAGE HISTÓRICO
    # ======================================================

    if CORE_COVERAGE_FILE.exists():

        core_coverage = pd.read_csv(
            CORE_COVERAGE_FILE
        )

    else:

        core_coverage = pd.DataFrame(
            columns=[
                "TEMPORADA",
                "LIGA",
                "PARTIDOS",
                "CORE_SEÑALES",
                "CORE_COBERTURA",
                "CORE_P_MEDIA",
                "CORE_P_MIN",
                "CORE_P_MAX",
                "CORE_STAKE",
                "CORE_RETURN",
                "CORE_PROFIT",
                "CORE_ROI",
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
    # RESUMEN MOTORES - PERFORMANCE ENGINE
    # Una fila = rendimiento económico por motor
    # ======================================================

    engine_summary = (
        performance["by_engine"]
        .copy()
    )

    engine_summary = engine_summary.rename(
        columns={
            "MOTOR": "ENGINE",
        }
    )

    engine_order = [
        "CORE",
        "RARE HOME",
        "RARE AWAY",
    ]

    engine_summary["ENGINE"] = pd.Categorical(
        engine_summary["ENGINE"],
        categories=engine_order,
        ordered=True
    )

    engine_summary = (
        engine_summary
        .sort_values("ENGINE")
        .reset_index(drop=True)
    )

    engine_summary["ENGINE"] = (
        engine_summary["ENGINE"]
        .astype(str)
    )

    # ======================================================
    # RENDIMIENTO MENSUAL
    # ======================================================

    monthly_summary = (
        performance["by_month"]
        .copy()
    )

    # ======================================================
    # EXPORTAR EXCEL
    # ======================================================

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl"
    ) as writer:

        # ==================================================
        # DASHBOARD
        # ==================================================

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

        monthly_summary.to_excel(
            writer,
            sheet_name="DASHBOARD",
            index=False,
            startrow=(
                len(dashboard)
                +
                len(engine_summary)
                +
                7
            )
        )

        # ==================================================
        # JORNADA
        # ==================================================

        jornada.to_excel(
            writer,
            sheet_name="JORNADA",
            index=False
        )

        # ==================================================
        # SELECCIONES
        # ==================================================

        selections.to_excel(
            writer,
            sheet_name="SELECCIONES",
            index=False
        )

        # ==================================================
        # CORE
        # ==================================================

        core.to_excel(
            writer,
            sheet_name="CORE",
            index=False
        )

        # ==================================================
        # RARE
        # ==================================================

        rare.to_excel(
            writer,
            sheet_name="RARE",
            index=False
        )

        # ==================================================
        # HISTORICO
        # ==================================================

        historico.to_excel(
            writer,
            sheet_name="HISTORICO",
            index=False
        )

        # ==================================================
        # VALIDACION MULTILIGA
        # ==================================================

        validation.to_excel(
            writer,
            sheet_name="VALIDACION",
            index=False
        )

        # ==================================================
        # CORE COVERAGE
        #
        # Se coloca debajo de la tabla de validación
        # dejando tres filas de separación.
        # ==================================================

        core_coverage_startrow = (
            len(validation)
            + 4
        )

        core_coverage.to_excel(
            writer,
            sheet_name="VALIDACION",
            index=False,
            startrow=core_coverage_startrow
        )

        # ==================================================
        # CONFIG
        # ==================================================

        config.to_excel(
            writer,
            sheet_name="CONFIG",
            index=False
        )

    # ======================================================
    # FORMATO VISUAL AUTOMÁTICO
    # ======================================================

    format_excel(
        OUTPUT_FILE
    )

    # ======================================================
    # SALIDA CONSOLA
    # ======================================================

    print()
    print("Excel CorrectScoreLab V1 creado correctamente.")

    print()
    print("Archivo:")
    print(OUTPUT_FILE)

    print()
    print(f"Temporada          : {season_name}")
    print(f"Partidos analizados: {len(portfolio)}")
    print(f"Selecciones        : {len(active)}")
    print(f"CORE               : {core_summary['signals']}")
    print(f"RARE HOME          : {rare_home_summary['signals']}")
    print(f"RARE AWAY          : {rare_away_summary['signals']}")

    print()

    print(
        f"Temporadas CORE Coverage: "
        f"{len(core_coverage)}"
    )

    # ======================================================
    # RETURN
    # ======================================================

    return OUTPUT_FILE