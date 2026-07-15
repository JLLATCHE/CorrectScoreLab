"""
Odds Analyzer

Analiza el comportamiento de CorrectScoreLab
sobre la temporada con datos de cuotas.
"""


def analyze_odds(df):

    print()
    print("=" * 60)
    print("ODDS ANALYZER")
    print("=" * 60)

    df = df.copy()

    # ==========================================================
    # VALIDACIÓN
    # ==========================================================

    required_columns = [

        "ODDS_REAL_SCORE",
        "ODDS_TOP1_HIT",
        "TOP1",
        "P_TOP1",
        "CUOTA",

    ]

    missing = [

        column

        for column in required_columns

        if column not in df.columns

    ]

    if missing:

        raise ValueError(
            f"Faltan columnas para OddsAnalyzer: {missing}"
        )

    hits = df[
        df["ODDS_TOP1_HIT"]
    ].copy()

    fails = df[
        ~df["ODDS_TOP1_HIT"]
    ].copy()

    # ==========================================================
    # RESUMEN
    # ==========================================================

    print()
    print("RESUMEN")
    print("-" * 60)

    print(f"Partidos          : {len(df):,}")
    print(f"Aciertos TOP1     : {len(hits):,}")
    print(f"Fallos TOP1       : {len(fails):,}")

    # ==========================================================
    # TOP1 PREDICHOS
    # ==========================================================

    print()
    print("TOP1 PREDICHOS")
    print("-" * 60)

    predictions = (

        df
        .groupby("TOP1")
        .agg(

            PREDICCIONES=(
                "TOP1",
                "size"
            ),

            ACIERTOS=(
                "ODDS_TOP1_HIT",
                "sum"
            ),

        )
        .reset_index()

    )

    predictions["HIT_RATE"] = (

        predictions["ACIERTOS"]

        /

        predictions["PREDICCIONES"]

    )

    predictions = predictions.sort_values(

        by="PREDICCIONES",

        ascending=False

    )

    for _, row in predictions.iterrows():

        print(

            f"{row['TOP1']:6}"

            f"{int(row['PREDICCIONES']):5} pred   "

            f"{int(row['ACIERTOS']):4} hit   "

            f"{row['HIT_RATE']:.2%}"

        )

    # ==========================================================
    # MARCADORES ACERTADOS
    # ==========================================================

    print()
    print("MARCADORES ACERTADOS TOP1")
    print("-" * 60)

    winning_scores = (

        hits
        .groupby("ODDS_REAL_SCORE")
        .agg(

            ACIERTOS=(
                "ODDS_REAL_SCORE",
                "size"
            ),

            CUOTA_MEDIA=(
                "CUOTA",
                "mean"
            ),

            SUMA_CUOTAS=(
                "CUOTA",
                "sum"
            ),

        )
        .reset_index()

        .sort_values(

            by="ACIERTOS",

            ascending=False

        )

    )

    for _, row in winning_scores.iterrows():

        print(

            f"{row['ODDS_REAL_SCORE']:6}"

            f"{int(row['ACIERTOS']):4} hits   "

            f"cuota media {row['CUOTA_MEDIA']:7.2f}   "

            f"suma {row['SUMA_CUOTAS']:8.2f}"

        )

    # ==========================================================
    # PROBABILIDAD TOP1
    # ==========================================================

    print()
    print("P_TOP1")
    print("-" * 60)

    print(

        f"Media aciertos    : "
        f"{hits['P_TOP1'].mean():.4f}"

    )

    print(

        f"Media fallos      : "
        f"{fails['P_TOP1'].mean():.4f}"

    )

    print(

        f"Diferencia        : "
        f"{hits['P_TOP1'].mean() - fails['P_TOP1'].mean():+.4f}"

    )

    # ==========================================================
    # VARIABLES CS
    # ==========================================================

    print()
    print("VARIABLES CS - TEMPORADA ODDS")
    print("-" * 60)

    cs_columns = [

        column

        for column in df.columns

        if column.startswith("CS")

    ]

    cs_columns.sort()

    for column in cs_columns:

        hit_mean = hits[column].mean()

        fail_mean = fails[column].mean()

        diff = (

            hit_mean

            -

            fail_mean

        )

        print(

            f"{column:35}"

            f"{diff:+.4f}"

        )

    return df