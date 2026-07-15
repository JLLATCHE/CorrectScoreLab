from collections import Counter


def analyze_confusions(df):

    print()
    print("=" * 60)
    print("CONFUSION ANALYZER")
    print("=" * 60)

    errors = df[df["TOP1_HIT"] == False]

    counter = Counter()

    for _, row in errors.iterrows():

        real = row["REAL_SCORE"]
        pred = row["TOP1"]

        counter[(real, pred)] += 1

    print()
    print(f"{'REAL':<8}{'PRED':<8}{'VECES'}")
    print("-" * 35)

    for (real, pred), n in counter.most_common(30):

        print(
            f"{real:<8}"
            f"{pred:<8}"
            f"{n}"
        )