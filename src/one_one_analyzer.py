def analyze_one_one(df):

    print()
    print("=" * 60)
    print("1-1 LAB")
    print("=" * 60)

    pred = df[df["TOP1"] == "1-1"]

    good = pred[pred["REAL_SCORE"] == "1-1"]
    bad = pred[pred["REAL_SCORE"] != "1-1"]

    variables = [

        "HOME_GF_HOME",
        "HOME_GA_HOME",
        "HOME_HST_HOME",
        "HOME_FORM_HOME",
        "HOME_OVER25_HOME",
        "HOME_BTTS_HOME",

        "AWAY_GF_AWAY",
        "AWAY_GA_AWAY",
        "AWAY_AST_AWAY",
        "AWAY_FORM_AWAY",
        "AWAY_OVER25_AWAY",
        "AWAY_BTTS_AWAY",

    ]

    print()
    print(f"{'VARIABLE':25}{'GOOD':>10}{'BAD':>10}{'DIFF':>10}")
    print("-" * 60)

    for var in variables:

        good_mean = good[var].mean()
        bad_mean = bad[var].mean()

        diff = good_mean - bad_mean

        print(
            f"{var:25}"
            f"{good_mean:10.3f}"
            f"{bad_mean:10.3f}"
            f"{diff:10.3f}"
        )