"""
Bet Settlement Engine V0.1

Liquida las apuestas individuales generadas
por Bet Selector.

BACKTEST:
- Si MARCADOR_APUESTA == RESULTADO_REAL:
    GANADA
    CUOTA = cuota disponible del marcador real
    RETORNO = STAKE * CUOTA
    PROFIT = RETORNO - STAKE

- Si MARCADOR_APUESTA != RESULTADO_REAL:
    PERDIDA
    CUOTA = desconocida
    RETORNO = 0
    PROFIT = -STAKE

LIVE:
- Preparado para mantener apuestas PENDIENTES.
"""


import pandas as pd


def settle_bets(
    bet_selections,
    odds_result,
    mode="BACKTEST"
):

    print()
    print("=" * 100)
    print("BET SETTLEMENT ENGINE V0.1")
    print("=" * 100)

    bets = bet_selections.copy()

    odds = odds_result.copy()

    # ==========================================================
    # VALIDACIÓN
    # ==========================================================

    required_bet_columns = [

        "ID_PARTIDO",
        "ID_APUESTA",
        "FECHA",
        "LOCAL",
        "VISITANTE",
        "MARCADOR_APUESTA",
        "STAKE",
        "RESULTADO_REAL",

    ]

    missing = [

        column

        for column in required_bet_columns

        if column not in bets.columns

    ]

    if missing:

        raise ValueError(
            f"Faltan columnas en Bet Selector: {missing}"
        )

    required_odds_columns = [

        "FECHA",
        "LOCAL",
        "VISITANTE",
        "ODDS_REAL_SCORE",
        "CUOTA",

    ]

    missing = [

        column

        for column in required_odds_columns

        if column not in odds.columns

    ]

    if missing:

        raise ValueError(
            f"Faltan columnas en Odds Result: {missing}"
        )

    # ==========================================================
    # NORMALIZACIÓN
    # ==========================================================

    bets["FECHA"] = pd.to_datetime(
        bets["FECHA"],
        errors="coerce"
    )

    odds["FECHA"] = pd.to_datetime(
        odds["FECHA"],
        errors="coerce"
    )

    for column in [
        "LOCAL",
        "VISITANTE",
    ]:

        bets[column] = (
            bets[column]
            .astype(str)
            .str.strip()
        )

        odds[column] = (
            odds[column]
            .astype(str)
            .str.strip()
        )

    bets["MARCADOR_APUESTA"] = (
        bets["MARCADOR_APUESTA"]
        .astype(str)
        .str.strip()
    )

    bets["RESULTADO_REAL"] = (
        bets["RESULTADO_REAL"]
        .astype(str)
        .str.strip()
    )

    odds["ODDS_REAL_SCORE"] = (
        odds["ODDS_REAL_SCORE"]
        .astype(str)
        .str.strip()
    )

    # ==========================================================
    # PREPARAR CUOTA DEL RESULTADO REAL
    # ==========================================================

    odds_lookup = (

        odds[[
            "FECHA",
            "LOCAL",
            "VISITANTE",
            "ODDS_REAL_SCORE",
            "CUOTA",
        ]]

        .drop_duplicates(
            subset=[
                "FECHA",
                "LOCAL",
                "VISITANTE",
            ]
        )

        .rename(
            columns={
                "ODDS_REAL_SCORE":
                    "_ODDS_REAL_SCORE",

                "CUOTA":
                    "_WINNING_ODDS",
            }
        )

    )

    # ==========================================================
    # CRUZAR APUESTAS CON CUOTAS
    # ==========================================================

    bets = bets.merge(

        odds_lookup,

        on=[
            "FECHA",
            "LOCAL",
            "VISITANTE",
        ],

        how="left",

        validate="many_to_one"

    )

    # ==========================================================
    # BACKTEST
    # ==========================================================

    if mode.upper() == "BACKTEST":

        bets["_HIT"] = (

            bets["MARCADOR_APUESTA"]

            ==

            bets["RESULTADO_REAL"]

        )

        bets["ESTADO"] = "PERDIDA"

        bets.loc[

            bets["_HIT"],

            "ESTADO"

        ] = "GANADA"

        # ------------------------------------------
        # CUOTA
        # Solo conocemos la cuota cuando la apuesta
        # coincide con el resultado real.
        # ------------------------------------------

        bets["CUOTA"] = pd.NA

        bets.loc[

            bets["_HIT"],

            "CUOTA"

        ] = bets.loc[

            bets["_HIT"],

            "_WINNING_ODDS"

        ]

        # ------------------------------------------
        # RETORNO
        # ------------------------------------------

        bets["RETORNO"] = 0.0

        bets.loc[

            bets["_HIT"],

            "RETORNO"

        ] = (

            bets.loc[
                bets["_HIT"],
                "STAKE"
            ]

            *

            bets.loc[
                bets["_HIT"],
                "_WINNING_ODDS"
            ]

        )

        # ------------------------------------------
        # PROFIT
        # ------------------------------------------

        bets["PROFIT"] = (

            bets["RETORNO"]

            -

            bets["STAKE"]

        )

    # ==========================================================
    # LIVE
    # ==========================================================

    else:

        bets["ESTADO"] = "PENDIENTE"

        bets["RETORNO"] = pd.NA

        bets["PROFIT"] = pd.NA

    # ==========================================================
    # LIMPIEZA
    # ==========================================================

    internal_columns = [

        "_ODDS_REAL_SCORE",
        "_WINNING_ODDS",
        "_HIT",

    ]

    bets = bets.drop(

        columns=[

            column

            for column in internal_columns

            if column in bets.columns

        ]

    )

    # ==========================================================
    # RESUMEN
    # ==========================================================

    total_bets = len(bets)

    won = (

        bets["ESTADO"]
        .eq("GANADA")
        .sum()

    )

    lost = (

        bets["ESTADO"]
        .eq("PERDIDA")
        .sum()

    )

    pending = (

        bets["ESTADO"]
        .eq("PENDIENTE")
        .sum()

    )

    total_stake = (

        pd.to_numeric(
            bets["STAKE"],
            errors="coerce"
        )
        .fillna(0)
        .sum()

    )

    total_return = (

        pd.to_numeric(
            bets["RETORNO"],
            errors="coerce"
        )
        .fillna(0)
        .sum()

    )

    total_profit = (

        pd.to_numeric(
            bets["PROFIT"],
            errors="coerce"
        )
        .fillna(0)
        .sum()

    )

    roi = (

        total_profit
        /
        total_stake
        *
        100

        if total_stake > 0

        else 0

    )

    print()
    print(f"Modo               : {mode}")
    print(f"Apuestas totales   : {total_bets}")
    print(f"Ganadas            : {won}")
    print(f"Perdidas           : {lost}")
    print(f"Pendientes         : {pending}")

    print()
    print(f"Stake total        : {total_stake:.2f}")
    print(f"Retorno conocido   : {total_return:.2f}")
    print(f"Profit             : {total_profit:+.2f}")
    print(f"ROI                : {roi:+.2f}%")

    return bets