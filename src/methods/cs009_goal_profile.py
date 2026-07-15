"""
CS009 - Goal Profile

Distribución histórica de goles totales
en los últimos FORM_MATCHES partidos.
"""

from collections import deque

from config import FORM_MATCHES


def apply(df):

    df = df.copy()

    columns = [

        "CS009_HOME_TG0_RATE",
        "CS009_HOME_TG1_RATE",
        "CS009_HOME_TG2_RATE",
        "CS009_HOME_TG3_RATE",
        "CS009_HOME_TG4PLUS_RATE",

        "CS009_AWAY_TG0_RATE",
        "CS009_AWAY_TG1_RATE",
        "CS009_AWAY_TG2_RATE",
        "CS009_AWAY_TG3_RATE",
        "CS009_AWAY_TG4PLUS_RATE",

    ]

    for col in columns:

        df[col] = 0.0

    history = {}

    for idx, row in df.iterrows():

        home = row["HomeTeam"]
        away = row["AwayTeam"]

        if home not in history:

            history[home] = deque(maxlen=FORM_MATCHES)

        if away not in history:

            history[away] = deque(maxlen=FORM_MATCHES)

        # ==========================
        # HOME
        # ==========================

        if len(history[home]) > 0:

            matches = len(history[home])

            df.at[idx, "CS009_HOME_TG0_RATE"] = sum(g == 0 for g in history[home]) / matches
            df.at[idx, "CS009_HOME_TG1_RATE"] = sum(g == 1 for g in history[home]) / matches
            df.at[idx, "CS009_HOME_TG2_RATE"] = sum(g == 2 for g in history[home]) / matches
            df.at[idx, "CS009_HOME_TG3_RATE"] = sum(g == 3 for g in history[home]) / matches
            df.at[idx, "CS009_HOME_TG4PLUS_RATE"] = sum(g >= 4 for g in history[home]) / matches

        # ==========================
        # AWAY
        # ==========================

        if len(history[away]) > 0:

            matches = len(history[away])

            df.at[idx, "CS009_AWAY_TG0_RATE"] = sum(g == 0 for g in history[away]) / matches
            df.at[idx, "CS009_AWAY_TG1_RATE"] = sum(g == 1 for g in history[away]) / matches
            df.at[idx, "CS009_AWAY_TG2_RATE"] = sum(g == 2 for g in history[away]) / matches
            df.at[idx, "CS009_AWAY_TG3_RATE"] = sum(g == 3 for g in history[away]) / matches
            df.at[idx, "CS009_AWAY_TG4PLUS_RATE"] = sum(g >= 4 for g in history[away]) / matches

        # ==========================
        # UPDATE
        # ==========================

        total_goals = row["FTHG"] + row["FTAG"]

        history[home].append(total_goals)
        history[away].append(total_goals)

    return df