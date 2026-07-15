"""
CS008 - Goal Volatility

Volatilidad reciente de goles anotados
y recibidos por ambos equipos.
"""

from collections import deque
import numpy as np

from config import FORM_MATCHES


def apply(df):

    df = df.copy()

    columns = [

        "CS008_HOME_GF_STD",
        "CS008_HOME_GA_STD",

        "CS008_AWAY_GF_STD",
        "CS008_AWAY_GA_STD",

    ]

    for col in columns:

        df[col] = 0.0

    history = {}

    for idx, row in df.iterrows():

        home = row["HomeTeam"]
        away = row["AwayTeam"]

        if home not in history:

            history[home] = {

                "gf": deque(maxlen=FORM_MATCHES),
                "ga": deque(maxlen=FORM_MATCHES),

            }

        if away not in history:

            history[away] = {

                "gf": deque(maxlen=FORM_MATCHES),
                "ga": deque(maxlen=FORM_MATCHES),

            }

        # ==========================
        # FEATURES
        # ==========================

        if len(history[home]["gf"]) > 1:

            df.at[idx, "CS008_HOME_GF_STD"] = np.std(history[home]["gf"])

        if len(history[home]["ga"]) > 1:

            df.at[idx, "CS008_HOME_GA_STD"] = np.std(history[home]["ga"])

        if len(history[away]["gf"]) > 1:

            df.at[idx, "CS008_AWAY_GF_STD"] = np.std(history[away]["gf"])

        if len(history[away]["ga"]) > 1:

            df.at[idx, "CS008_AWAY_GA_STD"] = np.std(history[away]["ga"])

        # ==========================
        # UPDATE
        # ==========================

        history[home]["gf"].append(row["FTHG"])
        history[home]["ga"].append(row["FTAG"])

        history[away]["gf"].append(row["FTAG"])
        history[away]["ga"].append(row["FTHG"])

    return df