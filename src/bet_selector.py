"""
Bet Selector V1.1
Selecciones Operativas V0.2

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

Añade:
- ID_PARTIDO
- ID_APUESTA
- LIGA

La estructura está preparada para BACKTEST
y para el futuro modo LIVE.
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
# FUNCIONES AUXILIARES
# ==========================================================

def get_league_from_season(season_name):

    if not season_name:

        return ""

    return str(season_name).split("_")[0]


def clean_id_text(value):

    return (
        str(value)
        .strip()
        .upper()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )


def build_match_id(
    season_name,
    fecha,
    local,
    visitante
):

    if pd.isna(fecha):

        fecha_text = "NO_DATE"

    else:

        fecha_text = pd.to_datetime(
            fecha
        ).strftime("%Y%m%d")

    local_text = clean_id_text(
        local
    )

    visitante_text = clean_id_text(
        visitante
    )

    return (
        f"{season_name}_"
        f"{fecha_text}_"
        f"{local_text}_"
        f"{visitante_text}"
    )


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
    print("BET SELECTOR V1.1 - SELECCIONES V0.2")
    print("=" * 100)

    portfolio = (
        portfolio_result["portfolio"]
        .copy()
    )

   

    league = get_league_from_season(
        season_name
    )

    selections = []

    bet_counter = 1

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

        match_id = build_match_id(
            season_name=season_name,
            fecha=fecha,
            local=local,
            visitante=visitante
        )

        # ==================================================
        # CORE
        # ==================================================

        if row.get(
            "CORE_ACTIVE",
            False
        ):

            bet_id = (
                f"{match_id}_"
                f"CORE_"
                f"{bet_counter:04d}"
            )

            selections.append(
                {
                    "ID_PARTIDO":
                        match_id,

                    "ID_APUESTA":
                        bet_id,

                    "TEMPORADA":
                        season_name,

                    "LIGA":
                        league,

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

                    "ESTADO":
                        "PENDIENTE",

                    "RESULTADO_REAL":
                        real_score,

                    "RETORNO":
                        None,

                    "PROFIT":
                        None,
                }
            )

            bet_counter += 1

        # ==================================================
        # RARE HOME
        # ==================================================

        if row.get(
            "RARE_HOME_ACTIVE",
            False
        ):

            for score in RARE_HOME_SCORES:

                bet_id = (
                    f"{match_id}_"
                    f"RARE_HOME_"
                    f"{score.replace('-', '')}_"
                    f"{bet_counter:04d}"
                )

                selections.append(
                    {
                        "ID_PARTIDO":
                            match_id,

                        "ID_APUESTA":
                            bet_id,

                        "TEMPORADA":
                            season_name,

                        "LIGA":
                            league,

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

                        "ESTADO":
                            "PENDIENTE",

                        "RESULTADO_REAL":
                            real_score,

                        "RETORNO":
                            None,

                        "PROFIT":
                            None,
                    }
                )

                bet_counter += 1

        # ==================================================
        # RARE AWAY
        # ==================================================

        if row.get(
            "RARE_AWAY_ACTIVE",
            False
        ):

            for score in RARE_AWAY_SCORES:

                bet_id = (
                    f"{match_id}_"
                    f"RARE_AWAY_"
                    f"{score.replace('-', '')}_"
                    f"{bet_counter:04d}"
                )

                selections.append(
                    {
                        "ID_PARTIDO":
                            match_id,

                        "ID_APUESTA":
                            bet_id,

                        "TEMPORADA":
                            season_name,

                        "LIGA":
                            league,

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

                        "ESTADO":
                            "PENDIENTE",

                        "RESULTADO_REAL":
                            real_score,

                        "RETORNO":
                            None,

                        "PROFIT":
                            None,
                    }
                )

                bet_counter += 1

    # ======================================================
    # DATAFRAME
    # ======================================================

    columns = [

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
        "P_MODELO",
        "STAKE",
        "CUOTA",
        "ESTADO",
        "RESULTADO_REAL",
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

    if len(bets) > 0:

        core_bets = (
            bets["MOTOR"]
            .eq("CORE")
            .sum()
        )

        rare_home_bets = (
            bets["MOTOR"]
            .eq("RARE HOME")
            .sum()
        )

        rare_away_bets = (
            bets["MOTOR"]
            .eq("RARE AWAY")
            .sum()
        )

        total_stake = (
            bets["STAKE"]
            .sum()
        )

        unique_matches = (
            bets["ID_PARTIDO"]
            .nunique()
        )

        unique_bets = (
            bets["ID_APUESTA"]
            .nunique()
        )

    else:

        core_bets = 0
        rare_home_bets = 0
        rare_away_bets = 0
        total_stake = 0
        unique_matches = 0
        unique_bets = 0

    print()
    print(f"Temporada          : {season_name}")
    print(f"Liga               : {league}")
    print(f"Modo               : {mode}")

    print()
    print(f"Partidos apostados : {unique_matches}")
    print(f"Apuestas CORE      : {core_bets}")
    print(f"Apuestas RARE HOME : {rare_home_bets}")
    print(f"Apuestas RARE AWAY : {rare_away_bets}")

    print("-" * 40)

    print(f"Apuestas totales   : {len(bets)}")
    print(f"IDs únicos apuesta : {unique_bets}")
    print(f"Stake total        : {total_stake:.2f}")

    # ======================================================
    # CONTROL DE INTEGRIDAD
    # ======================================================

    if unique_bets != len(bets):

        raise ValueError(
            "Existen ID_APUESTA duplicados "
            "en Bet Selector."
        )

    return bets