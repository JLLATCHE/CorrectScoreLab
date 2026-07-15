"""
Core Selector Lab

Laboratorio para estudiar reglas de selección del CORE ENGINE.

Objetivo:

- No apostar automáticamente todos los TOP1.
- Detectar cuándo una predicción TOP1 tiene suficiente calidad.
- Stake fijo = 1 unidad por selección.
- Evaluar rentabilidad y riesgo.

IMPORTANTE:

Este laboratorio es exploratorio.
España 2021/22 es muestra de desarrollo.
Las reglas candidatas deberán validarse posteriormente
sin modificaciones en otras ligas y temporadas.
"""

import pandas as pd


STAKE = 1.0


def analyze_core_selectors(df):

    print()
    print("=" * 100)
    print("CORE SELECTOR LAB")
    print("=" * 100)

    data = df.copy()

    # ======================================================
    # VALIDACIÓN
    # ======================================================

    required_columns = [

        "TOP1",
        "P_TOP1",
        "ODDS_REAL_SCORE",
        "CUOTA",

    ]

    missing = [

        column

        for column in required_columns

        if column not in data.columns

    ]

    if missing:

        raise ValueError(

            f"Faltan columnas para CoreSelectorLab: "
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

    # Orden cronológico si existe FECHA

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
    # ESTRATEGIAS
    # ======================================================

    strategies = {

        # ==================================================
        # BASELINES
        # ==================================================

        "ALL_TOP1":

            pd.Series(
                True,
                index=data.index
            ),

        "P_012":

            data["P_TOP1"] >= 0.12,

        "P_014":

            data["P_TOP1"] >= 0.14,

        "P_016":

            data["P_TOP1"] >= 0.16,

        "P_018":

            data["P_TOP1"] >= 0.18,

        "P_020":

            data["P_TOP1"] >= 0.20,

        # ==================================================
        # 1-0
        # ==================================================

        "S10_ALL":

            data["TOP1"] == "1-0",

        "S10_P014":

            (
                (data["TOP1"] == "1-0")
                &
                (data["P_TOP1"] >= 0.14)
            ),

        "S10_P015":

            (
                (data["TOP1"] == "1-0")
                &
                (data["P_TOP1"] >= 0.15)
            ),

        "S10_P016":

            (
                (data["TOP1"] == "1-0")
                &
                (data["P_TOP1"] >= 0.16)
            ),

        "S10_P018":

            (
                (data["TOP1"] == "1-0")
                &
                (data["P_TOP1"] >= 0.18)
            ),

        # ==================================================
        # 0-0
        # ==================================================

        "S00_ALL":

            data["TOP1"] == "0-0",

        "S00_P015":

            (
                (data["TOP1"] == "0-0")
                &
                (data["P_TOP1"] >= 0.15)
            ),

        "S00_P018":

            (
                (data["TOP1"] == "0-0")
                &
                (data["P_TOP1"] >= 0.18)
            ),

        "S00_P020":

            (
                (data["TOP1"] == "0-0")
                &
                (data["P_TOP1"] >= 0.20)
            ),

        # ==================================================
        # 1-0 + 0-0
        # ==================================================

        "CORE_10_00_ALL":

            data["TOP1"].isin(
                [
                    "1-0",
                    "0-0",
                ]
            ),

        "CORE_10_00_P015":

            (
                data["TOP1"].isin(
                    [
                        "1-0",
                        "0-0",
                    ]
                )
                &
                (data["P_TOP1"] >= 0.15)
            ),

        "CORE_10_00_P018":

            (
                data["TOP1"].isin(
                    [
                        "1-0",
                        "0-0",
                    ]
                )
                &
                (data["P_TOP1"] >= 0.18)
            ),

        "CORE_10_00_P020":

            (
                data["TOP1"].isin(
                    [
                        "1-0",
                        "0-0",
                    ]
                )
                &
                (data["P_TOP1"] >= 0.20)
            ),

    }

    # ======================================================
    # EVALUAR ESTRATEGIA
    # ======================================================

    def evaluate_strategy(

        name,
        mask

    ):

        selected = data[
            mask
        ].copy()

        bets = len(
            selected
        )

        if bets == 0:

            return None

        # El TOP1 acierta cuando coincide
        # con el marcador real

        selected["_HIT"] = (

            selected["TOP1"]

            ==

            selected["ODDS_REAL_SCORE"]

        )

        hits = int(

            selected["_HIT"].sum()

        )

        hit_rate = (

            hits / bets

        )

        total_stake = (

            bets * STAKE

        )

        winners = selected[

            selected["_HIT"]

        ].copy()

        # Retorno:
        # cuota real del marcador acertado
        # multiplicada por stake 1

        total_return = (

            winners["CUOTA"]

            * STAKE

        ).sum()

        profit = (

            total_return

            -

            total_stake

        )

        roi = (

            profit

            /

            total_stake

            if total_stake > 0

            else 0

        )

        avg_hit_odds = (

            winners["CUOTA"].mean()

            if hits > 0

            else 0

        )

        # ==================================================
        # RACHA MÁXIMA DE FALLOS
        # ==================================================

        max_losing_streak = 0
        current_losing_streak = 0

        for hit in selected["_HIT"]:

            if hit:

                current_losing_streak = 0

            else:

                current_losing_streak += 1

                max_losing_streak = max(

                    max_losing_streak,

                    current_losing_streak

                )

        # ==================================================
        # CURVA DE BENEFICIO
        # ==================================================

        balance = 0.0

        peak = 0.0

        max_drawdown = 0.0

        gross_profit = 0.0
        gross_loss = 0.0

        for _, row in selected.iterrows():

            # Apostamos 1 unidad

            if row["_HIT"]:

                bet_profit = (

                    row["CUOTA"]

                    -

                    STAKE

                )

                gross_profit += (

                    bet_profit

                )

            else:

                bet_profit = (

                    -STAKE

                )

                gross_loss += (

                    STAKE

                )

            balance += (

                bet_profit

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

        # ==================================================
        # PROFIT FACTOR
        # ==================================================

        profit_factor = (

            gross_profit

            /

            gross_loss

            if gross_loss > 0

            else float("inf")

        )

        return {

            "strategy": name,

            "bets": bets,

            "hits": hits,

            "hit_rate": hit_rate,

            "avg_hit_odds": avg_hit_odds,

            "stake": total_stake,

            "return": total_return,

            "profit": profit,

            "roi": roi,

            "max_losing_streak":
                max_losing_streak,

            "max_drawdown":
                max_drawdown,

            "profit_factor":
                profit_factor,

        }

    # ======================================================
    # EJECUTAR
    # ======================================================

    results = []

    print()

    print(

        f"{'STRATEGY':20}"

        f"{'BETS':>7}"

        f"{'HITS':>7}"

        f"{'HIT%':>10}"

        f"{'AVG ODDS':>11}"

        f"{'RETURN':>11}"

        f"{'PROFIT':>11}"

        f"{'ROI':>10}"

        f"{'MAX LS':>9}"

        f"{'MAX DD':>10}"

        f"{'PF':>9}"

    )

    print("-" * 115)

    for (

        strategy_name,
        mask

    ) in strategies.items():

        result = evaluate_strategy(

            strategy_name,

            mask

        )

        if result is None:

            continue

        results.append(
            result
        )

        print(

            f"{result['strategy']:20}"

            f"{result['bets']:>7}"

            f"{result['hits']:>7}"

            f"{result['hit_rate']:>9.2%}"

            f"{result['avg_hit_odds']:>11.2f}"

            f"{result['return']:>11.2f}"

            f"{result['profit']:>+11.2f}"

            f"{result['roi']:>+9.2%}"

            f"{result['max_losing_streak']:>9}"

            f"{result['max_drawdown']:>10.2f}"

            f"{result['profit_factor']:>9.2f}"

        )

    # ======================================================
    # MEJOR ROI
    # ======================================================

    if results:

        best_roi = max(

            results,

            key=lambda x: x["roi"]

        )

        print()
        print("=" * 70)
        print("MEJOR ROI - SOLO EXPLORATORIO")
        print("=" * 70)

        print(
            f"Estrategia       : "
            f"{best_roi['strategy']}"
        )

        print(
            f"Apuestas         : "
            f"{best_roi['bets']}"
        )

        print(
            f"Aciertos         : "
            f"{best_roi['hits']}"
        )

        print(
            f"Hit Rate         : "
            f"{best_roi['hit_rate']:.2%}"
        )

        print(
            f"Cuota media hit  : "
            f"{best_roi['avg_hit_odds']:.2f}"
        )

        print(
            f"Stake total      : "
            f"{best_roi['stake']:.2f}"
        )

        print(
            f"Retorno          : "
            f"{best_roi['return']:.2f}"
        )

        print(
            f"Beneficio        : "
            f"{best_roi['profit']:+.2f}"
        )

        print(
            f"ROI              : "
            f"{best_roi['roi']:+.2%}"
        )

        print(
            f"Profit Factor    : "
            f"{best_roi['profit_factor']:.2f}"
        )

        print(
            f"Max Drawdown     : "
            f"{best_roi['max_drawdown']:.2f}"
        )

        print(
            f"Máx. racha fallo : "
            f"{best_roi['max_losing_streak']}"
        )

    return results