"""
Blowout Detector Lab

Laboratorio experimental para detectar prepartido
posibles goleadas locales y visitantes.

OBJETIVOS:

1. Detectar zonas donde aumenta la concentración de goleadas.
2. Utilizar únicamente variables disponibles prepartido.
3. No modificar el Core Engine.
4. No optimizar agresivamente los umbrales.
5. Preparar señales que posteriormente puedan validarse
   en otras ligas y temporadas.

DEFINICIONES:

HOME BLOWOUT:
Victoria local por 3 o más goles de diferencia.

AWAY BLOWOUT:
Victoria visitante por 3 o más goles de diferencia.
"""

import pandas as pd


# ==========================================================
# ANALIZADOR PRINCIPAL
# ==========================================================

def analyze_blowout_detector(df):

    print()
    print("=" * 80)
    print("BLOWOUT DETECTOR LAB")
    print("=" * 80)

    data = df.copy()

    # ======================================================
    # VALIDACIÓN
    # ======================================================

    required_columns = [

        "ODDS_REAL_SCORE",
        "CUOTA",

        "CS001_ATTACK_EDGE",
        "CS002_DOMINANCE",
        "CS003_FORM_EDGE",
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

            f"Faltan columnas para BlowoutDetectorLab: "
            f"{missing}"

        )

    # ======================================================
    # EXTRAER MARCADOR REAL
    # ======================================================

    score_split = (

        data["ODDS_REAL_SCORE"]
        .astype(str)
        .str.split(
            "-",
            expand=True
        )

    )

    data["_HOME_GOALS"] = pd.to_numeric(

        score_split[0],

        errors="coerce"

    )

    data["_AWAY_GOALS"] = pd.to_numeric(

        score_split[1],

        errors="coerce"

    )

    data = data[

        data["_HOME_GOALS"].notna()

        &

        data["_AWAY_GOALS"].notna()

    ].copy()

    # ======================================================
    # DEFINIR GOLEADAS
    # ======================================================

    data["_GOAL_DIFF"] = (

        data["_HOME_GOALS"]

        -

        data["_AWAY_GOALS"]

    )

    data["_HOME_BLOWOUT"] = (

        data["_GOAL_DIFF"] >= 3

    )

    data["_AWAY_BLOWOUT"] = (

        data["_GOAL_DIFF"] <= -3

    )

    total_matches = len(data)

    home_blowouts = int(

        data["_HOME_BLOWOUT"].sum()

    )

    away_blowouts = int(

        data["_AWAY_BLOWOUT"].sum()

    )

    # ======================================================
    # BASELINE
    # ======================================================

    print()
    print("BASELINE")
    print("-" * 80)

    print(
        f"Partidos           : "
        f"{total_matches}"
    )

    print(
        f"Home Blowouts      : "
        f"{home_blowouts} "
        f"({home_blowouts / total_matches:.2%})"
    )

    print(
        f"Away Blowouts      : "
        f"{away_blowouts} "
        f"({away_blowouts / total_matches:.2%})"
    )

    # ======================================================
    # FUNCIÓN PARA EVALUAR SEÑALES
    # ======================================================

    def evaluate_signal(

        name,
        mask,
        target_column

    ):

        selected = data[
            mask
        ]

        signals = len(selected)

        if signals == 0:

            return None

        hits = int(

            selected[
                target_column
            ].sum()

        )

        precision = (

            hits / signals

        )

        total_target = int(

            data[
                target_column
            ].sum()

        )

        recall = (

            hits / total_target

            if total_target > 0

            else 0

        )

        avg_odds = (

            selected.loc[

                selected[
                    target_column
                ],

                "CUOTA"

            ].mean()

        )

        return {

            "name": name,

            "signals": signals,

            "hits": hits,

            "precision": precision,

            "recall": recall,

            "avg_hit_odds": avg_odds,

        }

    # ======================================================
    # HOME BLOWOUT SIGNALS
    # ======================================================
    #
    # Los umbrales son deliberadamente simples.
    # No buscamos todavía el mejor resultado posible.
    # ======================================================

    home_signals = [

        (

            "H1 SHOTS >= 1.0",

            data[
                "CS004_SHOTS_EDGE"
            ] >= 1.0

        ),

        (

            "H2 SHOTS >= 1.5",

            data[
                "CS004_SHOTS_EDGE"
            ] >= 1.5

        ),

        (

            "H3 HOME_ATTACK >= 2.0",

            data[
                "CS007_HOME_ATTACK_EDGE"
            ] >= 2.0

        ),

        (

            "H4 DOMINANCE >= 0.5",

            data[
                "CS002_DOMINANCE"
            ] >= 0.5

        ),

        (

            "H5 SHOTS >= 1.0 + HOME_ATTACK >= 2.0",

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

        ),

        (

            "H6 SHOTS >= 1.0 + DOMINANCE >= 0.5",

            (

                data[
                    "CS004_SHOTS_EDGE"
                ] >= 1.0

            )

            &

            (

                data[
                    "CS002_DOMINANCE"
                ] >= 0.5

            )

        ),

        (

            "H7 HOME_ATTACK >= 2.0 + DOMINANCE >= 0.5",

            (

                data[
                    "CS007_HOME_ATTACK_EDGE"
                ] >= 2.0

            )

            &

            (

                data[
                    "CS002_DOMINANCE"
                ] >= 0.5

            )

        ),

        (

            "H8 TRIPLE",

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

            &

            (

                data[
                    "CS002_DOMINANCE"
                ] >= 0.5

            )

        ),

    ]

    # ======================================================
    # AWAY BLOWOUT SIGNALS
    # ======================================================

    away_signals = [

        (

            "A1 SHOTS <= -0.5",

            data[
                "CS004_SHOTS_EDGE"
            ] <= -0.5

        ),

        (

            "A2 SHOTS <= -1.0",

            data[
                "CS004_SHOTS_EDGE"
            ] <= -1.0

        ),

        (

            "A3 DOMINANCE <= -0.5",

            data[
                "CS002_DOMINANCE"
            ] <= -0.5

        ),

        (

            "A4 AWAY_ATTACK >= 1.2",

            data[
                "CS007_AWAY_ATTACK_EDGE"
            ] >= 1.2

        ),

        (

            "A5 SHOTS <= -0.5 + DOMINANCE <= -0.5",

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

        ),

        (

            "A6 SHOTS <= -0.5 + AWAY_ATTACK >= 1.2",

            (

                data[
                    "CS004_SHOTS_EDGE"
                ] <= -0.5

            )

            &

            (

                data[
                    "CS007_AWAY_ATTACK_EDGE"
                ] >= 1.2

            )

        ),

        (

            "A7 DOMINANCE <= -0.5 + AWAY_ATTACK >= 1.2",

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

        ),

        (

            "A8 TRIPLE",

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

        ),

    ]

    # ======================================================
    # MOSTRAR RESULTADOS
    # ======================================================

    def print_results(

        title,
        signals,
        target

    ):

        print()
        print("=" * 100)
        print(title)
        print("=" * 100)

        print(

            f"{'SIGNAL':50}"

            f"{'N':>8}"

            f"{'HITS':>8}"

            f"{'PRECISION':>12}"

            f"{'RECALL':>10}"

            f"{'AVG HIT ODDS':>15}"

        )

        results = []

        for name, mask in signals:

            result = evaluate_signal(

                name,
                mask,
                target

            )

            if result is None:

                continue

            results.append(
                result
            )

            avg_odds = (

                result[
                    "avg_hit_odds"
                ]

            )

            avg_odds_text = (

                f"{avg_odds:.2f}"

                if pd.notna(avg_odds)

                else "-"

            )

            print(

                f"{result['name']:50}"

                f"{result['signals']:>8}"

                f"{result['hits']:>8}"

                f"{result['precision']:>11.2%}"

                f"{result['recall']:>9.2%}"

                f"{avg_odds_text:>15}"

            )

        return results

    home_results = print_results(

        "HOME BLOWOUT DETECTOR",

        home_signals,

        "_HOME_BLOWOUT"

    )

    away_results = print_results(

        "AWAY BLOWOUT DETECTOR",

        away_signals,

        "_AWAY_BLOWOUT"

    )

    # ======================================================
    # MEJORES SEÑALES POR PRECISIÓN
    # ======================================================

    print()
    print("=" * 80)
    print("MEJORES SEÑALES")
    print("=" * 80)

    for label, results in [

        (
            "HOME",
            home_results
        ),

        (
            "AWAY",
            away_results
        ),

    ]:

        valid_results = [

            result

            for result in results

            if result["signals"] >= 5

        ]

        if not valid_results:

            continue

        best = max(

            valid_results,

            key=lambda x: x["precision"]

        )

        print()

        print(
            f"{label}:"
        )

        print(
            f"Señal      : "
            f"{best['name']}"
        )

        print(
            f"Partidos   : "
            f"{best['signals']}"
        )

        print(
            f"Goleadas   : "
            f"{best['hits']}"
        )

        print(
            f"Precisión  : "
            f"{best['precision']:.2%}"
        )

        print(
            f"Recall     : "
            f"{best['recall']:.2%}"
        )

    # ======================================================
    # DETALLE DE LA SEÑAL TRIPLE HOME
    # ======================================================

    home_triple_mask = (

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

        &

        (
            data[
                "CS002_DOMINANCE"
            ] >= 0.5
        )

    )

    # ======================================================
    # DETALLE DE LA SEÑAL TRIPLE AWAY
    # ======================================================

    away_triple_mask = (

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

    # ======================================================
    # MOSTRAR PARTIDOS SELECCIONADOS
    # ======================================================

    def show_selected(

        title,
        mask,
        target

    ):

        selected = data[
            mask
        ].copy()

        print()
        print("=" * 100)
        print(title)
        print("=" * 100)

        if len(selected) == 0:

            print()
            print(
                "No hay partidos seleccionados."
            )

            return

        columns = [

            column

            for column in [

                "FECHA",
                "LOCAL",
                "VISITANTE",
                "ODDS_REAL_SCORE",
                "CUOTA",
                "TOP1",
                "P_TOP1",

                "CS004_SHOTS_EDGE",
                "CS007_HOME_ATTACK_EDGE",
                "CS007_AWAY_ATTACK_EDGE",
                "CS002_DOMINANCE",

                target,

            ]

            if column in selected.columns

        ]

        print()

        print(

            selected[
                columns
            ].to_string(

                index=False

            )

        )

    show_selected(

        "PARTIDOS SELECCIONADOS - HOME TRIPLE",

        home_triple_mask,

        "_HOME_BLOWOUT"

    )

    show_selected(

        "PARTIDOS SELECCIONADOS - AWAY TRIPLE",

        away_triple_mask,

        "_AWAY_BLOWOUT"

    )