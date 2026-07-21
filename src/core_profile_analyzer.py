"""
Core Profile Analyzer V0.2

Analiza el perfil de las señales candidatas al CORE
de CorrectScoreLab.

Objetivos:
- Separar señales por niveles CORE A, B y C.
- Comparar HIT vs MISS.
- Analizar variables CS.
- Probar perfiles candidatos.
- Medir rentabilidad de cada perfil.
- Guardar histórico por temporada.
- Preparar la futura construcción del CORE V1.

IMPORTANTE:
Este módulo es exclusivamente analítico.
No modifica las reglas actuales del CORE.
No modifica Portfolio Backtest.

LÓGICA ECONÓMICA:
- ODDS_TOP1_HIT indica si el TOP1 fue acertado.
- CUOTA contiene la cuota del marcador real.
- En un HIT, como TOP1 = marcador real, CUOTA es la
  cuota correspondiente al marcador apostado.
- Stake fijo teórico de 1 unidad por señal.
"""


from pathlib import Path

import pandas as pd


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RESULTS_FILE = (
    BASE_DIR
    / "data"
    / "results"
    / "core_profile_history.csv"
)


# ==========================================================
# NIVELES CORE
# ==========================================================

PROFILE_LEVELS = {

    "CORE_A": {
        "min_p": 0.16,
        "max_p": None,
    },

    "CORE_B": {
        "min_p": 0.14,
        "max_p": 0.16,
    },

    "CORE_C": {
        "min_p": 0.12,
        "max_p": 0.14,
    },

}


# ==========================================================
# VARIABLES CS
# ==========================================================

PRIMARY_CS_VARIABLES = [

    "CS001_ATTACK_EDGE",
    "CS002_DOMINANCE",
    "CS003_FORM_EDGE",
    "CS004_SHOTS_EDGE",
    "CS005_OVER_EDGE",
    "CS006_BTTS_EDGE",
    "CS007_HOME_ATTACK_EDGE",
    "CS007_AWAY_ATTACK_EDGE",

]


# ==========================================================
# PROFILE TESTS
# ==========================================================
#
# Son perfiles EXPLORATORIOS.
#
# No son reglas CORE.
# No modifican apuestas.
#
# Los umbrales se mantienen fijos para poder comparar
# exactamente el mismo perfil entre temporadas y ligas.
#
# ==========================================================

PROFILE_TESTS = [

    {
        "name": "ALL",
    },

    {
        "name": "DOM_GE_0.25",
        "dominance_min": 0.25,
    },

    {
        "name": "DOM_GE_0.50",
        "dominance_min": 0.50,
    },

    {
        "name": "AWAY_LE_1.00",
        "away_attack_max": 1.00,
    },

    {
        "name": "AWAY_LE_0.75",
        "away_attack_max": 0.75,
    },

    {
        "name": "DOM25_AWAY100",
        "dominance_min": 0.25,
        "away_attack_max": 1.00,
    },

    {
        "name": "DOM25_AWAY075",
        "dominance_min": 0.25,
        "away_attack_max": 0.75,
    },

    {
        "name": "DOM50_AWAY100",
        "dominance_min": 0.50,
        "away_attack_max": 1.00,
    },

    {
        "name": "DOM50_AWAY075",
        "dominance_min": 0.50,
        "away_attack_max": 0.75,
    },

]


# ==========================================================
# UTILIDADES
# ==========================================================

def _safe_mean(series):

    if len(series) == 0:
        return 0.0

    values = pd.to_numeric(
        series,
        errors="coerce"
    )

    if values.notna().sum() == 0:
        return 0.0

    return float(
        values.mean()
    )


# ==========================================================
# CREAR MÁSCARA DE NIVEL CORE
# ==========================================================

def _build_profile_mask(
    df,
    min_p,
    max_p
):

    p_top1 = pd.to_numeric(
        df["P_TOP1"],
        errors="coerce"
    )

    valid = (
        df["VALID"]
        .fillna(False)
        .astype(bool)
    )

    mask = (
        valid
        &
        (p_top1 >= min_p)
    )

    if max_p is not None:

        mask = (
            mask
            &
            (p_top1 < max_p)
        )

    return mask


