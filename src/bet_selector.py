"""
Bet Selector V1

Convierte las señales generadas por CorrectScoreLab
en apuestas individuales.

Cada fila representa UNA apuesta real.

CORE:
    TOP1 -> Stake 1.0

RARE HOME:
    4-0 -> Stake 0.5
    4-1 -> Stake 0.5

RARE AWAY:
    0-3 -> Stake 0.5
    1-4 -> Stake 0.5

Esta estructura será utilizada tanto por BACKTEST
como por el futuro modo LIVE.
"""

import pandas as pd


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

CORE_STAKE = 1.0

RARE_STAKE = 0.5


RARE_HOME_SCORES = [
    "4-0",
    "4-1",
]


RARE_AWAY_SCORES = [
    "0-3",
    "1-4",
]


# ==========================================================
# BET SELECTOR
# ==========================================================

def build_bet_selections(
    portfolio_result,
    season_name,
    mode="BACKTEST"
):

    print()
    print("=" * 100)
    print("BET SELECTOR V1")
    print("=" * 100)

    portfolio = (
        portfolio_result["portfolio"]
        .copy()
    )

    selections = []

    # ======================================================
    # RECORRER PARTIDOS
    # ======================================================

    for _, row in portfolio.iterrows():

        fecha = row.get(
            "FECHA",
            pd.NaT
        )

        local = row.get(
            "LOCAL",
            ""
        )

        visitante = row.get(
            "VISITANTE",
            ""
        )

        real_score = row.get(
            "REAL_SCORE",
            ""
        )

        top1 = str(
            row.get(
                "TOP1",
                ""
            )
        )

        p_top1 = row.get(
            "P_TOP1",
            None
        )

        # ==================================================
        # CORE
        # ==================================================

        if row.get(
            "CORE_ACTIVE",
            False
        ):

            selections.append(
                {
                    "TEMPORADA":
                        season_name,

                    "MODO":
                        mode,

                    "FECHA":
                        fecha,

                    "LOCAL":
                        local,

                    "VISITANTE":
                        visitante,

                    "MOTOR":
                        "CORE",

                    "MARCADOR_APUESTA":
                        top1,

                    "P_MODELO":
                        p_top1,

                    "STAKE":
                        CORE_STAKE,

                    "CUOTA":
                        None,

                    "RESULTADO_REAL":
                        real_score,

                    "ESTADO":
                        "PENDIENTE",

                    "RETORNO":
                        None,

                    "PROFIT":
                        None,
                }
            )

        # ==================================================
        # RARE HOME
        # ==================================================

        if row.get(
            "RARE_HOME_ACTIVE",
            False
        ):

            for score in RARE_HOME_SCORES:

                selections.append(
                    {
                        "TEMPORADA":
                            season_name,

                        "MODO":
                            mode,

                        "FECHA":
                            fecha,

                        "LOCAL":
                            local,

                        "VISITANTE":
                            visitante,

                        "MOTOR":
                            "RARE HOME",

                        "MARCADOR_APUESTA":
                            score,

                        "P_MODELO":
                            None,

                        "STAKE":
                            RARE_STAKE,

                        "CUOTA":
                            None,

                        "RESULTADO_REAL":
                            real_score,

                        "ESTADO":
                            "PENDIENTE",

                        "RETORNO":
                            None,

                        "PROFIT":
                            None,
                    }
                )

        # ==================================================
        # RARE AWAY
        # ==================================================

        if row.get(
            "RARE_AWAY_ACTIVE",
            False
        ):

            for score in RARE_AWAY_SCORES:

                selections.append(
                    {
                        "TEMPORADA":
                            season_name,

                        "MODO":
                            mode,

                        "FECHA":
                            fecha,

                        "LOCAL":
                            local,

                        "VISITANTE":
                            visitante,

                        "MOTOR":
                            "RARE AWAY",

                        "MARCADOR_APUESTA":
                            score,

                        "P_MODELO":
                            None,

                        "STAKE":
                            RARE_STAKE,

                        "CUOTA":
                            None,

                        "RESULTADO_REAL":
                            real_score,

                        "ESTADO":
                            "PENDIENTE",

                        "RETORNO":
                            None,

                        "PROFIT":
                            None,
                    }
                )

    # ======================================================
    # DATAFRAME
    # ======================================================

    columns = [

        "TEMPORADA",
        "MODO",
        "FECHA",
        "LOCAL",
        "VISITANTE",
        "MOTOR",
        "MARCADOR_APUESTA",
        "P_MODELO",
        "STAKE",
        "CUOTA",
        "RESULTADO_REAL",
        "ESTADO",
        "RETORNO",
        "PROFIT",

    ]

    bets = pd.DataFrame(
        selections,
        columns=columns
    )

    # ======================================================
    # RESUMEN
    # ======================================================

    core_bets = (

        bets["MOTOR"]
        .eq("CORE")
        .sum()

        if len(bets) > 0

        else 0

    )

    rare_home_bets = (

        bets["MOTOR"]
        .eq("RARE HOME")
        .sum()

        if len(bets) > 0

        else 0

    )

    rare_away_bets = (

        bets["MOTOR"]
        .eq("RARE AWAY")
        .sum()

        if len(bets) > 0

        else 0

    )

    total_stake = (

        bets["STAKE"].sum()

        if len(bets) > 0

        else 0
    )

    print()
    print(f"Temporada          : {season_name}")
    print(f"Modo               : {mode}")
    print()
    print(f"Apuestas CORE      : {core_bets}")
    print(f"Apuestas RARE HOME : {rare_home_bets}")
    print(f"Apuestas RARE AWAY : {rare_away_bets}")
    print("-" * 40)
    print(f"Apuestas totales   : {len(bets)}")
    print(f"Stake total        : {total_stake:.2f}")

    return bets