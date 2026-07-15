"""
Motor de ejecución de métodos
"""

import runtime

import methods.cs001_attack_edge as cs001_attack_edge
import methods.cs002_defense_edge as cs002_defense_edge
import methods.cs003_form_edge as cs003_form_edge
import methods.cs004_shots_edge as cs004_shots_edge
import methods.cs005_over_profile as cs005_over_profile
import methods.cs006_btts_edge as cs006_btts_edge
import methods.cs007_attack_defense_compatibility as cs007_attack_defense_compatibility
import methods.cs008_goal_volatility as cs008_goal_volatility
import methods.cs009_goal_profile as cs009_goal_profile
import methods.cs010_winning_signature as cs010_winning_signature


METHODS = [

    ("CS001", cs001_attack_edge.apply),
    ("CS002", cs002_defense_edge.apply),
    ("CS003", cs003_form_edge.apply),
    ("CS004", cs004_shots_edge.apply),
    ("CS005", cs005_over_profile.apply),
    ("CS006", cs006_btts_edge.apply),
    ("CS007", cs007_attack_defense_compatibility.apply),
    ("CS008", cs008_goal_volatility.apply),
    ("CS009", cs009_goal_profile.apply),
    ("CS010", cs010_winning_signature.apply),

]


for name, _ in METHODS:

    runtime.register(name)


def apply_methods(df):

    df = df.copy()

    for name, method in METHODS:

        if runtime.is_enabled(name):

            df = method(df)

    return df