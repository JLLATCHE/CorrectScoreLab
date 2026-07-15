"""
Odds Filter Analyzer

Analiza el rendimiento del modelo según
probabilidad TOP1 y marcador predicho.

IMPORTANTE:
Los resultados económicos son teóricos
mientras CUOTA represente únicamente
la cuota del marcador real.
"""


def analyze_odds_filters(df):

    print()
    print("=" * 60)
    print("ODDS FILTER ANALYZER")
    print("=" * 60)

    df = df.copy()

    # ==========================================================
    # VALIDACIÓN
    # ==========================================================

    required_columns = [

        "TOP1",
        "P_TOP1",
        "ODDS_TOP1_HIT",
        "CUOTA",

    ]

    missing = [

        column

        for column in required_columns

        if column not in df.columns

    ]

    if missing:

        raise ValueError(
            f"Faltan columnas para OddsFilterAnalyzer: {missing}"
        )

    # ==========================================================
    # FUNCIÓN DE MÉTRICAS
    # ==========================================================

    def calculate_metrics(data):

        bets = len(data)

        if bets == 0:

            return None

        hits_df = data[
            data["ODDS_TOP1_HIT"]
        ]

        hits = len(hits_df)

        hit_rate = hits / bets

        average_odds = (

            hits_df["CUOTA"].mean()

            if hits > 0

            else 0.0

        )

        returns = hits_df["CUOTA"].sum()

        profit = returns - bets

        roi = profit / bets

        return {

            "bets": bets,
            "hits": hits,
            "hit_rate": hit_rate,
            "average_odds": average_odds,
            "returns": returns,
            "profit": profit,
            "roi": roi,

        }

    # ==========================================================
    # FILTRO POR P_TOP1
    # ==========================================================

    print()
    print("RENDIMIENTO POR P_TOP1")
    print("-" * 95)

    print(
        f"{'MIN P':<8}"
        f"{'BETS':>7}"
        f"{'HITS':>7}"
        f"{'HIT RATE':>12}"
        f"{'AVG ODDS':>12}"
        f"{'RETURN':>12}"
        f"{'PROFIT':>12}"
        f"{'ROI':>10}"
    )

    thresholds = [

        0.10,
        0.12,
        0.14,
        0.16,
        0.18,
        0.20,
        0.22,
        0.25,
        0.30,

    ]

    for threshold in thresholds:

        filtered = df[
            df["P_TOP1"] >= threshold
        ]

        metrics = calculate_metrics(
            filtered
        )

        if metrics is None:

            continue

        print(

            f"{threshold:<8.2f}"

            f"{metrics['bets']:>7}"

            f"{metrics['hits']:>7}"

            f"{metrics['hit_rate']:>11.2%}"

            f"{metrics['average_odds']:>12.2f}"

            f"{metrics['returns']:>12.2f}"

            f"{metrics['profit']:>12.2f}"

            f"{metrics['roi']:>9.2%}"

        )

    # ==========================================================
    # RENDIMIENTO POR MARCADOR TOP1
    # ==========================================================

    print()
    print("RENDIMIENTO POR MARCADOR TOP1")
    print("-" * 95)

    print(
        f"{'SCORE':<8}"
        f"{'BETS':>7}"
        f"{'HITS':>7}"
        f"{'HIT RATE':>12}"
        f"{'AVG ODDS':>12}"
        f"{'RETURN':>12}"
        f"{'PROFIT':>12}"
        f"{'ROI':>10}"
    )

    scores = (

        df["TOP1"]
        .value_counts()
        .index
        .tolist()

    )

    for score in scores:

        filtered = df[
            df["TOP1"] == score
        ]

        metrics = calculate_metrics(
            filtered
        )

        if metrics is None:

            continue

        print(

            f"{str(score):<8}"

            f"{metrics['bets']:>7}"

            f"{metrics['hits']:>7}"

            f"{metrics['hit_rate']:>11.2%}"

            f"{metrics['average_odds']:>12.2f}"

            f"{metrics['returns']:>12.2f}"

            f"{metrics['profit']:>12.2f}"

            f"{metrics['roi']:>9.2%}"

        )

    # ==========================================================
    # MARCADOR + P_TOP1
    # ==========================================================

    print()
    print("RENDIMIENTO MARCADOR + P_TOP1")
    print("-" * 95)

    key_scores = [

        "1-0",
        "1-1",
        "0-0",
        "0-1",
        "2-0",
        "2-1",

    ]

    key_thresholds = [

        0.15,
        0.18,
        0.20,
        0.22,
        0.25,

    ]

    for score in key_scores:

        print()
        print(f"TOP1 = {score}")

        for threshold in key_thresholds:

            filtered = df[

                (df["TOP1"] == score)

                &

                (df["P_TOP1"] >= threshold)

            ]

            metrics = calculate_metrics(
                filtered
            )

            if metrics is None:

                continue

            print(

                f"P >= {threshold:.2f}   "

                f"Bets {metrics['bets']:3}   "

                f"Hits {metrics['hits']:3}   "

                f"Hit {metrics['hit_rate']:6.2%}   "

                f"Profit {metrics['profit']:8.2f}   "

                f"ROI {metrics['roi']:7.2%}"

            )

    print()
    print(
        "* Resultados económicos teóricos. "
        "No equivalen todavía a un backtest completo."
    )