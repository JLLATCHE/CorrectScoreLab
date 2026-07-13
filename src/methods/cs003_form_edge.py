"""
CS003 - Form Edge
"""


def apply(df):

    df = df.copy()

    df["CS003_FORM_EDGE"] = (

        df["HOME_FORM_HOME"]

        -

        df["AWAY_FORM_AWAY"]

    )

    return df