# ==========================================================
# APLICAR PROFILE TEST
# ==========================================================

def _apply_test(
    df,
    test
):

    result = df.copy()

    # ------------------------------------------------------
    # DOMINANCE
    # ------------------------------------------------------

    if "dominance_min" in test:

        values = pd.to_numeric(
            result["CS002_DOMINANCE"],
            errors="coerce"
        )

        result = result[
            values >= test["dominance_min"]
        ]

    # ------------------------------------------------------
    # AWAY ATTACK EDGE
    # ------------------------------------------------------

    if "away_attack_max" in test:

        values = pd.to_numeric(
            result["CS007_AWAY_ATTACK_EDGE"],
            errors="coerce"
        )

        result = result[
            values <= test["away_attack_max"]
        ]

    return result


# ==========================================================
# CALCULAR RENTABILIDAD
# ==========================================================
#
# Replica la lógica utilizada por Odds Filter Analyzer:
#
# hits_df = data[data["ODDS_TOP1_HIT"]]
#
# La columna ODDS_TOP1_HIT es un booleano.
#
# CUOTA contiene la cuota del marcador real.
#
# Si TOP1 fue acertado:
# TOP1 = marcador real
#
# Por tanto CUOTA es la cuota que habría cobrado
# la apuesta al TOP1.
#
# ==========================================================

def _calculate_performance(
    df
):

    signals = len(df)

    if signals == 0:

        return {

            "signals": 0,
            "hits": 0,
            "hit_rate": 0.0,
            "avg_odds": 0.0,
            "stake": 0.0,
            "return": 0.0,
            "profit": 0.0,
            "roi": 0.0,

        }

    # ======================================================
    # IDENTIFICAR ACIERTOS TOP1
    # ======================================================

    hit_mask = (
        df["ODDS_TOP1_HIT"]
        .fillna(False)
        .astype(bool)
    )

    hits_df = df[
        hit_mask
    ].copy()

    hits = len(
        hits_df
    )

    hit_rate = (
        hits
        /
        signals
    )

    # ======================================================
    # CUOTAS DE LOS ACIERTOS
    # ======================================================

    if hits > 0:

        hit_odds = pd.to_numeric(
            hits_df["CUOTA"],
            errors="coerce"
        ).fillna(0.0)

        avg_odds = float(
            hit_odds.mean()
        )

        total_return = float(
            hit_odds.sum()
        )

    else:

        avg_odds = 0.0

        total_return = 0.0

    # ======================================================
    # STAKE
    # ======================================================

    stake = float(
        signals
    )

    # ======================================================
    # PROFIT
    # ======================================================

    profit = (
        total_return
        -
        stake
    )

    # ======================================================
    # ROI
    # ======================================================

    roi = (
        profit
        /
        stake
        if stake > 0
        else 0.0
    )

    return {

        "signals":
            signals,

        "hits":
            hits,

        "hit_rate":
            hit_rate,

        "avg_odds":
            avg_odds,

        "stake":
            stake,

        "return":
            total_return,

        "profit":
            profit,

        "roi":
            roi,

    }


# ==========================================================
# HIT VS MISS
# ==========================================================

def _analyze_hit_vs_miss(
    profile
):

    # Usamos TOP1_HIT para mantener el análisis
    # descriptivo original HIT vs MISS.

    hits = profile[
        profile["TOP1_HIT"] == True
    ]

    misses = profile[
        profile["TOP1_HIT"] != True
    ]

    print()
    print("PERFIL HIT VS MISS")
    print("-" * 100)

    print(

        f"{'VARIABLE':35}"

        f"{'HIT':>14}"

        f"{'MISS':>14}"

        f"{'DIF':>14}"

    )

    print("-" * 100)

    differences = []

    for column in PRIMARY_CS_VARIABLES:

        if column not in profile.columns:
            continue

        hit_mean = _safe_mean(
            hits[column]
        )

        miss_mean = _safe_mean(
            misses[column]
        )

        difference = (
            hit_mean
            -
            miss_mean
        )

        differences.append(

            (

                column,
                hit_mean,
                miss_mean,
                difference,

            )

        )

    differences = sorted(

        differences,

        key=lambda x: abs(x[3]),

        reverse=True

    )

    for (

        column,
        hit_mean,
        miss_mean,
        difference,

    ) in differences:

        print(

            f"{column:35}"

            f"{hit_mean:>14.4f}"

            f"{miss_mean:>14.4f}"

            f"{difference:>+14.4f}"

        )


