"""
Portfolio Backtest

Evalúa conjuntamente los motores candidatos actuales
de CorrectScoreLab.

PORTFOLIO V0.1

CORE V0.1
-----------
Condición:
    P_TOP1 >= 0.16

Apuesta:
    TOP1 del modelo

Stake:
    1.0 unidad


RARE HOME V0.1
--------------
Condición:
    CS004_SHOTS_EDGE >= 1.0
    CS007_HOME_ATTACK_EDGE >= 2.0

Apuestas:
    4-0 -> Stake 0.5
    4-1 -> Stake 0.5


RARE AWAY V0.1
--------------
Condición:
    CS004_SHOTS_EDGE <= -0.5
    CS002_DOMINANCE <= -0.5
    CS007_AWAY_ATTACK_EDGE >= 1.2

Apuestas:
    0-3 -> Stake 0.5
    1-4 -> Stake 0.5


OBJETIVOS
---------
- Medir CORE y RARE por separado.
- Medir portfolio combinado.
- Detectar partidos con varios motores activos.
- Calcular exposición total.
- Calcular beneficio.
- Calcular ROI.
- Calcular drawdown.
- Calcular racha de jornadas/partidos negativos.
- Analizar rendimiento mensual.

España 2021/22 sigue siendo muestra de desarrollo.
"""

import pandas as pd


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

CORE_STAKE = 1.0
RARE_STAKE = 0.5

CORE_MIN_P = 0.16

RARE_HOME_SCORES = [
    "4-0",
    "4-1",
]

RARE_AWAY_SCORES = [
    "0-3",
    "1-4",
]


# ==========================================================
# PORTFOLIO BACKTEST
# ==========================================================

