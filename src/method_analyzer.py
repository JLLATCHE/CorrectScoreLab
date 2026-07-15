def analyze(df):

    methods = [

        column

        for column in df.columns

        if column.startswith("CS")

    ]

    methods.sort()

    print()
    print("=" * 60)
    print("METHOD ANALYZER")
    print("=" * 60)

    hit = df[df["TOP1_HIT"]]
    fail = df[~df["TOP1_HIT"]]

    for column in methods:

        hit_mean = hit[column].mean()
        fail_mean = fail[column].mean()

        diff = hit_mean - fail_mean

        print(
            f"{column:35}"
            f"{diff:+.4f}"
        )