# ==========================================================
# PROFILE TESTS
# ==========================================================

def _run_profile_tests(
    profile,
    level_name,
    season_name
):

    print()
    print("PROFILE TESTS")
    print("-" * 120)

    print(

        f"{'PROFILE':22}"

        f"{'SIGNALS':>10}"

        f"{'HITS':>8}"

        f"{'HIT%':>10}"

        f"{'AVG ODDS':>12}"

        f"{'STAKE':>10}"

        f"{'RETURN':>12}"

        f"{'PROFIT':>12}"

        f"{'ROI':>12}"

    )

    print("-" * 120)

    records = []

    for test in PROFILE_TESTS:

        # --------------------------------------------------
        # APLICAR PERFIL
        # --------------------------------------------------

        test_df = _apply_test(
            profile,
            test
        )

        # --------------------------------------------------
        # CALCULAR MÉTRICAS
        # --------------------------------------------------

        result = _calculate_performance(
            test_df
        )

        # --------------------------------------------------
        # MOSTRAR RESULTADO
        # --------------------------------------------------

        print(

            f"{test['name']:22}"

            f"{result['signals']:>10}"

            f"{result['hits']:>8}"

            f"{result['hit_rate']:>9.2%}"

            f"{result['avg_odds']:>12.2f}"

            f"{result['stake']:>10.2f}"

            f"{result['return']:>12.2f}"

            f"{result['profit']:>+12.2f}"

            f"{result['roi']:>11.2%}"

        )

        # --------------------------------------------------
        # GUARDAR REGISTRO
        # --------------------------------------------------

        record = {

            "SEASON":
                season_name,

            "LEVEL":
                level_name,

            "PROFILE":
                test["name"],

            "SIGNALS":
                result["signals"],

            "HITS":
                result["hits"],

            "HIT_RATE":
                result["hit_rate"],

            "AVG_ODDS":
                result["avg_odds"],

            "STAKE":
                result["stake"],

            "RETURN":
                result["return"],

            "PROFIT":
                result["profit"],

            "ROI":
                result["roi"],

        }

        records.append(
            record
        )

    return records


# ==========================================================
# ANALIZAR NIVEL
# ==========================================================

def _analyze_level(
    df,
    level_name,
    min_p,
    max_p,
    season_name
):

    mask = _build_profile_mask(

        df=df,

        min_p=min_p,

        max_p=max_p,

    )

    profile = df[
        mask
    ].copy()

    total = len(
        profile
    )

    print()
    print("=" * 100)
    print(level_name)
    print("=" * 100)

    if max_p is None:

        print(
            f"Rango P_TOP1 : >= {min_p:.2f}"
        )

    else:

        print(

            f"Rango P_TOP1 : "
            f"{min_p:.2f} <= P_TOP1 < {max_p:.2f}"

        )

    print(
        f"Señales      : {total}"
    )

    if total == 0:

        return []

    # ======================================================
    # RENDIMIENTO BASE
    # ======================================================

    performance = _calculate_performance(
        profile
    )

    print()
    print("RENDIMIENTO")
    print("-" * 60)

    print(
        f"HITS         : "
        f"{performance['hits']}"
    )

    print(
        f"MISS         : "
        f"{total - performance['hits']}"
    )

    print(
        f"HIT RATE     : "
        f"{performance['hit_rate']:.2%}"
    )

    print(
        f"P_TOP1 media : "
        f"{_safe_mean(profile['P_TOP1']):.2%}"
    )

    print(
        f"CUOTA MEDIA  : "
        f"{performance['avg_odds']:.2f}"
    )

    print(
        f"STAKE        : "
        f"{performance['stake']:.2f}"
    )

    print(
        f"RETURN       : "
        f"{performance['return']:.2f}"
    )

    print(
        f"PROFIT       : "
        f"{performance['profit']:+.2f}"
    )

    print(
        f"ROI          : "
        f"{performance['roi']:+.2%}"
    )

    # ======================================================
    # HIT VS MISS
    # ======================================================

    _analyze_hit_vs_miss(
        profile
    )

    # ======================================================
    # PROFILE TESTS
    # ======================================================

    records = _run_profile_tests(

        profile=profile,

        level_name=level_name,

        season_name=season_name,

    )

    return records


