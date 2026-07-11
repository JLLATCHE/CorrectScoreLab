import math
import itertools

from config import MAX_GOALS
from config import ATTACK_WEIGHT
from config import DEFENSE_WEIGHT


def poisson(lmbda, k):
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)


def predict_scores(df):

    df = df.copy()

    df["VALID"] = (
        (df["HOME_GF_HOME"] > 0)
        &
        (df["AWAY_GF_AWAY"] > 0)
    )

    top1 = []
    top3 = []
    top5 = []

    for _, row in df.iterrows():

        # Ajuste muy suave utilizando los nuevos indicadores
        home_bonus = 1.0 + ((row["HOME_HST_HOME"] - row["HOME_GF_HOME"]) * 0.02)
        away_bonus = 1.0 + ((row["AWAY_AST_AWAY"] - row["AWAY_GF_AWAY"]) * 0.02)

        home_bonus = max(0.90, min(1.10, home_bonus))
        away_bonus = max(0.90, min(1.10, away_bonus))

        home_exp = (
            row["HOME_GF_HOME"] * home_bonus * ATTACK_WEIGHT +
            row["AWAY_GA_AWAY"] * DEFENSE_WEIGHT
        )

        away_exp = (
            row["AWAY_GF_AWAY"] * away_bonus * ATTACK_WEIGHT +
            row["HOME_GA_HOME"] * DEFENSE_WEIGHT
        )

        probs = []

        for hg, ag in itertools.product(range(MAX_GOALS + 1), repeat=2):

            p = poisson(home_exp, hg) * poisson(away_exp, ag)

            probs.append((f"{hg}-{ag}", p))

        probs.sort(key=lambda x: x[1], reverse=True)

        top1.append(probs[0][0])
        top3.append([x[0] for x in probs[:3]])
        top5.append([x[0] for x in probs[:5]])

    df["REAL_SCORE"] = (
        df["FTHG"].astype(str)
        + "-"
        + df["FTAG"].astype(str)
    )

    df["TOP1"] = top1
    df["TOP3"] = top3
    df["TOP5"] = top5

    df["TOP1_HIT"] = (
        (df["TOP1"] == df["REAL_SCORE"])
        &
        (df["VALID"])
    )

    df["TOP3_HIT"] = False
    df["TOP5_HIT"] = False

    for i in df.index:

        if not df.at[i, "VALID"]:
            continue

        real = df.at[i, "REAL_SCORE"]

        if real in df.at[i, "TOP3"]:
            df.at[i, "TOP3_HIT"] = True

        if real in df.at[i, "TOP5"]:
            df.at[i, "TOP5_HIT"] = True

    return df