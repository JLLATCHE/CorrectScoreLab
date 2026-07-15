"""
CS007 - Attack Defense Compatibility

Compatibilidad entre el ataque de un equipo
y la defensa del rival.
"""


def apply(df):

    df = df.copy()

    df["CS007_HOME_ATTACK_EDGE"] = (

        df["HOME_GF_HOME"]

        * df["AWAY_GA_AWAY"]

    )

    df["CS007_AWAY_ATTACK_EDGE"] = (

        df["AWAY_GF_AWAY"]

        * df["HOME_GA_HOME"]

    )

    return df