"""
Historical Engine V0.1

Construye el histórico operativo de apuestas
de CorrectScoreLab.

BACKTEST:
- Recibe las apuestas liquidadas por Settlement Engine.
- Conserva una fila por ID_APUESTA.
- Ordena cronológicamente.
- Calcula BANK acumulado.
- Calcula PROFIT acumulado.

LIVE:
- La persistencia definitiva se implementará
  sobre esta misma estructura.
"""

import pandas as pd


def build_historical(
    settled_bets,
    initial_bank=0.0,
    mode="BACKTEST"
):

    print()
    print("=" * 100)
    print("HISTORICAL ENGINE V0.1")
    print("=" * 100)

    history = settled_bets.copy()

    # ==========================================================
    # VALIDACIÓN
    # ==========================================================

    required_columns = [

        "ID_PARTIDO",
        "ID_APUESTA",
        "TEMPORADA",
        "LIGA",
        "MODO",
        "FECHA",
        "LOCAL",
        "VISITANTE",
        "MOTOR",
        "MARCADOR_APUESTA",
        "STAKE",
        "CUOTA",
        "ESTADO",
        "RESULTADO_REAL",
        "RETORNO",
        "PROFIT",

    ]

    missing = [

        column

        for column in required_columns

        if column not in history.columns

    ]

    if missing:

        raise ValueError(
            f"Faltan columnas para Historical Engine: {missing}"
        )

    # ==========================================================
    # NORMALIZACIÓN
    # ==========================================================

    history["FECHA"] = pd.to_datetime(
        history["FECHA"],
        errors="coerce"
    )

    history["STAKE"] = pd.to_numeric(
        history["STAKE"],
        errors="coerce"
    ).fillna(0.0)

    history["RETORNO"] = pd.to_numeric(
        history["RETORNO"],
        errors="coerce"
    ).fillna(0.0)

    history["PROFIT"] = pd.to_numeric(
        history["PROFIT"],
        errors="coerce"
    ).fillna(0.0)

    # ==========================================================
    # CONTROL ID_APUESTA
    # ==========================================================

    duplicate_ids = history[
        "ID_APUESTA"
    ].duplicated().sum()

    if duplicate_ids > 0:

        raise ValueError(
            f"Historical Engine detectó "
            f"{duplicate_ids} ID_APUESTA duplicados."
        )

    # ==========================================================
    # ORDEN CRONOLÓGICO
    # ==========================================================

    history = (

        history

        .sort_values(
            by=[
                "FECHA",
                "ID_APUESTA",
            ]
        )

        .reset_index(
            drop=True
        )

    )

    # ==========================================================
    # ACUMULADOS
    # ==========================================================

    history["PROFIT_ACUMULADO"] = (
        history["PROFIT"]
        .cumsum()
    )

    history["BANK"] = (
        initial_bank
        +
        history["PROFIT_ACUMULADO"]
    )

    # ==========================================================
    # EQUITY PEAK
    # ==========================================================

    history["BANK_PEAK"] = (
        history["BANK"]
        .cummax()
    )

    # ==========================================================
    # DRAWDOWN
    # ==========================================================

    history["DRAWDOWN"] = (

        history["BANK_PEAK"]

        -

        history["BANK"]

    )

    # ==========================================================
    # CONTROL FINAL
    # ==========================================================

    total_bets = len(history)

    unique_bets = (
        history["ID_APUESTA"]
        .nunique()
    )

    total_stake = (
        history["STAKE"]
        .sum()
    )

    total_return = (
        history["RETORNO"]
        .sum()
    )

    total_profit = (
        history["PROFIT"]
        .sum()
    )

    final_bank = (
        history["BANK"].iloc[-1]

        if len(history) > 0

        else initial_bank
    )

    max_drawdown = (
        history["DRAWDOWN"]
        .max()

        if len(history) > 0

        else 0.0
    )

    roi = (

        total_profit
        /
        total_stake
        *
        100

        if total_stake > 0

        else 0.0
    )

    print()
    print(f"Modo               : {mode}")
    print(f"Apuestas histórico : {total_bets}")
    print(f"IDs únicos         : {unique_bets}")

    print()
    print(f"Stake total        : {total_stake:.2f}")
    print(f"Retorno total      : {total_return:.2f}")
    print(f"Profit total       : {total_profit:+.2f}")
    print(f"ROI                : {roi:+.2f}%")

    print()
    print(f"Bank inicial       : {initial_bank:.2f}")
    print(f"Bank final         : {final_bank:.2f}")
    print(f"Max Drawdown       : {max_drawdown:.2f}")

    return history