def backtest_portfolio(df):

    print()
    print("=" * 100)
    print("CORRECTSCORELAB - PORTFOLIO BACKTEST V0.1")
    print("=" * 100)

    data = df.copy()

    # ======================================================
    # VALIDACIÓN
    # ======================================================

    required_columns = [

        "TOP1",
        "P_TOP1",
        "VALID",
        "ODDS_REAL_SCORE",
        "CUOTA",

        "CS002_DOMINANCE",
        "CS004_SHOTS_EDGE",
        "CS007_HOME_ATTACK_EDGE",
        "CS007_AWAY_ATTACK_EDGE",

    ]

    missing = [

        column

        for column in required_columns

        if column not in data.columns

    ]

    if missing:

        raise ValueError(

            f"Faltan columnas para PortfolioBacktest: "
            f"{missing}"

        )

    # ======================================================
    # LIMPIEZA
    # ======================================================

    data["CUOTA"] = pd.to_numeric(

        data["CUOTA"],

        errors="coerce"

    )

    data["P_TOP1"] = pd.to_numeric(

        data["P_TOP1"],

        errors="coerce"

    )

    if "FECHA" in data.columns:

        data["FECHA"] = pd.to_datetime(

            data["FECHA"],

            errors="coerce"

        )

        data = data.sort_values(

            "FECHA"

        ).reset_index(

            drop=True

        )

    # ======================================================
    # SEÑALES
    # Solo partidos con histórico válido pueden generar apuesta
    # ======================================================

    data["_CORE"] = (

        data["VALID"].eq(True)

         &

         (
             data["P_TOP1"]
            >=
            CORE_MIN_P
         )

    )

    data["_RARE_HOME"] = (

         data["VALID"].eq(True)

         &

        (
             data["CS004_SHOTS_EDGE"]
              >= 1.0
         )

         &

         (
             data["CS007_HOME_ATTACK_EDGE"]
             >= 2.0
         )

    )

    data["_RARE_AWAY"] = (

         data["VALID"].eq(True)

         &

        (
            data["CS004_SHOTS_EDGE"]
             <= -0.5
         )

         &

         (
            data["CS002_DOMINANCE"]
             <= -0.5
        )

         &

        (
            data["CS007_AWAY_ATTACK_EDGE"]
             >= 1.2
         )

    )

    # ======================================================
    # RESULTADOS POR PARTIDO
    # ======================================================

    records = []

    for _, row in data.iterrows():

        real_score = str(

            row["ODDS_REAL_SCORE"]

        )

        odds = row["CUOTA"]

        core_active = bool(

            row["_CORE"]

        )

        rare_home_active = bool(

            row["_RARE_HOME"]

        )

        rare_away_active = bool(

            row["_RARE_AWAY"]

        )

        # ==================================================
        # CORE
        # ==================================================

        core_stake = 0.0
        core_return = 0.0

        if core_active:

            core_stake = (

                CORE_STAKE

            )

            if (

                str(row["TOP1"])

                ==

                real_score

            ):

                core_return = (

                    odds

                    *

                    CORE_STAKE

                )

        core_profit = (

            core_return

            -

            core_stake

        )

        # ==================================================
        # RARE HOME
        # ==================================================

        rare_home_stake = 0.0
        rare_home_return = 0.0

        if rare_home_active:

            rare_home_stake = (

                len(
                    RARE_HOME_SCORES
                )

                *

                RARE_STAKE

            )

            if (

                real_score

                in

                RARE_HOME_SCORES

            ):

                rare_home_return = (

                    odds

                    *

                    RARE_STAKE

                )

        rare_home_profit = (

            rare_home_return

            -

            rare_home_stake

        )

        # ==================================================
        # RARE AWAY
        # ==================================================

        rare_away_stake = 0.0
        rare_away_return = 0.0

        if rare_away_active:

            rare_away_stake = (

                len(
                    RARE_AWAY_SCORES
                )

                *

                RARE_STAKE

            )

            if (

                real_score

                in

                RARE_AWAY_SCORES

            ):

                rare_away_return = (

                    odds

                    *

                    RARE_STAKE

                )

        rare_away_profit = (

            rare_away_return

            -

            rare_away_stake

        )

        # ==================================================
        # PORTFOLIO
        # ==================================================

        total_stake = (

            core_stake

            +

            rare_home_stake

            +

            rare_away_stake

        )

        total_return = (

            core_return

            +

            rare_home_return

            +

            rare_away_return

        )

        total_profit = (

            total_return

            -

            total_stake

        )

        active_engines = sum(

            [

                core_active,

                rare_home_active,

                rare_away_active,

            ]

        )

        record = {

            "FECHA":

                row["FECHA"]

                if "FECHA" in row.index

                else pd.NaT,

            "LOCAL":

                row["LOCAL"]

                if "LOCAL" in row.index

                else "",

            "VISITANTE":

                row["VISITANTE"]

                if "VISITANTE" in row.index

                else "",

            "REAL_SCORE":

                real_score,

            "TOP1":

                row["TOP1"],

            "P_TOP1":

                row["P_TOP1"],

            "CUOTA":

                odds,

            "CORE_ACTIVE":

                core_active,

            "RARE_HOME_ACTIVE":

                rare_home_active,

            "RARE_AWAY_ACTIVE":

                rare_away_active,

            "ACTIVE_ENGINES":

                active_engines,

            "CORE_STAKE":

                core_stake,

            "CORE_RETURN":

                core_return,

            "CORE_PROFIT":

                core_profit,

            "RARE_HOME_STAKE":

                rare_home_stake,

            "RARE_HOME_RETURN":

                rare_home_return,

            "RARE_HOME_PROFIT":

                rare_home_profit,

            "RARE_AWAY_STAKE":

                rare_away_stake,

            "RARE_AWAY_RETURN":

                rare_away_return,

            "RARE_AWAY_PROFIT":

                rare_away_profit,

            "TOTAL_STAKE":

                total_stake,

            "TOTAL_RETURN":

                total_return,

            "TOTAL_PROFIT":

                total_profit,

        }

        records.append(

            record

        )

    portfolio = pd.DataFrame(

        records

    )

    # ======================================================
    # SOLO PARTIDOS CON APUESTA
    # ======================================================

    active = portfolio[

        portfolio["TOTAL_STAKE"]

        >

        0

    ].copy()

    # ======================================================
    # RESUMEN DE MOTOR
    # ======================================================

    def engine_summary(

        name,
        stake_column,
        return_column,
        profit_column

    ):

        engine_data = portfolio[

            portfolio[stake_column]

            >

            0

        ]

        signals = len(

            engine_data

        )

        stake = engine_data[

            stake_column

        ].sum()

        total_return = engine_data[

            return_column

        ].sum()

        profit = engine_data[

            profit_column

        ].sum()

        roi = (

            profit / stake

            if stake > 0

            else 0

        )

        return {

            "name": name,

            "signals": signals,

            "stake": stake,

            "return": total_return,

            "profit": profit,

            "roi": roi,

        }

    core_summary = engine_summary(

        "CORE",

        "CORE_STAKE",

        "CORE_RETURN",

        "CORE_PROFIT"

    )

    home_summary = engine_summary(

        "RARE HOME",

        "RARE_HOME_STAKE",

        "RARE_HOME_RETURN",

        "RARE_HOME_PROFIT"

    )

    away_summary = engine_summary(

        "RARE AWAY",

        "RARE_AWAY_STAKE",

        "RARE_AWAY_RETURN",

        "RARE_AWAY_PROFIT"

    )

    # ======================================================
    # MOSTRAR MOTORES
    # ======================================================

    print()
    print("RESULTADOS POR MOTOR")
    print("-" * 85)

    print(

        f"{'ENGINE':15}"

        f"{'SIGNALS':>10}"

        f"{'STAKE':>12}"

        f"{'RETURN':>12}"

        f"{'PROFIT':>12}"

        f"{'ROI':>12}"

    )

    for result in [

        core_summary,
        home_summary,
        away_summary,

    ]:

        print(

            f"{result['name']:15}"

            f"{result['signals']:>10}"

            f"{result['stake']:>12.2f}"

            f"{result['return']:>12.2f}"

            f"{result['profit']:>+12.2f}"

            f"{result['roi']:>+11.2%}"

        )

    # ======================================================
    # PORTFOLIO TOTAL
    # ======================================================

    total_matches = len(

        portfolio

    )

    active_matches = len(

        active

    )

    total_stake = active[

        "TOTAL_STAKE"

    ].sum()

    total_return = active[

        "TOTAL_RETURN"

    ].sum()

    total_profit = active[

        "TOTAL_PROFIT"

    ].sum()

    total_roi = (

        total_profit

        /

        total_stake

        if total_stake > 0

        else 0

    )

    print()
    print("=" * 85)
    print("PORTFOLIO TOTAL")
    print("=" * 85)

    print(
        f"Partidos analizados : "
        f"{total_matches}"
    )

    print(
        f"Partidos apostados  : "
        f"{active_matches}"
    )

    print(
        f"Stake total         : "
        f"{total_stake:.2f}"
    )

    print(
        f"Retorno             : "
        f"{total_return:.2f}"
    )

    print(
        f"Beneficio           : "
        f"{total_profit:+.2f}"
    )

    print(
        f"ROI                 : "
        f"{total_roi:+.2%}"
    )

    # ======================================================
    # SOLAPAMIENTOS
    # ======================================================

    core_home_overlap = (

        portfolio["CORE_ACTIVE"]

        &

        portfolio["RARE_HOME_ACTIVE"]

    ).sum()

    core_away_overlap = (

        portfolio["CORE_ACTIVE"]

        &

        portfolio["RARE_AWAY_ACTIVE"]

    ).sum()

    home_away_overlap = (

        portfolio["RARE_HOME_ACTIVE"]

        &

        portfolio["RARE_AWAY_ACTIVE"]

    ).sum()

    triple_overlap = (

        portfolio["CORE_ACTIVE"]

        &

        portfolio["RARE_HOME_ACTIVE"]

        &

        portfolio["RARE_AWAY_ACTIVE"]

    ).sum()

    print()
    print("=" * 85)
    print("SOLAPAMIENTOS")
    print("=" * 85)

    print(
        f"CORE + RARE HOME    : "
        f"{core_home_overlap}"
    )

    print(
        f"CORE + RARE AWAY    : "
        f"{core_away_overlap}"
    )

    print(
        f"RARE HOME + AWAY    : "
        f"{home_away_overlap}"
    )

    print(
        f"TRIPLE              : "
        f"{triple_overlap}"
    )

    # ======================================================
    # EXPOSICIÓN
    # ======================================================

    print()
    print("=" * 85)
    print("EXPOSICIÓN POR PARTIDO")
    print("=" * 85)

    exposure = (

        active[
            "TOTAL_STAKE"
        ]
        .value_counts()
        .sort_index()

    )

    for stake, count in exposure.items():

        print(

            f"Stake {stake:.2f} : "
            f"{count} partidos"

        )

    max_exposure = (

        active[
            "TOTAL_STAKE"
        ].max()

        if len(active) > 0

        else 0

    )

    print()
    print(
        f"Exposición máxima   : "
        f"{max_exposure:.2f}"
    )

    # ======================================================
    # DRAWDOWN DEL PORTFOLIO
    # ======================================================

    balance = 0.0
    peak = 0.0
    max_drawdown = 0.0

    current_losing_streak = 0
    max_losing_streak = 0

    for _, row in active.iterrows():

        profit = row[

            "TOTAL_PROFIT"

        ]

        balance += (

            profit

        )

        peak = max(

            peak,

            balance

        )

        drawdown = (

            peak

            -

            balance

        )

        max_drawdown = max(

            max_drawdown,

            drawdown

        )

        if profit < 0:

            current_losing_streak += 1

            max_losing_streak = max(

                max_losing_streak,

                current_losing_streak

            )

        else:

            current_losing_streak = 0

    print()
    print("=" * 85)
    print("RIESGO PORTFOLIO")
    print("=" * 85)

    print(
        f"Max Drawdown        : "
        f"{max_drawdown:.2f}"
    )

    print(
        f"Máx. racha negativa : "
        f"{max_losing_streak}"
    )

    # ======================================================
    # RENDIMIENTO MENSUAL
    # ======================================================

    if (

        "FECHA" in active.columns

        and

        active["FECHA"].notna().any()

    ):

        active["MES"] = (

            active["FECHA"]

            .dt.to_period("M")

            .astype(str)

        )

        monthly = (

            active

            .groupby("MES")

            .agg(

                PARTIDOS=(
                    "TOTAL_STAKE",
                    "size"
                ),

                STAKE=(
                    "TOTAL_STAKE",
                    "sum"
                ),

                RETURN=(
                    "TOTAL_RETURN",
                    "sum"
                ),

                PROFIT=(
                    "TOTAL_PROFIT",
                    "sum"
                ),

            )

            .reset_index()

        )

        monthly["ROI"] = (

            monthly["PROFIT"]

            /

            monthly["STAKE"]

        )

        print()
        print("=" * 85)
        print("RENDIMIENTO MENSUAL")
        print("=" * 85)

        print(

            f"{'MES':10}"

            f"{'PARTIDOS':>10}"

            f"{'STAKE':>12}"

            f"{'RETURN':>12}"

            f"{'PROFIT':>12}"

            f"{'ROI':>12}"

        )

        for _, row in monthly.iterrows():

            print(

                f"{row['MES']:10}"

                f"{int(row['PARTIDOS']):>10}"

                f"{row['STAKE']:>12.2f}"

                f"{row['RETURN']:>12.2f}"

                f"{row['PROFIT']:>+12.2f}"

                f"{row['ROI']:>+11.2%}"

            )

    # ======================================================
    # PARTIDOS CON SOLAPAMIENTO
    # ======================================================

    overlaps = active[

        active["ACTIVE_ENGINES"]

        >

        1

    ].copy()

    print()
    print("=" * 100)
    print("DETALLE DE SOLAPAMIENTOS")
    print("=" * 100)

    if len(overlaps) == 0:

        print(
            "No existen partidos con múltiples motores activos."
        )

    else:

        columns = [

            "FECHA",
            "LOCAL",
            "VISITANTE",
            "REAL_SCORE",
            "TOP1",
            "P_TOP1",
            "CORE_ACTIVE",
            "RARE_HOME_ACTIVE",
            "RARE_AWAY_ACTIVE",
            "TOTAL_STAKE",
            "TOTAL_RETURN",
            "TOTAL_PROFIT",

        ]

        print()

        print(

            overlaps[
                columns
            ].to_string(

                index=False

            )

        )

    return {

        "portfolio":

            portfolio,

        "active":

            active,

        "core":

            core_summary,

        "rare_home":

            home_summary,

        "rare_away":

            away_summary,

        "total": {

            "matches":

                active_matches,

            "stake":

                total_stake,

            "return":

                total_return,

            "profit":

                total_profit,

            "roi":

                total_roi,

            "max_drawdown":

                max_drawdown,

            "max_losing_streak":

                max_losing_streak,

        }

    }