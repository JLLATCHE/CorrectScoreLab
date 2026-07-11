import pandas as pd

from config import FORM_MATCHES


def _avg(values):

    if not values:
        return 0.0

    return sum(values) / len(values)


def _form(points):

    if not points:
        return 0.0

    return sum(points) / (len(points) * 3)


def build_goal_features(df):

    df = df.copy()

    history = {}

    rows = []

    seasons = sorted(df["SEASON"].unique())

    for season in seasons:

        season_df = df[df["SEASON"] == season]

        history.clear()

        for _, row in season_df.iterrows():

            home = row["HomeTeam"]
            away = row["AwayTeam"]

            if home not in history:
                history[home] = {
                    "gf_home": [],
                    "ga_home": [],
                    "hst_home": [],
                    "pts_home": [],
                    "gf_away": [],
                    "ga_away": [],
                    "ast_away": [],
                    "pts_away": []
                }

            if away not in history:
                history[away] = {
                    "gf_home": [],
                    "ga_home": [],
                    "hst_home": [],
                    "pts_home": [],
                    "gf_away": [],
                    "ga_away": [],
                    "ast_away": [],
                    "pts_away": []
                }

            h = history[home]
            a = history[away]

            rows.append({

                "HOME_GF_HOME": _avg(h["gf_home"][-FORM_MATCHES:]),
                "HOME_GA_HOME": _avg(h["ga_home"][-FORM_MATCHES:]),
                "HOME_HST_HOME": _avg(h["hst_home"][-FORM_MATCHES:]),
                "HOME_FORM_HOME": _form(h["pts_home"][-FORM_MATCHES:]),

                "AWAY_GF_AWAY": _avg(a["gf_away"][-FORM_MATCHES:]),
                "AWAY_GA_AWAY": _avg(a["ga_away"][-FORM_MATCHES:]),
                "AWAY_AST_AWAY": _avg(a["ast_away"][-FORM_MATCHES:]),
                "AWAY_FORM_AWAY": _form(a["pts_away"][-FORM_MATCHES:])

            })

            # Actualización histórico local
            h["gf_home"].append(row["FTHG"])
            h["ga_home"].append(row["FTAG"])
            h["hst_home"].append(row["HST"])

            if row["FTHG"] > row["FTAG"]:
                h["pts_home"].append(3)
            elif row["FTHG"] == row["FTAG"]:
                h["pts_home"].append(1)
            else:
                h["pts_home"].append(0)

            # Actualización histórico visitante
            a["gf_away"].append(row["FTAG"])
            a["ga_away"].append(row["FTHG"])
            a["ast_away"].append(row["AST"])

            if row["FTAG"] > row["FTHG"]:
                a["pts_away"].append(3)
            elif row["FTAG"] == row["FTHG"]:
                a["pts_away"].append(1)
            else:
                a["pts_away"].append(0)

    feat = pd.DataFrame(rows)

    return pd.concat(
        [df.reset_index(drop=True), feat],
        axis=1
    )