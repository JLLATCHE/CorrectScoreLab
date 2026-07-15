"""
Odds Backtest

Evalúa el rendimiento BASE de CorrectScoreLab
sobre los partidos que disponen de cuota.
"""


def evaluate_odds(matched_df):

    print()
    print("=" * 60)
    print("ODDS BACKTEST - BASE")
    print("=" * 60)

    df = matched_df.copy()

    # ==========================================================
    # SOLO PARTIDOS CORRECTAMENTE CRUZADOS
    # ==========================================================

    if "_merge" in df.columns:

        df = df[
            df["_merge"] == "both"
        ].copy()

    # ==========================================================
    # VALIDACIÓN
    # ==========================================================

    required_columns = [

        "MARCADOR",
        "CUOTA",
        "TOP1",
        "TOP2",
        "TOP3",
        "TOP5",
        "P_TOP1",

    ]

    missing_columns = [

        column

        for column in required_columns

        if column not in df.columns

    ]

    if missing_columns:

        raise ValueError(
            f"Faltan columnas para OddsBacktest: {missing_columns}"
        )

    # ==========================================================
    # NORMALIZAR MARCADOR REAL
    # ==========================================================

    df["ODDS_REAL_SCORE"] = (

        df["MARCADOR"]
        .astype(str)
        .str.strip()

    )

    # ==========================================================
    # HITS
    # ==========================================================

    df["ODDS_TOP1_HIT"] = (

        df["TOP1"]
        == df["ODDS_REAL_SCORE"]

    )

    df["ODDS_TOP3_HIT"] = df.apply(

        lambda row:

        row["ODDS_REAL_SCORE"]

        in [

            row["TOP1"],
            row["TOP2"],
            row["TOP3"],

        ],

        axis=1

    )

    df["ODDS_TOP5_HIT"] = df.apply(

        lambda row:

        row["ODDS_REAL_SCORE"]

        in row["TOP5"],

        axis=1

    )

    # ==========================================================
    # MÉTRICAS PREDICTIVAS
    # ==========================================================

    matches = len(df)

    top1_hits = df["ODDS_TOP1_HIT"].sum()
    top3_hits = df["ODDS_TOP3_HIT"].sum()
    top5_hits = df["ODDS_TOP5_HIT"].sum()

    top1 = (
        top1_hits / matches
        if matches > 0
        else 0
    )

    top3 = (
        top3_hits / matches
        if matches > 0
        else 0
    )

    top5 = (
        top5_hits / matches
        if matches > 0
        else 0
    )

    # ==========================================================
    # INFORMACIÓN DE CUOTAS DE LOS ACIERTOS TOP1
    #
    # IMPORTANTE:
    # La cuota disponible corresponde al marcador REAL.
    # Por tanto solo coincide con la apuesta TOP1 cuando
    # TOP1 acierta.
    #
    # Esto NO es todavía un ROI completo del sistema.
    # ==========================================================

    winning_bets = df[
        df["ODDS_TOP1_HIT"]
    ].copy()

    winning_odds_sum = (
        winning_bets["CUOTA"].sum()
    )

    average_winning_odds = (

        winning_bets["CUOTA"].mean()

        if len(winning_bets) > 0

        else 0

    )

    # ==========================================================
    # RESULTADOS
    # ==========================================================

    print(f"Partidos          : {matches:,}")

    print()

    print(
        f"TOP1              : "
        f"{top1_hits}/{matches} "
        f"({top1:.2%})"
    )

    print(
        f"TOP3              : "
        f"{top3_hits}/{matches} "
        f"({top3:.2%})"
    )

    print(
        f"TOP5              : "
        f"{top5_hits}/{matches} "
        f"({top5:.2%})"
    )

    print()
    print("CUOTAS TOP1 ACERTADOS")
    print("-" * 60)

    print(
        f"Aciertos TOP1     : "
        f"{len(winning_bets):,}"
    )

    print(
        f"Cuota media       : "
        f"{average_winning_odds:.2f}"
    )

    print(
        f"Suma cuotas       : "
        f"{winning_odds_sum:.2f}"
    )

    return df