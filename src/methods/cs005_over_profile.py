"""
CS005 - Over Profile
"""


def apply(df):

    df = df.copy()

    df["CS005_OVER_EDGE"] = (

        df["HOME_OVER25_HOME"]

        +

        df["AWAY_OVER25_AWAY"]

    ) / 2

    return df