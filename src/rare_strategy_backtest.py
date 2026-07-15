"""
Rare Strategy Backtest

Simula estrategias de Correct Score para el RARE ENGINE.

Concepto:

HOME H5:
    SHOTS_EDGE >= 1.0
    HOME_ATTACK_EDGE >= 2.0

AWAY A8:
    SHOTS_EDGE <= -0.5
    DOMINANCE <= -0.5
    AWAY_ATTACK_EDGE >= 1.2

Cuando aparece una señal:

- Apostamos a 2 o 3 marcadores.
- Stake = 0.5 unidades por marcador.
- Si ningún marcador acierta, se pierde todo el stake.
- Si un marcador acierta, el retorno se calcula:
      cuota_real * 0.5

IMPORTANTE:

Este laboratorio NO modifica el Core Engine.
Los detectores H5 y A8 quedan congelados para esta prueba.
"""

import pandas as pd


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

STAKE_PER_SCORE = 0.5


# ==========================================================
# ANALIZADOR PRINCIPAL
# ==========================================================

def backtest_rare_strategies(df):

    print()
    print("=" * 90)
    print("RARE STRATEGY BACKTEST")
    print("=" * 90)

    data = df.copy()

    # ======================================================
    # VALIDACIÓN
    # ======================================================

    required_columns = [

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

            f"Faltan columnas para RareStrategyBacktest: "
            f"{missing}"

        )

    # ======================================================
    # LIMPIAR CUOTA
    # ======================================================

    data["CUOTA"] = pd.to_numeric(

        data["CUOTA"],

        errors="coerce"

    )

    # ======================================================
    # DETECTORES CONGELADOS
    # ======================================================

    # HOME H5
    #
    # SHOTS >= 1.0
    # HOME ATTACK >= 2.0

    home_mask = (

        (
            data[
                "CS004_SHOTS_EDGE"
            ] >= 1.0
        )

        &

        (
            data[
                "CS007_HOME_ATTACK_EDGE"
            ] >= 2.0
        )

    )

    # AWAY A8
    #
    # SHOTS <= -0.5
    # DOMINANCE <= -0.5
    # AWAY ATTACK >= 1.2

    away_mask = (

        (
            data[
                "CS004_SHOTS_EDGE"
            ] <= -0.5
        )

        &

        (
            data[
                "CS002_DOMINANCE"
            ] <= -0.5
        )

        &

        (
            data[
                "CS007_AWAY_ATTACK_EDGE"
            ] >= 1.2
        )

    )

    home_data = data[
        home_mask
    ].copy()

    away_data = data[
        away_mask
    ].copy()

    # ======================================================
    # ESTRATEGIAS
    # ======================================================
    #
    # No buscamos optimizar todos los resultados posibles.
    #
    # Probamos familias lógicas de 2 y 3 marcadores.
    # ======================================================

    home_strategies = {

        # --------------------------
        # 2 MARCADORES
        # --------------------------

        "HOME_2_A":

            [
                "3-0",
                "3-1",
            ],

        "HOME_2_B":

            [
                "3-0",
                "4-0",
            ],

        "HOME_2_C":

            [
                "3-0",
                "4-1",
            ],

        "HOME_2_D":

            [
                "3-1",
                "4-1",
            ],

        "HOME_2_E":

            [
                "4-0",
                "4-1",
            ],

        # --------------------------
        # 3 MARCADORES
        # --------------------------

        "HOME_3_A":

            [
                "3-0",
                "3-1",
                "4-0",
            ],

        "HOME_3_B":

            [
                "3-0",
                "3-1",
                "4-1",
            ],

        "HOME_3_C":

            [
                "3-0",
                "4-0",
                "4-1",
            ],

    }

    away_strategies = {

        # --------------------------
        # 2 MARCADORES
        # --------------------------

        "AWAY_2_A":

            [
                "0-3",
                "1-3",
            ],

        "AWAY_2_B":

            [
                "0-3",
                "0-4",
            ],

        "AWAY_2_C":

            [
                "0-3",
                "1-4",
            ],

        "AWAY_2_D":

            [
                "1-3",
                "1-4",
            ],

        "AWAY_2_E":

            [
                "0-4",
                "1-4",
            ],

        # --------------------------
        # 3 MARCADORES
        # --------------------------

        "AWAY_3_A":

            [
                "0-3",
                "1-3",
                "0-4",
            ],

        "AWAY_3_B":

            [
                "0-3",
                "1-3",
                "1-4",
            ],

        "AWAY_3_C":

            [
                "0-3",
                "0-4",
                "1-4",
            ],

    }

    # ======================================================
    # BACKTEST DE UNA ESTRATEGIA
    # ======================================================

    def evaluate_strategy(

        signal_data,
        strategy_name,
        scores

    ):

        signals = len(
            signal_data
        )

        number_scores = len(
            scores
        )

        stake_per_signal = (

            number_scores

            *

            STAKE_PER_SCORE

        )

        total_stake = (

            signals

            *

            stake_per_signal

        )

        hits_mask = (

            signal_data[
                "ODDS_REAL_SCORE"
            ].isin(
                scores
            )

        )

        hits = int(

            hits_mask.sum()

        )

        hit_rate = (

            hits / signals

            if signals > 0

            else 0

        )

        winning_matches = signal_data[

            hits_mask

        ].copy()

        # Cada acierto tiene stake 0.5
        #
        # Retorno:
        #
        # cuota * 0.5

        total_return = (

            winning_matches[
                "CUOTA"
            ]

            *

            STAKE_PER_SCORE

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

            winning_matches[
                "CUOTA"
            ].mean()

            if hits > 0

            else 0

        )

        # ==================================================
        # RACHA MÁXIMA SIN ACIERTO
        # ==================================================

        max_losing_streak = 0

        current_losing_streak = 0

        for hit in hits_mask:

            if hit:

                current_losing_streak = 0

            else:

                current_losing_streak += 1

                max_losing_streak = max(

                    max_losing_streak,

                    current_losing_streak

                )

        return {

            "strategy": strategy_name,

            "scores": scores,

            "signals": signals,

            "number_scores": number_scores,

            "stake_signal": stake_per_signal,

            "total_stake": total_stake,

            "hits": hits,

            "hit_rate": hit_rate,

            "avg_hit_odds": avg_hit_odds,

            "return": total_return,

            "profit": profit,

            "roi": roi,

            "max_losing_streak":
                max_losing_streak,

        }

    # ======================================================
    # EJECUTAR GRUPO DE ESTRATEGIAS
    # ======================================================

    def run_strategies(

        title,
        signal_data,
        strategies

    ):

        print()
        print("=" * 120)
        print(title)
        print("=" * 120)

        print(
            f"Señales detectadas : "
            f"{len(signal_data)}"
        )

        print(
            f"Stake por marcador : "
            f"{STAKE_PER_SCORE:.2f}"
        )

        print()

        print(

            f"{'STRATEGY':12}"

            f"{'SCORES':25}"

            f"{'SIGNALS':>8}"

            f"{'STAKE':>10}"

            f"{'HITS':>8}"

            f"{'HIT%':>10}"

            f"{'AVG ODDS':>12}"

            f"{'RETURN':>12}"

            f"{'PROFIT':>12}"

            f"{'ROI':>10}"

            f"{'MAX LS':>10}"

        )

        results = []

        for (

            strategy_name,
            scores

        ) in strategies.items():

            result = evaluate_strategy(

                signal_data,

                strategy_name,

                scores

            )

            results.append(
                result
            )

            scores_text = (

                " + ".join(
                    scores
                )

            )

            print(

                f"{strategy_name:12}"

                f"{scores_text:25}"

                f"{result['signals']:>8}"

                f"{result['total_stake']:>10.2f}"

                f"{result['hits']:>8}"

                f"{result['hit_rate']:>9.2%}"

                f"{result['avg_hit_odds']:>12.2f}"

                f"{result['return']:>12.2f}"

                f"{result['profit']:>+12.2f}"

                f"{result['roi']:>+9.2%}"

                f"{result['max_losing_streak']:>10}"

            )

        return results

    # ======================================================
    # EJECUTAR HOME
    # ======================================================

    home_results = run_strategies(

        "RARE ENGINE - HOME H5",

        home_data,

        home_strategies

    )

    # ======================================================
    # EJECUTAR AWAY
    # ======================================================

    away_results = run_strategies(

        "RARE ENGINE - AWAY A8",

        away_data,

        away_strategies

    )

    # ======================================================
    # MEJOR ESTRATEGIA
    # ======================================================

    print()
    print("=" * 90)
    print("MEJORES RESULTADOS - SOLO EXPLORATORIO")
    print("=" * 90)

    for (

        label,
        results

    ) in [

        (
            "HOME",
            home_results
        ),

        (
            "AWAY",
            away_results
        ),

    ]:

        if not results:

            continue

        best_roi = max(

            results,

            key=lambda x: x["roi"]

        )

        print()
        print(
            label
        )
        print("-" * 50)

        print(
            f"Estrategia       : "
            f"{best_roi['strategy']}"
        )

        print(
            f"Marcadores       : "
            f"{' + '.join(best_roi['scores'])}"
        )

        print(
            f"Señales          : "
            f"{best_roi['signals']}"
        )

        print(
            f"Stake total      : "
            f"{best_roi['total_stake']:.2f}"
        )

        print(
            f"Aciertos         : "
            f"{best_roi['hits']}"
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
            f"Máx. racha fallo : "
            f"{best_roi['max_losing_streak']}"
        )

    # ======================================================
    # DISTRIBUCIÓN REAL DE LAS SEÑALES
    # ======================================================

    def show_real_distribution(

        title,
        signal_data

    ):

        print()
        print("=" * 70)
        print(title)
        print("=" * 70)

        distribution = (

            signal_data[
                "ODDS_REAL_SCORE"
            ]
            .value_counts()

        )

        for score, count in distribution.items():

            percentage = (

                count

                /

                len(signal_data)

            )

            avg_odds = (

                signal_data.loc[

                    signal_data[
                        "ODDS_REAL_SCORE"
                    ] == score,

                    "CUOTA"

                ].mean()

            )

            print(

                f"{str(score):6}"

                f"{count:5} veces   "

                f"{percentage:7.2%}   "

                f"cuota media "
                f"{avg_odds:7.2f}"

            )

    show_real_distribution(

        "DISTRIBUCIÓN REAL - HOME H5",

        home_data

    )

    show_real_distribution(

        "DISTRIBUCIÓN REAL - AWAY A8",

        away_data

    )

    return {

        "home": home_results,

        "away": away_results,

    }