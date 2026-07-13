"""
CS004 - Shots Edge
"""


def apply(df):

    df = df.copy()

    df["CS004_SHOTS_EDGE"] = (

        df["HOME_HST_HOME"]

        -

        df["AWAY_AST_AWAY"]

    )

    return df