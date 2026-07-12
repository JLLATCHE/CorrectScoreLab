from config import (
    ATTACK_WEIGHT,
    DEFENSE_WEIGHT
)


def calculate_lambda(row):

    home_bonus = 1.0 + (
        (row["HOME_HST_HOME"] - row["HOME_GF_HOME"]) * 0.02
    )

    away_bonus = 1.0 + (
        (row["AWAY_AST_AWAY"] - row["AWAY_GF_AWAY"]) * 0.02
    )

    home_bonus = max(0.90, min(1.10, home_bonus))
    away_bonus = max(0.90, min(1.10, away_bonus))

    home_form = (
        0.95
        + row["HOME_FORM_HOME"] * 0.10
    )

    away_form = (
        0.95
        + row["AWAY_FORM_AWAY"] * 0.10
    )

    home_over = (
        0.95
        + row["HOME_OVER25_HOME"] * 0.10
    )

    away_over = (
        0.95
        + row["AWAY_OVER25_AWAY"] * 0.10
    )

    lambda_home = (

        row["HOME_GF_HOME"]

        * home_bonus

        * home_form

        * home_over

        * ATTACK_WEIGHT

        +

        row["AWAY_GA_AWAY"]

        * DEFENSE_WEIGHT

    )

    lambda_away = (

        row["AWAY_GF_AWAY"]

        * away_bonus

        * away_form

        * away_over

        * ATTACK_WEIGHT

        +

        row["HOME_GA_HOME"]

        * DEFENSE_WEIGHT

    )

    return lambda_home, lambda_away