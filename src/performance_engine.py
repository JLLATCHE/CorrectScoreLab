"""
Performance Engine V0.1

Analiza el histórico operativo de apuestas
de CorrectScoreLab.

Fuente:
Historical Engine V0.1

Genera:
- Rendimiento global
- Rendimiento por motor
- Rendimiento por mes
- Rendimiento por liga
- Métricas de riesgo

Esta capa será la fuente de datos
del Dashboard operativo.
"""

import pandas as pd


def _calculate_summary(df):

    bets = len(df)

    stake = (
        pd.to_numeric(
            df["STAKE"],
            errors="coerce"
        )
        .fillna(0.0)
        .sum()
    )

    returns = (
        pd.to_numeric(
            df["RETORNO"],
            errors="coerce"
        )
        .fillna(0.0)
        .sum()
    )

    profit = (
        pd.to_numeric(
            df["PROFIT"],
            errors="coerce"
        )
        .fillna(0.0)
        .sum()
    )

    wins = (
        df["ESTADO"]
        .eq("GANADA")
        .sum()
    )

    losses = (
        df["ESTADO"]
        .eq("PERDIDA")
        .sum()
    )

    pending = (
        df["ESTADO"]
        .eq("PENDIENTE")
        .sum()
    )

    roi = (
        profit
        /
        stake
        *
        100

        if stake > 0

        else 0.0
    )

    hit_rate = (
        wins
        /
        (wins + losses)
        *
        100

        if (wins + losses) > 0

        else 0.0
    )

    return {

        "BETS": bets,
        "WINS": wins,
        "LOSSES": losses,
        "PENDING": pending,
        "HIT_RATE": hit_rate,
        "STAKE": stake,
        "RETURN": returns,
        "PROFIT": profit,
        "ROI": roi,

    }


def _build_group_summary(
    history,
    group_column
):

    rows = []

    grouped = history.groupby(
        group_column,
        dropna=False
    )

    for group_value, group_df in grouped:

        summary = _calculate_summary(
            group_df
        )

        row = {
            group_column: group_value,
            **summary,
        }

        rows.append(row)

    result = pd.DataFrame(
        rows
    )

    return result


def _calculate_max_losing_streak(history):

    max_streak = 0
    current_streak = 0

    for state in history["ESTADO"]:

        if state == "PERDIDA":

            current_streak += 1

            max_streak = max(
                max_streak,
                current_streak
            )

        elif state == "GANADA":

            current_streak = 0

    return max_streak


def analyze_performance(
    historical
):

    print()
    print("=" * 100)
    print("PERFORMANCE ENGINE V0.1")
    print("=" * 100)

    history = historical.copy()

    # ==========================================================
    # VALIDACIÓN
    # ==========================================================

    required_columns = [

        "ID_APUESTA",
        "TEMPORADA",
        "LIGA",
        "FECHA",
        "MOTOR",
        "STAKE",
        "ESTADO",
        "RETORNO",
        "PROFIT",
        "BANK",
        "BANK_PEAK",
        "DRAWDOWN",

    ]

    missing = [

        column

        for column in required_columns

        if column not in history.columns

    ]

    if missing:

        raise ValueError(
            f"Faltan columnas para Performance Engine: {missing}"
        )

    # ==========================================================
    # NORMALIZACIÓN
    # ==========================================================

    history["FECHA"] = pd.to_datetime(
        history["FECHA"],
        errors="coerce"
    )

    history["MES"] = (
        history["FECHA"]
        .dt.to_period("M")
        .astype(str)
    )

    # ==========================================================
    # GLOBAL
    # ==========================================================

    global_summary = _calculate_summary(
        history
    )

    # ==========================================================
    # POR MOTOR
    # ==========================================================

    by_engine = _build_group_summary(
        history,
        "MOTOR"
    )

    # ==========================================================
    # POR MES
    # ==========================================================

    by_month = _build_group_summary(
        history,
        "MES"
    )

    if not by_month.empty:

        by_month = (
            by_month
            .sort_values("MES")
            .reset_index(drop=True)
        )

    # ==========================================================
    # POR LIGA
    # ==========================================================

    by_league = _build_group_summary(
        history,
        "LIGA"
    )

    # ==========================================================
    # POR TEMPORADA
    # ==========================================================

    by_season = _build_group_summary(
        history,
        "TEMPORADA"
    )

    # ==========================================================
    # RIESGO
    # ==========================================================

    initial_bank = (

        history["BANK"].iloc[0]
        -
        history["PROFIT"].iloc[0]

        if len(history) > 0

        else 0.0
    )

    final_bank = (

        history["BANK"].iloc[-1]

        if len(history) > 0

        else initial_bank
    )

    bank_peak = (

        history["BANK_PEAK"].max()

        if len(history) > 0

        else initial_bank
    )

    max_drawdown = (

        history["DRAWDOWN"].max()

        if len(history) > 0

        else 0.0
    )

    max_losing_streak = (
        _calculate_max_losing_streak(
            history
        )
    )

    risk_summary = {

        "INITIAL_BANK":
            initial_bank,

        "FINAL_BANK":
            final_bank,

        "BANK_PEAK":
            bank_peak,

        "MAX_DRAWDOWN":
            max_drawdown,

        "MAX_LOSING_STREAK":
            max_losing_streak,

    }

    # ==========================================================
    # PRINT GLOBAL
    # ==========================================================

    print()
    print("GLOBAL")
    print("-" * 100)

    print(
        f"Apuestas           : "
        f"{global_summary['BETS']}"
    )

    print(
        f"Ganadas            : "
        f"{global_summary['WINS']}"
    )

    print(
        f"Perdidas           : "
        f"{global_summary['LOSSES']}"
    )

    print(
        f"Pendientes         : "
        f"{global_summary['PENDING']}"
    )

    print(
        f"Hit Rate           : "
        f"{global_summary['HIT_RATE']:.2f}%"
    )

    print(
        f"Stake              : "
        f"{global_summary['STAKE']:.2f}"
    )

    print(
        f"Retorno            : "
        f"{global_summary['RETURN']:.2f}"
    )

    print(
        f"Profit             : "
        f"{global_summary['PROFIT']:+.2f}"
    )

    print(
        f"ROI                : "
        f"{global_summary['ROI']:+.2f}%"
    )

    # ==========================================================
    # PRINT MOTORES
    # ==========================================================

    print()
    print("POR MOTOR")
    print("-" * 100)

    if not by_engine.empty:

        print(
            by_engine.to_string(
                index=False
            )
        )

    # ==========================================================
    # PRINT RIESGO
    # ==========================================================

    print()
    print("RIESGO")
    print("-" * 100)

    print(
        f"Bank inicial       : "
        f"{risk_summary['INITIAL_BANK']:.2f}"
    )

    print(
        f"Bank final         : "
        f"{risk_summary['FINAL_BANK']:.2f}"
    )

    print(
        f"Bank peak          : "
        f"{risk_summary['BANK_PEAK']:.2f}"
    )

    print(
        f"Max Drawdown       : "
        f"{risk_summary['MAX_DRAWDOWN']:.2f}"
    )

    print(
        f"Máx. racha pérdidas: "
        f"{risk_summary['MAX_LOSING_STREAK']}"
    )

    # ==========================================================
    # RETURN
    # ==========================================================

    return {

        "global":
            global_summary,

        "by_engine":
            by_engine,

        "by_month":
            by_month,

        "by_league":
            by_league,

        "by_season":
            by_season,

        "risk":
            risk_summary,

    }