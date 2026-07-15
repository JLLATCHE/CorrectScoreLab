from collections import Counter


def analyze_scores(df):

    print()
    print("=" * 60)
    print("SCORE ANALYZER")
    print("=" * 60)

    # Marcadores reales

    real_counter = Counter(df["REAL_SCORE"])

    # Marcadores acertados

    hit_counter = Counter(
        df[df["TOP1_HIT"]]["REAL_SCORE"]
    )

    print()
    print("TOP 15 MARCADORES REALES")
    print("-" * 60)

    for score, total in real_counter.most_common(15):

        hits = hit_counter.get(score, 0)

        pct = hits / total * 100

        print(
            f"{score:5}"
            f"{hits:4}/{total:<4}"
            f"{pct:7.2f}%"
        )