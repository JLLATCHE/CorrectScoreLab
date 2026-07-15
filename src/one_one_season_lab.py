"""
1-1 Season Lab

Analiza los partidos de la temporada de control
en los que CorrectScoreLab predice 1-1 como TOP1.

Objetivos:

1. Ver qué marcadores reales aparecen cuando falla el 1-1.
2. Comparar las variables CS entre:
   - 1-1 acertados
   - falsos 1-1
"""


def analyze_one_one_season(df):

    print()
    print("=" * 60)
    print("1-1 SEASON LAB")
    print("=" * 60)

    data = df.copy()

    # ==========================================================
    # FILTRAR PREDICCIONES 1-1
    # ==========================================================

    one_one = data[
        data["TOP1"] == "1-1"
    ].copy()

    if len(one_one) == 0:

        print()
        print("No existen predicciones TOP1 = 1-1")

        return

    good = one_one[
        one_one["ODDS_TOP1_HIT"]
    ].copy()

    bad = one_one[
        ~one_one["ODDS_TOP1_HIT"]
    ].copy()

    # ==========================================================
    # RESUMEN
    # ==========================================================

    print()
    print("RESUMEN")
    print("-" * 60)

    print(
        f"Predicciones 1-1 : "
        f"{len(one_one):,}"
    )

    print(
        f"1-1 correctos    : "
        f"{len(good):,}"
    )

    print(
        f"1-1 incorrectos  : "
        f"{len(bad):,}"
    )

    hit_rate = (

        len(good) / len(one_one)

        if len(one_one) > 0

        else 0

    )

    print(
        f"Acierto 1-1      : "
        f"{hit_rate:.2%}"
    )

    # ==========================================================
    # DESTINO DE LOS FALSOS 1-1
    # ==========================================================

    print()
    print("MARCADORES REALES CUANDO FALLA EL 1-1")
    print("-" * 60)

    real_scores = (

        bad["ODDS_REAL_SCORE"]
        .value_counts()
    )

    for score, count in real_scores.items():

        percentage = (

            count / len(bad)

            if len(bad) > 0

            else 0

        )

        print(

            f"{str(score):6}"

            f"{count:4} partidos   "

            f"{percentage:6.2%}"

        )

    # ==========================================================
    # P_TOP1
    # ==========================================================

    print()
    print("P_TOP1 - 1-1")
    print("-" * 60)

    good_p = (
        good["P_TOP1"].mean()
        if len(good) > 0
        else 0
    )

    bad_p = (
        bad["P_TOP1"].mean()
        if len(bad) > 0
        else 0
    )

    print(
        f"Media correctos   : "
        f"{good_p:.4f}"
    )

    print(
        f"Media incorrectos : "
        f"{bad_p:.4f}"
    )

    print(
        f"Diferencia        : "
        f"{good_p - bad_p:+.4f}"
    )

    # ==========================================================
    # VARIABLES CS
    # ==========================================================

    print()
    print("VARIABLES CS - 1-1 CORRECTO VS FALSO")
    print("-" * 75)

    print(
        f"{'VARIABLE':35}"
        f"{'GOOD':>12}"
        f"{'BAD':>12}"
        f"{'DIFF':>12}"
    )

    cs_columns = sorted([

        column

        for column in data.columns

        if column.startswith("CS")

    ])

    for column in cs_columns:

        good_mean = (

            good[column].mean()

            if len(good) > 0

            else 0

        )

        bad_mean = (

            bad[column].mean()

            if len(bad) > 0

            else 0

        )

        diff = (
            good_mean
            -
            bad_mean
        )

        print(

            f"{column:35}"

            f"{good_mean:>12.4f}"

            f"{bad_mean:>12.4f}"

            f"{diff:>+12.4f}"

        )

    # ==========================================================
    # TOP3 CUANDO TOP1 = 1-1
    # ==========================================================

    print()
    print("RECUPERACIÓN TOP3 DE FALSOS 1-1")
    print("-" * 60)

    recovered_top3 = (

        bad["ODDS_TOP3_HIT"].sum()

        if "ODDS_TOP3_HIT" in bad.columns

        else 0

    )

    recovery_rate = (

        recovered_top3 / len(bad)

        if len(bad) > 0

        else 0

    )

    print(
        f"Falsos 1-1       : "
        f"{len(bad):,}"
    )

    print(
        f"Real estaba TOP3 : "
        f"{recovered_top3:,}"
    )

    print(
        f"Recuperación     : "
        f"{recovery_rate:.2%}"
    )