# ==========================================================
# GUARDAR HISTÓRICO
# ==========================================================

def _save_history(
    records,
    season_name
):

    if len(records) == 0:
        return

    new_rows = pd.DataFrame(
        records
    )

    RESULTS_FILE.parent.mkdir(

        parents=True,

        exist_ok=True

    )

    # ======================================================
    # CARGAR HISTÓRICO
    # ======================================================

    if RESULTS_FILE.exists():

        history = pd.read_csv(
            RESULTS_FILE
        )

        # --------------------------------------------------
        # ELIMINAR EJECUCIÓN ANTERIOR DE LA TEMPORADA
        # --------------------------------------------------
        #
        # Permite repetir el análisis sin crear duplicados.
        #
        # --------------------------------------------------

        if "SEASON" in history.columns:

            history = history[
                history["SEASON"] != season_name
            ]

        history = pd.concat(

            [

                history,
                new_rows,

            ],

            ignore_index=True

        )

    else:

        history = new_rows

    # ======================================================
    # ORDENAR
    # ======================================================

    history = history.sort_values(

        [

            "SEASON",
            "LEVEL",
            "PROFILE",

        ]

    ).reset_index(
        drop=True
    )

    # ======================================================
    # GUARDAR
    # ======================================================

    history.to_csv(

        RESULTS_FILE,

        index=False

    )

    print()
    print(
        "Histórico CORE PROFILE guardado en:"
    )

    print(
        RESULTS_FILE
    )


# ==========================================================
# ANALIZADOR PRINCIPAL
# ==========================================================

def analyze_core_profiles(
    odds_result,
    season_name
):

    print()
    print("=" * 100)
    print("CORE PROFILE ANALYZER V0.2")
    print("=" * 100)

    print()
    print(
        f"Temporada : {season_name}"
    )

    # ======================================================
    # VALIDAR COLUMNAS
    # ======================================================

    required_columns = [

        "VALID",
        "TOP1",
        "P_TOP1",
        "TOP1_HIT",
        "ODDS_TOP1_HIT",
        "CUOTA",
        "CS002_DOMINANCE",
        "CS007_AWAY_ATTACK_EDGE",

    ]

    missing = [

        column

        for column in required_columns

        if column not in odds_result.columns

    ]

    if missing:

        raise ValueError(

            "CORE PROFILE ANALYZER - "
            f"Faltan columnas: {missing}"

        )

    # ======================================================
    # COPIA DE SEGURIDAD
    # ======================================================

    df = odds_result.copy()

    print(
        f"Partidos  : {len(df)}"
    )

    valid_matches = (

        df["VALID"]
        .fillna(False)
        .astype(bool)
        .sum()

    )

    print(
        f"VALID     : {valid_matches}"
    )

    # ======================================================
    # ANALIZAR NIVELES
    # ======================================================

    all_records = []

    for (

        level_name,
        config,

    ) in PROFILE_LEVELS.items():

        records = _analyze_level(

            df=df,

            level_name=level_name,

            min_p=config["min_p"],

            max_p=config["max_p"],

            season_name=season_name,

        )

        all_records.extend(
            records
        )

    # ======================================================
    # GUARDAR HISTÓRICO
    # ======================================================

    _save_history(

        records=all_records,

        season_name=season_name,

    )

    print()
    print("=" * 100)
    print(
        "FIN CORE PROFILE ANALYZER V0.2"
    )
    print("=" * 100)

    return pd.DataFrame(
        all_records
    )