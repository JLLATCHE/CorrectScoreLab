"""
Odds Matcher

Cruza los partidos del dataset de cuotas
con los partidos procesados por CorrectScoreLab.
"""

import pandas as pd
import unicodedata


# ==========================================================
# TEAM MAPPING
# ==========================================================

TEAM_MAPPING = {

    "rayo vallecano": "vallecano",
    "celta de vigo": "celta",
    "atletico madrid": "ath madrid",
    "athletic club": "ath bilbao",
    "real sociedad": "sociedad",

    # Corrección typo detectado en odds
    "real socieda": "sociedad",

}


def normalize_team(name):

    name = str(name).strip().lower()

    # Eliminar tildes
    name = "".join(

        char

        for char in unicodedata.normalize(
            "NFD",
            name
        )

        if unicodedata.category(char) != "Mn"

    )

    # Aplicar mapping
    name = TEAM_MAPPING.get(
        name,
        name
    )

    return name


def match_odds(df, odds_df):

    print()
    print("=" * 60)
    print("ODDS MATCHER")
    print("=" * 60)

    model_df = df.copy()
    odds = odds_df.copy()

    # ==========================================================
    # NORMALIZAR FECHAS
    # ==========================================================

    model_df["Date"] = pd.to_datetime(
        model_df["Date"],
        errors="coerce",
        dayfirst=True
    )

    odds["FECHA"] = pd.to_datetime(
        odds["FECHA"],
        errors="coerce"
    )

    # ==========================================================
    # NORMALIZAR EQUIPOS MODELO
    # ==========================================================

    model_df["_HOME_KEY"] = (
        model_df["HomeTeam"]
        .apply(normalize_team)
    )

    model_df["_AWAY_KEY"] = (
        model_df["AwayTeam"]
        .apply(normalize_team)
    )

    # ==========================================================
    # NORMALIZAR EQUIPOS ODDS
    # ==========================================================

    odds["_HOME_KEY"] = (
        odds["LOCAL"]
        .apply(normalize_team)
    )

    odds["_AWAY_KEY"] = (
        odds["VISITANTE"]
        .apply(normalize_team)
    )

    # ==========================================================
    # CRUCE
    # ==========================================================

    matched = odds.merge(

        model_df,

        left_on=[
            "FECHA",
            "_HOME_KEY",
            "_AWAY_KEY"
        ],

        right_on=[
            "Date",
            "_HOME_KEY",
            "_AWAY_KEY"
        ],

        how="left",

        indicator=True

    )

    # ==========================================================
    # RESULTADOS
    # ==========================================================

    found = (
        matched["_merge"] == "both"
    ).sum()

    missing = (
        matched["_merge"] == "left_only"
    ).sum()

    print(f"Partidos cuotas : {len(odds):,}")
    print(f"Encontrados     : {found:,}")
    print(f"No encontrados  : {missing:,}")

    # ==========================================================
    # MOSTRAR NO ENCONTRADOS
    # ==========================================================

    if missing > 0:

        print()
        print("PARTIDOS NO ENCONTRADOS")
        print("-" * 60)

        missing_df = matched[
            matched["_merge"] == "left_only"
        ]

        print(

            missing_df[
                [
                    "FECHA",
                    "LOCAL",
                    "VISITANTE",
                    "_HOME_KEY",
                    "_AWAY_KEY",
                ]
            ]
            .to_string(index=False)

        )

    else:

        print()
        print("Cruce perfecto: 380/380")

    return matched