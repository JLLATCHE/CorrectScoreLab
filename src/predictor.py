import math
import itertools

from config import MAX_GOALS
from lambda_engine import calculate_lambda


def poisson(lmbda, k):

    return (
        math.exp(-lmbda)
        *
        (lmbda ** k)
    ) / math.factorial(k)


def predict_scores(df):

    df = df.copy()

    df["VALID"] = (

        (df["HOME_GF_HOME"] > 0)

        &

        (df["AWAY_GF_AWAY"] > 0)

    )

    top1 = []
    top2 = []
    top3 = []

    p_top1 = []
    p_top2 = []
    p_top3 = []

    top5 = []

    for _, row in df.iterrows():

        home_exp, away_exp = calculate_lambda(row)

        probs = []

        for hg, ag in itertools.product(

            range(MAX_GOALS + 1),

            repeat=2

        ):

            p = (

                poisson(home_exp, hg)

                *

                poisson(away_exp, ag)

            )

            probs.append(

                (

                    f"{hg}-{ag}",

                    p

                )

            )

        probs.sort(

            key=lambda x: x[1],

            reverse=True

        )

        top1.append(probs[0][0])
        top2.append(probs[1][0])
        top3.append(probs[2][0])

        p_top1.append(probs[0][1])
        p_top2.append(probs[1][1])
        p_top3.append(probs[2][1])

        top5.append(

            [x[0] for x in probs[:5]]

        )

    df["REAL_SCORE"] = (

        df["FTHG"].astype(str)

        +

        "-"

        +

        df["FTAG"].astype(str)

    )

    df["TOP1"] = top1
    df["TOP2"] = top2
    df["TOP3"] = top3

    df["P_TOP1"] = p_top1
    df["P_TOP2"] = p_top2
    df["P_TOP3"] = p_top3

    df["TOP5"] = top5

    df["TOP1_HIT"] = (

        (df["TOP1"] == df["REAL_SCORE"])

        &

        (df["VALID"])

    )

    df["TOP2_HIT"] = (

        (df["TOP2"] == df["REAL_SCORE"])

        &

        (df["VALID"])

    )

    df["TOP3_HIT"] = False
    df["TOP5_HIT"] = False

    for i in df.index:

        if not df.at[i, "VALID"]:

            continue

        real = df.at[i, "REAL_SCORE"]

        if real in [

            df.at[i, "TOP1"],

            df.at[i, "TOP2"],

            df.at[i, "TOP3"]

        ]:

            df.at[i, "TOP3_HIT"] = True

        if real in df.at[i, "TOP5"]:

            df.at[i, "TOP5_HIT"] = True

    return df