"""
Core Filter Analyzer V0.1

Analiza el embudo real de selección del motor CORE.

Objetivos:
- Medir cuántos partidos son VALID.
- Medir cobertura de diferentes umbrales P_TOP1.
- Analizar rendimiento histórico de cada umbral.
- Detectar por qué CORE genera diferente cobertura entre ligas.
- Preparar el diseño de CORE V1.

IMPORTANTE:
Este módulo es únicamente de análisis.
NO modifica la estrategia CORE actual.
"""

import pandas as pd


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

CORE_THRESHOLDS = [
    0.10,
    0.12,
    0.14,
    0.15,
    0.16,
    0.18,
    0.20,
    0.22,
    0.25,
]

CORE_CURRENT_MIN_P = 0.16


# ==========================================================
# CORE FILTER ANALYZER
# ==========================================================

def analyze_core_filters(
    df,
    season_name
):

    print()
    print("=" * 100)
    print("CORE FILTER ANALYZER V0.1")
    print("=" * 100)

    data = df.copy()

    # ======================================================
    # VALIDACIÓN
    # ======================================================

    required_columns = [
        "TOP1",
        "P_TOP1",
        "VALID",
        "ODDS_REAL_SCORE",
        "CUOTA",
    ]

    missing = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing:

        raise ValueError(
            f"Faltan columnas para CoreFilterAnalyzer: {missing}"
        )

    # ======================================================
    # LIMPIEZA
    # ======================================================

    data["P_TOP1"] = pd.to_numeric(
        data["P_TOP1"],
        errors="coerce"
    )

    data["CUOTA"] = pd.to_numeric(
        data["CUOTA"],
        errors="coerce"
    )

    # ======================================================
    # EMBUDO VALID
    # ======================================================

    total_matches = len(data)

    valid_mask = (
        data["VALID"].eq(True)
    )

    valid_matches = int(
        valid_mask.sum()
    )

    invalid_matches = (
        total_matches
        -
        valid_matches
    )

    valid_coverage = (
        valid_matches
        /
        total_matches
        if total_matches > 0
        else 0
    )

    print()
    print(f"Temporada              : {season_name}")
    print()
    print(f"Partidos totales       : {total_matches}")
    print(f"VALID = True           : {valid_matches}")
    print(f"VALID = False          : {invalid_matches}")
    print(f"Cobertura VALID        : {valid_coverage:.2%}")

    # ======================================================
    # DISTRIBUCIÓN P_TOP1
    # Solo partidos VALID
    # ======================================================

    valid_data = data[
        valid_mask
    ].copy()

    print()
    print("=" * 100)
    print("COBERTURA POR UMBRAL P_TOP1")
    print("=" * 100)

    print()

    print(
        f"{'MIN P':<10}"
        f"{'SEÑALES':>10}"
        f"{'% TOTAL':>12}"
        f"{'% VALID':>12}"
        f"{'HITS':>10}"
        f"{'HIT RATE':>12}"
        f"{'STAKE':>12}"
        f"{'RETURN':>12}"
        f"{'PROFIT':>12}"
        f"{'ROI':>12}"
    )

    print("-" * 112)

    records = []

    for threshold in CORE_THRESHOLDS:

        threshold_data = valid_data[
            valid_data["P_TOP1"]
            >=
            threshold
        ].copy()

        signals = len(
            threshold_data
        )

        coverage_total = (
            signals
            /
            total_matches
            if total_matches > 0
            else 0
        )

        coverage_valid = (
            signals
            /
            valid_matches
            if valid_matches > 0
            else 0
        )

        hits = (
            threshold_data["TOP1"].astype(str)
            ==
            threshold_data["ODDS_REAL_SCORE"].astype(str)
        )

        hit_count = int(
            hits.sum()
        )

        hit_rate = (
            hit_count
            /
            signals
            if signals > 0
            else 0
        )

        # Stake CORE = 1 unidad por apuesta

        stake = float(
            signals
        )

        # La CUOTA disponible corresponde al marcador real.
        # Solo genera retorno cuando TOP1 coincide con el
        # marcador real.

        total_return = float(
            threshold_data.loc[
                hits,
                "CUOTA"
            ]
            .fillna(0)
            .sum()
        )

        profit = (
            total_return
            -
            stake
        )

        roi = (
            profit
            /
            stake
            if stake > 0
            else 0
        )

        current_marker = (
            " <- CORE ACTUAL"
            if threshold == CORE_CURRENT_MIN_P
            else ""
        )

        print(
            f"P >= {threshold:<5.2f}"
            f"{signals:>10}"
            f"{coverage_total:>11.2%}"
            f"{coverage_valid:>11.2%}"
            f"{hit_count:>10}"
            f"{hit_rate:>11.2%}"
            f"{stake:>12.2f}"
            f"{total_return:>12.2f}"
            f"{profit:>+12.2f}"
            f"{roi:>+11.2%}"
            f"{current_marker}"
        )

        records.append(
            {
                "SEASON":
                    season_name,

                "MIN_P":
                    threshold,

                "TOTAL_MATCHES":
                    total_matches,

                "VALID_MATCHES":
                    valid_matches,

                "SIGNALS":
                    signals,

                "COVERAGE_TOTAL":
                    coverage_total,

                "COVERAGE_VALID":
                    coverage_valid,

                "HITS":
                    hit_count,

                "HIT_RATE":
                    hit_rate,

                "STAKE":
                    stake,

                "RETURN":
                    total_return,

                "PROFIT":
                    profit,

                "ROI":
                    roi,
            }
        )

    # ======================================================
    # CORE ACTUAL
    # ======================================================

    current_core = valid_data[
        valid_data["P_TOP1"]
        >=
        CORE_CURRENT_MIN_P
    ].copy()

    current_signals = len(
        current_core
    )

    current_coverage = (
        current_signals
        /
        total_matches
        if total_matches > 0
        else 0
    )

    print()
    print("=" * 100)
    print("CORE ACTUAL")
    print("=" * 100)

    print()
    print(
        f"Umbral actual          : "
        f"P_TOP1 >= {CORE_CURRENT_MIN_P:.2f}"
    )

    print(
        f"Señales CORE           : "
        f"{current_signals}"
    )

    print(
        f"Cobertura CORE         : "
        f"{current_coverage:.2%}"
    )

    return pd.DataFrame(
        records
    )