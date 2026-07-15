"""
1-0 Season Lab

Analiza los partidos de la temporada de control
en los que CorrectScoreLab predice 1-0 como TOP1.

Objetivos:

1. Comparar los 1-0 acertados con los falsos 1-0.
2. Analizar P_TOP1.
3. Detectar variables CS que diferencien ambos grupos.
4. Ver qué marcadores reales aparecen cuando falla el 1-0.
5. Medir la rentabilidad del 1-0 por niveles de confianza.
"""


def analyze_one_zero_season(df):

    print()
    print("=" * 60)
    print("1-0 SEASON LAB")
    print("=" * 60)

    data = df.copy()

    # ==========================================================
    # FILTRAR TOP1 = 1-0
    # ==========================================================

    one_zero = data[
        data["TOP1"] == "1-0"
    ].copy()

    if len(one_zero) == 0:

        print()
        print("No existen predicciones TOP1 = 1-0")

        return

    good = one_zero[
        one_zero["ODDS_TOP1_HIT"]
    ].copy()

    bad = one_zero[
        ~one_zero["ODDS_TOP1_HIT"]
    ].copy()

    # ==========================================================
    # RESUMEN
    # ==========================================================

    print()
    print("RESUMEN")
    print("-" * 60)

    print(
        f"Predicciones 1-0 : "
        f"{len(one_zero):,}"
    )

    print(
        f"1-0 correctos    : "
        f"{len(good):,}"
    )

    print(
        f"1-0 incorrectos  : "
        f"{len(bad):,}"
    )

    hit_rate = (
        len(good) / len(one_zero)
        if len(one_zero) > 0
        else 0
    )

    print(
        f"Acierto 1-0      : "
        f"{hit_rate:.2%}"
    )

    # ==========================================================
    # RENTABILIDAD BASE 1-0
    # ==========================================================

    returns = good["CUOTA"].sum()

    profit = (
        returns
        -
        len(one_zero)
    )

    roi = (
        profit / len(one_zero)
        if len(one_zero) > 0
        else 0
    )

    print()
    print("RENTABILIDAD 1-0")
    print("-" * 60)

    print(
        f"Stake total      : "
        f"{len(one_zero):.2f}"
    )

    print(
        f"Retorno          : "
        f"{returns:.2f}"
    )

    print(
        f"Beneficio        : "
        f"{profit:+.2f}"
    )

    print(
        f"ROI              : "
        f"{roi:+.2%}"
    )

    # ==========================================================
    # DESTINO DE LOS FALSOS 1-0
    # ==========================================================

    print()
    print("MARCADORES REALES CUANDO FALLA EL 1-0")
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
    print("P_TOP1 - 1-0")
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
    print("VARIABLES CS - 1-0 CORRECTO VS FALSO")
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
    # RENTABILIDAD POR P_TOP1
    # ==========================================================

    print()
    print("1-0 POR P_TOP1")
    print("-" * 75)

    thresholds = [

        0.10,
        0.12,
        0.14,
        0.15,
        0.16,
        0.18,
        0.20,
        0.22,
        0.25,

    ]

    for threshold in thresholds:

        filtered = one_zero[
            one_zero["P_TOP1"] >= threshold
        ]

        bets = len(filtered)

        if bets == 0:

            continue

        filtered_hits = filtered[
            filtered["ODDS_TOP1_HIT"]
        ]

        hits = len(filtered_hits)

        hit_rate = (
            hits / bets
        )

        returns = (
            filtered_hits["CUOTA"].sum()
        )

        profit = (
            returns
            -
            bets
        )

        roi = (
            profit / bets
        )

        print(
            f"P >= {threshold:.2f}   "
            f"Bets {bets:3}   "
            f"Hits {hits:3}   "
            f"Hit {hit_rate:6.2%}   "
            f"Return {returns:7.2f}   "
            f"Profit {profit:+7.2f}   "
            f"ROI {roi:+7.2%}"
        )