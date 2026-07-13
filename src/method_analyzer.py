def analyze(df):

    methods = [

        "CS001_ATTACK_EDGE",
        "CS002_DOMINANCE",
        "CS003_FORM_EDGE",
        "CS004_SHOTS_EDGE",
        "CS005_OVER_EDGE",
        "CS006_BTTS_EDGE",

    ]

    print()
    print("=" * 60)
    print("METHOD ANALYZER")
    print("=" * 60)

    hit = df[df["TOP1_HIT"]]
    fail = df[~df["TOP1_HIT"]]

    for column in methods:

        if column not in df.columns:

            continue

        hit_mean = hit[column].mean()
        fail_mean = fail[column].mean()

        diff = hit_mean - fail_mean

        print(
            f"{column:25}"
            f"{diff:+.4f}"
        )