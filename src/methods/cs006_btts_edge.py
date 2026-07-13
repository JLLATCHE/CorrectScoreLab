"""
CS006 - BTTS Edge
"""


def apply(df):

    df = df.copy()

    df["CS006_BTTS_EDGE"] = (

        df["HOME_BTTS_HOME"]

        +

        df["AWAY_BTTS_AWAY"]

    ) / 2

    return df