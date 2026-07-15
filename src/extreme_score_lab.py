"""
Extreme Score Lab

Analiza si las variables prepartido de CorrectScoreLab
permiten detectar diferentes tipos de resultados extremos.

NO modifica el predictor.
NO modifica probabilidades.
NO modifica la BASE.

Es únicamente un laboratorio de investigación.
"""


import pandas as pd


# ==========================================================
# ANALIZADOR PRINCIPAL
# ==========================================================

def analyze_extreme_scores(df):

    print()
    print("=" * 70)
    print("EXTREME SCORE LAB")
    print("=" * 70)

    data = df.copy()

    # ======================================================
    # VALIDACIÓN
    # ======================================================

    required_columns = [

        "ODDS_REAL_SCORE",
        "TOP1",
        "P_TOP1",
        "ODDS_TOP1_HIT",
        "ODDS_TOP3_HIT",
        "ODDS_TOP5_HIT",

    ]

    missing = [

        column

        for column in required_columns

        if column not in data.columns

    ]

    if missing:

        raise ValueError(

            f"Faltan columnas para ExtremeScoreLab: "
            f"{missing}"

        )

    # ======================================================
    # EXTRAER GOLES REALES
    # ======================================================

    score_split = (

        data["ODDS_REAL_SCORE"]
        .astype(str)
        .str.split(
            "-",
            expand=True
        )

    )

    data["_REAL_HOME_GOALS"] = pd.to_numeric(

        score_split[0],

        errors="coerce"

    )

    data["_REAL_AWAY_GOALS"] = pd.to_numeric(

        score_split[1],

        errors="coerce"

    )

    invalid_scores = (

        data["_REAL_HOME_GOALS"].isna()

        |

        data["_REAL_AWAY_GOALS"].isna()

    ).sum()

    if invalid_scores > 0:

        print()
        print(
            f"Marcadores inválidos ignorados: "
            f"{invalid_scores}"
        )

        data = data[

            data["_REAL_HOME_GOALS"].notna()

            &

            data["_REAL_AWAY_GOALS"].notna()

        ].copy()

    # ======================================================
    # VARIABLES DEL RESULTADO
    # ======================================================

    data["_TOTAL_GOALS"] = (

        data["_REAL_HOME_GOALS"]

        +

        data["_REAL_AWAY_GOALS"]

    )

    data["_GOAL_DIFF"] = (

        data["_REAL_HOME_GOALS"]

        -

        data["_REAL_AWAY_GOALS"]

    )

    data["_BTTS"] = (

        (data["_REAL_HOME_GOALS"] > 0)

        &

        (data["_REAL_AWAY_GOALS"] > 0)

    )

    # ======================================================
    # DEFINICIÓN DE PERFILES
    # ======================================================
    #
    # IMPORTANTE:
    #
    # Los grupos pueden solaparse.
    #
    # Ejemplo:
    # 4-2 puede ser:
    #
    # HIGH SCORING
    # CHAOS
    # EXTREME
    #
    # Esto es intencionado porque queremos estudiar
    # cada fenómeno por separado.
    # ======================================================

    groups = {

        "ALL MATCHES":

            data,

        "LOW SCORING - TOTAL <= 2":

            data[
                data["_TOTAL_GOALS"] <= 2
            ],

        "HIGH SCORING - TOTAL >= 5":

            data[
                data["_TOTAL_GOALS"] >= 5
            ],

        "HOME BLOWOUT - DIF >= 3":

            data[
                data["_GOAL_DIFF"] >= 3
            ],

        "AWAY BLOWOUT - DIF <= -3":

            data[
                data["_GOAL_DIFF"] <= -3
            ],

        "CHAOS - BTTS + TOTAL >= 5":

            data[
                data["_BTTS"]

                &

                (data["_TOTAL_GOALS"] >= 5)
            ],

        "EXTREME - TOTAL >= 6":

            data[
                data["_TOTAL_GOALS"] >= 6
            ],

    }

    # ======================================================
    # RESUMEN GENERAL
    # ======================================================

    print()
    print("RESUMEN POR PERFIL")
    print("=" * 90)

    print(

        f"{'PERFIL':35}"
        f"{'MATCHES':>10}"
        f"{'% TOTAL':>10}"
        f"{'TOP1':>10}"
        f"{'TOP3':>10}"
        f"{'TOP5':>10}"
        f"{'P_TOP1':>12}"

    )

    total_matches = len(data)

    for label, group in groups.items():

        matches = len(group)

        if matches == 0:

            continue

        percentage = (

            matches / total_matches

            if total_matches > 0

            else 0

        )

        top1 = (
            group["ODDS_TOP1_HIT"].mean()
        )

        top3 = (
            group["ODDS_TOP3_HIT"].mean()
        )

        top5 = (
            group["ODDS_TOP5_HIT"].mean()
        )

        p_top1 = (
            group["P_TOP1"].mean()
        )

        print(

            f"{label:35}"

            f"{matches:>10}"

            f"{percentage:>9.2%}"

            f"{top1:>9.2%}"

            f"{top3:>9.2%}"

            f"{top5:>9.2%}"

            f"{p_top1:>12.4f}"

        )

    # ======================================================
    # DISTRIBUCIÓN DE MARCADORES POR PERFIL
    # ======================================================

    for label, group in groups.items():

        if label == "ALL MATCHES":

            continue

        if len(group) == 0:

            continue

        print()
        print("=" * 70)
        print(label)
        print("=" * 70)

        score_counts = (

            group["ODDS_REAL_SCORE"]
            .value_counts()

        )

        print()
        print("MARCADORES REALES")
        print("-" * 50)

        for score, count in score_counts.items():

            percentage = (

                count / len(group)

            )

            print(

                f"{str(score):6}"

                f"{count:5} partidos   "

                f"{percentage:7.2%}"

            )

    # ======================================================
    # QUÉ PREDICE TOP1 EN CADA PERFIL
    # ======================================================

    print()
    print("=" * 70)
    print("COMPORTAMIENTO DEL TOP1")
    print("=" * 70)

    for label, group in groups.items():

        if label == "ALL MATCHES":

            continue

        if len(group) == 0:

            continue

        print()
        print(label)
        print("-" * 60)

        predictions = (

            group["TOP1"]
            .value_counts()
            .head(10)

        )

        for score, count in predictions.items():

            percentage = (

                count / len(group)

            )

            print(

                f"{str(score):6}"

                f"{count:5} predicciones   "

                f"{percentage:7.2%}"

            )

    # ======================================================
    # VARIABLES CS
    # ======================================================

    cs_columns = sorted([

        column

        for column in data.columns

        if column.startswith("CS")

    ])

    # ======================================================
    # COMPARACIÓN:
    #
    # Cada perfil contra todos los partidos que NO
    # pertenecen a ese perfil.
    #
    # Esto es más útil que comparar simplemente contra
    # la media global.
    # ======================================================

    profiles_to_compare = {

        "HIGH SCORING":

            data["_TOTAL_GOALS"] >= 5,

        "HOME BLOWOUT":

            data["_GOAL_DIFF"] >= 3,

        "AWAY BLOWOUT":

            data["_GOAL_DIFF"] <= -3,

        "CHAOS":

            data["_BTTS"]

            &

            (data["_TOTAL_GOALS"] >= 5),

        "EXTREME":

            data["_TOTAL_GOALS"] >= 6,

    }

    for profile_name, mask in profiles_to_compare.items():

        positive = data[
            mask
        ]

        negative = data[
            ~mask
        ]

        if len(positive) == 0:

            continue

        print()
        print("=" * 70)

        print(
            f"VARIABLES CS - "
            f"{profile_name} VS RESTO"
        )

        print("=" * 70)

        print(

            f"{'VARIABLE':35}"

            f"{'PROFILE':>12}"

            f"{'REST':>12}"

            f"{'DIFF':>12}"

        )

        differences = []

        for column in cs_columns:

            profile_mean = (
                positive[column].mean()
            )

            rest_mean = (
                negative[column].mean()
            )

            diff = (

                profile_mean

                -

                rest_mean

            )

            differences.append(

                (

                    column,
                    profile_mean,
                    rest_mean,
                    diff,

                )

            )

        # Ordenamos por diferencia absoluta
        # para ver primero las señales más fuertes.

        differences.sort(

            key=lambda x: abs(x[3]),

            reverse=True

        )

        for (

            column,
            profile_mean,
            rest_mean,
            diff,

        ) in differences:

            print(

                f"{column:35}"

                f"{profile_mean:>12.4f}"

                f"{rest_mean:>12.4f}"

                f"{diff:>+12.4f}"

            )

    # ======================================================
    # TOP VARIABLES DE CADA PERFIL
    # ======================================================

    print()
    print("=" * 70)
    print("TOP SEÑALES POR PERFIL")
    print("=" * 70)

    for profile_name, mask in profiles_to_compare.items():

        positive = data[
            mask
        ]

        negative = data[
            ~mask
        ]

        if len(positive) == 0:

            continue

        differences = []

        for column in cs_columns:

            profile_mean = (
                positive[column].mean()
            )

            rest_mean = (
                negative[column].mean()
            )

            diff = (

                profile_mean

                -

                rest_mean

            )

            differences.append(

                (

                    column,
                    diff,

                )

            )

        differences.sort(

            key=lambda x: abs(x[1]),

            reverse=True

        )

        print()
        print(profile_name)
        print("-" * 50)

        for column, diff in differences[:10]:

            print(

                f"{column:35}"

                f"{diff:>+10.4f}"

            )

    # ======================================================
    # LISTADO DE PARTIDOS EXTREMOS
    # ======================================================

    print()
    print("=" * 70)
    print("PARTIDOS EXTREME - TOTAL GOLES >= 6")
    print("=" * 70)

    extreme = data[

        data["_TOTAL_GOALS"] >= 6

    ].copy()

    extreme = extreme.sort_values(

        by="_TOTAL_GOALS",

        ascending=False

    )

    columns_to_show = [

        column

        for column in [

            "FECHA",
            "LOCAL",
            "VISITANTE",
            "ODDS_REAL_SCORE",
            "CUOTA",
            "TOP1",
            "P_TOP1",
            "ODDS_TOP1_HIT",
            "ODDS_TOP3_HIT",
            "ODDS_TOP5_HIT",

        ]

        if column in extreme.columns

    ]

    if len(extreme) > 0:

        print()

        print(

            extreme[
                columns_to_show
            ].to_string(

                index=False

            )

        )

    else:

        print()
        print(
            "No existen partidos con 6 o más goles."
        )