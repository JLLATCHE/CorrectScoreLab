"""
CS002 - Favourite Dominance
"""


def apply(df):

    df = df.copy()

    attack = (

        df["HOME_GF_HOME"]

        +

        df["HOME_HST_HOME"] * 0.20

    )

    defense = (

        df["AWAY_GA_AWAY"]

        +

        df["AWAY_AST_AWAY"] * 0.20

    )

    df["CS002_DOMINANCE"] = attack - defense

    return df