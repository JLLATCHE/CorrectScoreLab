"""
Bet Selector V1.2
Selecciones Operativas V0.3

Convierte las señales generadas por CorrectScoreLab
en apuestas individuales.

OBJETIVO V1.2
----------------------------------------------------------
Mantener intacta la operativa actual y preparar la
arquitectura para:

1. SINGLE
   - Sistema principal.
   - TOP1.
   - Stake 1.0.

2. MULTI SCORE LAB
   - Sistema experimental.
   - TOP1 + TOP2 o TOP1 + TOP2 + TOP3.
   - Stake configurable por marcador.
   - DESACTIVADO por defecto.

3. CORE PROFILE
   - Preparado para distinguir CORE_A / CORE_B / CORE_C.
   - CORE_B y CORE_C no se activan automáticamente.
   - La operativa actual sigue dependiendo de CORE_ACTIVE.

4. Excel LIVE
   - Añade información sobre sistema, nivel,
     perfil, versión de reglas y operativa.

IMPORTANTE
----------------------------------------------------------
Esta versión NO modifica las reglas actuales de apuestas.

CORE_ACTIVE:
    TOP1 -> Stake 1.0

RARE HOME:
    4-0 -> Stake 0.5
    4-1 -> Stake 0.5

RARE AWAY:
    0-3 -> Stake 0.5
    1-4 -> Stake 0.5

MULTI SCORE:
    Preparado como LAB.
    Desactivado por defecto.
"""

import pandas as pd


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================

BET_SELECTOR_VERSION = "V1.2"

RULE_VERSION = "CSP_V1_DEV"


# ==========================================================
# STAKES
# ==========================================================

CORE_STAKE = 1.0

RARE_STAKE = 0.5

MULTI_SCORE_STAKE = 0.5


# ==========================================================
# MULTI SCORE LAB
# ==========================================================
#
# IMPORTANTE:
#
# False:
#     No genera ninguna apuesta MULTI.
#
# True:
#     Permite generar apuestas experimentales MULTI.
#
# De momento debe permanecer en FALSE.
#
# ==========================================================

ENABLE_MULTI_SCORE_LAB = False


# ==========================================================
# NÚMERO DE MARCADORES MULTI
# ==========================================================
#
# Valores previstos:
#
# 2 -> TOP1 + TOP2
# 3 -> TOP1 + TOP2 + TOP3
#
# ==========================================================

MULTI_SCORE_COUNT = 2


# ==========================================================
# RARE SCORES
# ==========================================================

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

def get_league_from_season(
    season_name
):

    if not season_name:

        return ""

    return str(
        season_name
    ).split("_")[0]


def clean_id_text(
    value
):

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

    if pd.isna(
        fecha
    ):

        fecha_text = "NO_DATE"

    else:

        fecha_text = pd.to_datetime(

            fecha

        ).strftime(

            "%Y%m%d"

        )

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
# DETECTAR NIVEL CORE
# ==========================================================
#
# Esta clasificación es INFORMATIVA.
#
# NO activa apuestas.
#
# CORE_ACTIVE continúa siendo la única señal
# que activa una apuesta CORE operativa.
#
# ==========================================================

def get_core_level(
    p_top1
):

    try:

        probability = float(
            p_top1
        )

    except (

        TypeError,
        ValueError,

    ):

        return ""

    if probability >= 0.16:

        return "CORE_A"

    if probability >= 0.14:

        return "CORE_B"

    if probability >= 0.12:

        return "CORE_C"

    return ""


# ==========================================================
# DETECTAR PERFIL CORE B
# ==========================================================
#
# CANDIDATO ACTUAL:
#
# 0.14 <= P_TOP1 < 0.16
# CS002_DOMINANCE >= 0.50
# CS007_AWAY_ATTACK_EDGE <= 1.00
#
# IMPORTANTE:
#
# Solo etiqueta el perfil.
# NO activa ninguna apuesta.
#
# ==========================================================

def get_core_profile(
    row,
    core_level
):

    if core_level == "CORE_A":

        return "BASE"

    if core_level == "CORE_B":

        dominance = pd.to_numeric(

            pd.Series(
                [
                    row.get(
                        "CS002_DOMINANCE",
                        None
                    )
                ]
            ),

            errors="coerce"

        ).iloc[0]

        away_attack = pd.to_numeric(

            pd.Series(
                [
                    row.get(
                        "CS007_AWAY_ATTACK_EDGE",
                        None
                    )
                ]
            ),

            errors="coerce"

        ).iloc[0]

        if (

            pd.notna(
                dominance
            )

            and

            pd.notna(
                away_attack
            )

            and

            dominance >= 0.50

            and

            away_attack <= 1.00

        ):

            return "DOM50_AWAY100"

        return "NO_PROFILE"

    if core_level == "CORE_C":

        return "EXPERIMENTAL"

    return ""


