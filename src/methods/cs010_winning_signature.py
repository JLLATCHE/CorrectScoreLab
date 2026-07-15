"""
CS010 - Winning Signature

Distribución histórica de las victorias
por marcador.
"""

from collections import deque

from config import FORM_MATCHES


def apply(df):

    df = df.copy()

    columns = [

        "CS010_HOME_WIN10_RATE",
        "CS010_HOME_WIN20_RATE",
        "CS010_HOME_WIN21_RATE",
        "CS010_HOME_WINOTHER_RATE",

        "CS010_AWAY_WIN10_RATE",
        "CS010_AWAY_WIN20_RATE",
        "CS010_AWAY_WIN21_RATE",
        "CS010_AWAY_WINOTHER_RATE",

    ]

    for col in columns:

        df[col] = 0.0

    history = {}

    for idx, row in df.iterrows():

        home = row["HomeTeam"]
        away = row["AwayTeam"]

        if home not in history:

            history[home] = {

                "wins": deque(maxlen=FORM_MATCHES)

            }

        if away not in history:

            history[away] = {

                "wins": deque(maxlen=FORM_MATCHES)

            }

        # ==========================
        # HOME
        # ==========================

        if len(history[home]["wins"]) > 0:

            matches = len(history[home]["wins"])

            df.at[idx, "CS010_HOME_WIN10_RATE"] = sum(x == "10" for x in history[home]["wins"]) / matches
            df.at[idx, "CS010_HOME_WIN20_RATE"] = sum(x == "20" for x in history[home]["wins"]) / matches
            df.at[idx, "CS010_HOME_WIN21_RATE"] = sum(x == "21" for x in history[home]["wins"]) / matches
            df.at[idx, "CS010_HOME_WINOTHER_RATE"] = sum(x == "OT" for x in history[home]["wins"]) / matches

        # ==========================
        # AWAY
        # ==========================

        if len(history[away]["wins"]) > 0:

            matches = len(history[away]["wins"])

            df.at[idx, "CS010_AWAY_WIN10_RATE"] = sum(x == "10" for x in history[away]["wins"]) / matches
            df.at[idx, "CS010_AWAY_WIN20_RATE"] = sum(x == "20" for x in history[away]["wins"]) / matches
            df.at[idx, "CS010_AWAY_WIN21_RATE"] = sum(x == "21" for x in history[away]["wins"]) / matches
            df.at[idx, "CS010_AWAY_WINOTHER_RATE"] = sum(x == "OT" for x in history[away]["wins"]) / matches

        # ==========================
        # UPDATE
        # ==========================

        hg = row["FTHG"]
        ag = row["FTAG"]

        if hg > ag:

            if hg == 1 and ag == 0:

                history[home]["wins"].append("10")

            elif hg == 2 and ag == 0:

                history[home]["wins"].append("20")

            elif hg == 2 and ag == 1:

                history[home]["wins"].append("21")

            else:

                history[home]["wins"].append("OT")

        if ag > hg:

            if ag == 1 and hg == 0:

                history[away]["wins"].append("10")

            elif ag == 2 and hg == 0:

                history[away]["wins"].append("20")

            elif ag == 2 and hg == 1:

                history[away]["wins"].append("21")

            else:

                history[away]["wins"].append("OT")

    return df