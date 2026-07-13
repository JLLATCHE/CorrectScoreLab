"""
CS001 - Attack Edge
"""


def apply(df):

    df = df.copy()

    df["CS001_ATTACK_EDGE"] = (

        (df["HOME_GF_HOME"] - df["AWAY_GA_AWAY"])

        -

        (df["AWAY_GF_AWAY"] - df["HOME_GA_HOME"])

    )

    return df