# ==========================================================
# OPERATIVA CORE
# ==========================================================
#
# CORE_A:
#     Puede ser operativo si CORE_ACTIVE = True.
#
# CORE_B:
#     VALIDACION.
#
# CORE_C:
#     LAB.
#
# Esta función es informativa.
#
# ==========================================================

def get_core_operativa(
    core_level,
    core_active
):

    if (

        core_level == "CORE_A"

        and

        core_active

    ):

        return "SI"

    if core_level == "CORE_B":

        return "VALIDACION"

    if core_level == "CORE_C":

        return "LAB"

    return "NO"


# ==========================================================
# CREAR REGISTRO BASE DE APUESTA
# ==========================================================

def build_bet_record(
    match_id,
    bet_id,
    season_name,
    league,
    mode,
    fecha,
    local,
    visitante,
    motor,
    sistema,
    marcador_apuesta,
    p_modelo,
    stake,
    real_score,
    nivel_core="",
    perfil="",
    operativa="SI"
):

    return {

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
            motor,

        "SISTEMA":
            sistema,

        "NIVEL_CORE":
            nivel_core,

        "PERFIL":
            perfil,

        "REGLA_VERSION":
            RULE_VERSION,

        "OPERATIVA":
            operativa,

        "MARCADOR_APUESTA":
            marcador_apuesta,

        "P_MODELO":
            p_modelo,

        "STAKE":
            stake,

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

    print(
        "BET SELECTOR V1.2 - "
        "SELECCIONES V0.3"
    )

    print("=" * 100)

    portfolio = (

        portfolio_result[
            "portfolio"
        ]

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

        core_active = bool(

            row.get(
                "CORE_ACTIVE",
                False
            )

        )

        match_id = build_match_id(

            season_name=
                season_name,

            fecha=
                fecha,

            local=
                local,

            visitante=
                visitante

        )


        # ==================================================
        # CLASIFICACIÓN CORE INFORMATIVA
        # ==================================================

        core_level = get_core_level(
            p_top1
        )

        core_profile = get_core_profile(

            row=row,

            core_level=core_level

        )

        core_operativa = get_core_operativa(

            core_level=
                core_level,

            core_active=
                core_active

        )


        # ==================================================
        # CORE SINGLE
        # ==================================================
        #
        # OPERATIVA ACTUAL.
        #
        # NO SE MODIFICA.
        #
        # CORE_ACTIVE = True
        # TOP1
        # Stake 1.0
        #
        # ==================================================

        if core_active:

            bet_id = (

                f"{match_id}_"

                f"CORE_SINGLE_"

                f"{bet_counter:04d}"

            )

            selections.append(

                build_bet_record(

                    match_id=
                        match_id,

                    bet_id=
                        bet_id,

                    season_name=
                        season_name,

                    league=
                        league,

                    mode=
                        mode,

                    fecha=
                        fecha,

                    local=
                        local,

                    visitante=
                        visitante,

                    motor=
                        "CORE",

                    sistema=
                        "SINGLE",

                    marcador_apuesta=
                        top1,

                    p_modelo=
                        p_top1,

                    stake=
                        CORE_STAKE,

                    real_score=
                        real_score,

                    nivel_core=
                        core_level,

                    perfil=
                        core_profile,

                    operativa=
                        core_operativa,

                )

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

                    build_bet_record(

                        match_id=
                            match_id,

                        bet_id=
                            bet_id,

                        season_name=
                            season_name,

                        league=
                            league,

                        mode=
                            mode,

                        fecha=
                            fecha,

                        local=
                            local,

                        visitante=
                            visitante,

                        motor=
                            "RARE HOME",

                        sistema=
                            "MULTI SCORE",

                        marcador_apuesta=
                            score,

                        p_modelo=
                            None,

                        stake=
                            RARE_STAKE,

                        real_score=
                            real_score,

                        nivel_core=
                            "",

                        perfil=
                            "RARE_HOME_V1",

                        operativa=
                            "SI",

                    )

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

                    build_bet_record(

                        match_id=
                            match_id,

                        bet_id=
                            bet_id,

                        season_name=
                            season_name,

                        league=
                            league,

                        mode=
                            mode,

                        fecha=
                            fecha,

                        local=
                            local,

                        visitante=
                            visitante,

                        motor=
                            "RARE AWAY",

                        sistema=
                            "MULTI SCORE",

                        marcador_apuesta=
                            score,

                        p_modelo=
                            None,

                        stake=
                            RARE_STAKE,

                        real_score=
                            real_score,

                        nivel_core=
                            "",

                        perfil=
                            "RARE_AWAY_V1",

                        operativa=
                            "SI",

                    )

                )

                bet_counter += 1


        # ==================================================
        # MULTI SCORE LAB
        # ==================================================
        #
        # DESACTIVADO POR DEFECTO.
        #
        # Solo se genera si:
        #
        # ENABLE_MULTI_SCORE_LAB = True
        #
        # No afecta a la operativa actual.
        #
        # ==================================================

        if ENABLE_MULTI_SCORE_LAB:

            multi_candidates = []

            # ----------------------------------------------
            # TOP1
            # ----------------------------------------------

            top1_score = row.get(
                "TOP1",
                None
            )

            top1_probability = row.get(
                "P_TOP1",
                None
            )

            if top1_score:

                multi_candidates.append(

                    (

                        "TOP1",
                        str(
                            top1_score
                        ),
                        top1_probability,

                    )

                )


            # ----------------------------------------------
            # TOP2
            # ----------------------------------------------

            if MULTI_SCORE_COUNT >= 2:

                top2_score = row.get(
                    "TOP2",
                    None
                )

                top2_probability = row.get(
                    "P_TOP2",
                    None
                )

                if top2_score:

                    multi_candidates.append(

                        (

                            "TOP2",
                            str(
                                top2_score
                            ),
                            top2_probability,

                        )

                    )


            # ----------------------------------------------
            # TOP3
            # ----------------------------------------------

            if MULTI_SCORE_COUNT >= 3:

                top3_score = row.get(
                    "TOP3",
                    None
                )

                top3_probability = row.get(
                    "P_TOP3",
                    None
                )

                if top3_score:

                    multi_candidates.append(

                        (

                            "TOP3",
                            str(
                                top3_score
                            ),
                            top3_probability,

                        )

                    )


            # ----------------------------------------------
            # CREAR APUESTAS LAB
            # ----------------------------------------------

            for (

                rank,
                score,
                probability,

            ) in multi_candidates:

                bet_id = (

                    f"{match_id}_"

                    f"MULTI_LAB_"

                    f"{rank}_"

                    f"{bet_counter:04d}"

                )

                selections.append(

                    build_bet_record(

                        match_id=
                            match_id,

                        bet_id=
                            bet_id,

                        season_name=
                            season_name,

                        league=
                            league,

                        mode=
                            mode,

                        fecha=
                            fecha,

                        local=
                            local,

                        visitante=
                            visitante,

                        motor=
                            "MULTI LAB",

                        sistema=
                            "MULTI SCORE",

                        marcador_apuesta=
                            score,

                        p_modelo=
                            probability,

                        stake=
                            MULTI_SCORE_STAKE,

                        real_score=
                            real_score,

                        nivel_core=
                            core_level,

                        perfil=
                            f"MULTI_{MULTI_SCORE_COUNT}",

                        operativa=
                            "LAB",

                    )

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
        "SISTEMA",
        "NIVEL_CORE",
        "PERFIL",
        "REGLA_VERSION",
        "OPERATIVA",
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

        multi_lab_bets = (

            bets["MOTOR"]

            .eq("MULTI LAB")

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

        multi_lab_bets = 0

        total_stake = 0

        unique_matches = 0

        unique_bets = 0


    print()
    print(
        f"Versión            : "
        f"{BET_SELECTOR_VERSION}"
    )

    print(
        f"Reglas             : "
        f"{RULE_VERSION}"
    )

    print(
        f"Temporada          : "
        f"{season_name}"
    )

    print(
        f"Liga               : "
        f"{league}"
    )

    print(
        f"Modo               : "
        f"{mode}"
    )

    print()

    print(
        f"Partidos apostados : "
        f"{unique_matches}"
    )

    print(
        f"Apuestas CORE      : "
        f"{core_bets}"
    )

    print(
        f"Apuestas RARE HOME : "
        f"{rare_home_bets}"
    )

    print(
        f"Apuestas RARE AWAY : "
        f"{rare_away_bets}"
    )

    print(
        f"Apuestas MULTI LAB : "
        f"{multi_lab_bets}"
    )

    print("-" * 40)

    print(
        f"Apuestas totales   : "
        f"{len(bets)}"
    )

    print(
        f"IDs únicos apuesta : "
        f"{unique_bets}"
    )

    print(
        f"Stake total        : "
        f"{total_stake:.2f}"
    )


    # ======================================================
    # CONTROL DE INTEGRIDAD
    # ======================================================

    if unique_bets != len(
        bets
    ):

        raise ValueError(

            "Existen ID_APUESTA duplicados "
            "en Bet Selector."

        )


    # ======================================================
    # CONTROL MULTI LAB
    # ======================================================

    if not ENABLE_MULTI_SCORE_LAB:

        if multi_lab_bets > 0:

            raise ValueError(

                "MULTI SCORE LAB está desactivado "
                "pero existen apuestas MULTI LAB."

            )


    return bets