import pandas as pd

from config import FORM_MATCHES


def _avg(values):

    if not values:
        return 0.0

    return sum(values) / len(values)


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
                    "gf_away": [],
                    "ga_away": [],
                    "ast_away": []
                }

            if away not in history:
                history[away] = {
                    "gf_home": [],
                    "ga_home": [],
                    "hst_home": [],
                    "gf_away": [],
                    "ga_away": [],
                    "ast_away": []
                }

            h = history[home]
            a = history[away]

            rows.append({

                "HOME_GF_HOME": _avg(h["gf_home"][-FORM_MATCHES:]),
                "HOME_GA_HOME": _avg(h["ga_home"][-FORM_MATCHES:]),
                "HOME_HST_HOME": _avg(h["hst_home"][-FORM_MATCHES:]),

                "AWAY_GF_AWAY": _avg(a["gf_away"][-FORM_MATCHES:]),
                "AWAY_GA_AWAY": _avg(a["ga_away"][-FORM_MATCHES:]),
                "AWAY_AST_AWAY": _avg(a["ast_away"][-FORM_MATCHES:])

            })

            h["gf_home"].append(row["FTHG"])
            h["ga_home"].append(row["FTAG"])
            h["hst_home"].append(row["HST"])

            a["gf_away"].append(row["FTAG"])
            a["ga_away"].append(row["FTHG"])
            a["ast_away"].append(row["AST"])

    feat = pd.DataFrame(rows)

    return pd.concat(
        [df.reset_index(drop=True), feat],
        axis=1
    )