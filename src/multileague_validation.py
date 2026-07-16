"""
MultiLeague Validation Engine V0.1

Registra los resultados de validación de cada liga/temporada
probada con CorrectScoreLab.

Objetivos:
- Guardar resultados CORE.
- Guardar resultados RARE HOME.
- Guardar resultados RARE AWAY.
- Guardar resultados PORTFOLIO.
- Mantener histórico por liga y temporada.
- Diferenciar muestra de desarrollo y validación externa.
- Preparar la futura validación automática de múltiples temporadas.

Los resultados se guardan en:

data/results/multileague_validation.csv
"""

from pathlib import Path

import pandas as pd


RESULTS_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "results"
    / "multileague_validation.csv"
)


DEVELOPMENT_SAMPLE = "ESP_2021"


def register_validation(
    season_name,
    portfolio_result
):

    print()
    print("=" * 100)
    print("MULTILEAGUE VALIDATION ENGINE V0.1")
    print("=" * 100)

    # ======================================================
    # VALIDACIÓN
    # ======================================================

    required_keys = [
        "core",
        "rare_home",
        "rare_away",
        "total",
    ]

    missing = [
        key
        for key in required_keys
        if key not in portfolio_result
    ]

    if missing:

        raise ValueError(
            f"Faltan resultados del Portfolio Backtest: {missing}"
        )

    # ======================================================
    # EXTRAER RESULTADOS
    # ======================================================

    core = portfolio_result["core"]

    rare_home = portfolio_result["rare_home"]

    rare_away = portfolio_result["rare_away"]

    total = portfolio_result["total"]

    sample_type = (
        "DEVELOPMENT"
        if season_name == DEVELOPMENT_SAMPLE
        else "VALIDATION"
    )

    # ======================================================
    # CREAR REGISTRO
    # ======================================================

    record = {

        "SEASON":
            season_name,

        "SAMPLE_TYPE":
            sample_type,

        # CORE

        "CORE_SIGNALS":
            core["signals"],

        "CORE_STAKE":
            core["stake"],

        "CORE_RETURN":
            core["return"],

        "CORE_PROFIT":
            core["profit"],

        "CORE_ROI":
            core["roi"],

        # RARE HOME

        "RARE_HOME_SIGNALS":
            rare_home["signals"],

        "RARE_HOME_STAKE":
            rare_home["stake"],

        "RARE_HOME_RETURN":
            rare_home["return"],

        "RARE_HOME_PROFIT":
            rare_home["profit"],

        "RARE_HOME_ROI":
            rare_home["roi"],

        # RARE AWAY

        "RARE_AWAY_SIGNALS":
            rare_away["signals"],

        "RARE_AWAY_STAKE":
            rare_away["stake"],

        "RARE_AWAY_RETURN":
            rare_away["return"],

        "RARE_AWAY_PROFIT":
            rare_away["profit"],

        "RARE_AWAY_ROI":
            rare_away["roi"],

        # PORTFOLIO

        "PORTFOLIO_MATCHES":
            total["matches"],

        "PORTFOLIO_STAKE":
            total["stake"],

        "PORTFOLIO_RETURN":
            total["return"],

        "PORTFOLIO_PROFIT":
            total["profit"],

        "PORTFOLIO_ROI":
            total["roi"],

        "MAX_DRAWDOWN":
            total["max_drawdown"],

        "MAX_LOSING_STREAK":
            total["max_losing_streak"],

    }

    new_row = pd.DataFrame(
        [record]
    )

    # ======================================================
    # CREAR DIRECTORIO
    # ======================================================

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

        # Eliminar registro anterior de la misma temporada.
        # Así podemos volver a ejecutar sin duplicar filas.

        history = history[
            history["SEASON"] != season_name
        ]

        history = pd.concat(
            [
                history,
                new_row,
            ],
            ignore_index=True
        )

    else:

        history = new_row

    # ======================================================
    # ORDENAR
    # ======================================================

    history = history.sort_values(
        [
            "SAMPLE_TYPE",
            "SEASON",
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

    # ======================================================
    # MOSTRAR TABLA
    # ======================================================

    print()
    print("VALIDACIONES REGISTRADAS")
    print("-" * 115)

    print(
        f"{'SEASON':12}"
        f"{'TYPE':14}"
        f"{'CORE ROI':>12}"
        f"{'RH ROI':>12}"
        f"{'RA ROI':>12}"
        f"{'PORT ROI':>12}"
        f"{'PROFIT':>12}"
        f"{'MAX DD':>12}"
    )

    print("-" * 115)

    for _, row in history.iterrows():

        print(

            f"{row['SEASON']:12}"

            f"{row['SAMPLE_TYPE']:14}"

            f"{row['CORE_ROI']:>11.2%}"

            f"{row['RARE_HOME_ROI']:>11.2%}"

            f"{row['RARE_AWAY_ROI']:>11.2%}"

            f"{row['PORTFOLIO_ROI']:>11.2%}"

            f"{row['PORTFOLIO_PROFIT']:>+12.2f}"

            f"{row['MAX_DRAWDOWN']:>12.2f}"

        )

    # ======================================================
    # VALIDACIÓN EXTERNA ACUMULADA
    # ======================================================

    validation = history[
        history["SAMPLE_TYPE"] == "VALIDATION"
    ].copy()

    print()
    print("=" * 100)
    print("RESUMEN - VALIDACIÓN EXTERNA")
    print("=" * 100)

    if len(validation) == 0:

        print(
            "Todavía no existen muestras de validación externa."
        )

    else:

        seasons = len(
            validation
        )

        positive_core = (
            validation["CORE_PROFIT"] > 0
        ).sum()

        positive_rare_home = (
            validation["RARE_HOME_PROFIT"] > 0
        ).sum()

        positive_rare_away = (
            validation["RARE_AWAY_PROFIT"] > 0
        ).sum()

        positive_portfolio = (
            validation["PORTFOLIO_PROFIT"] > 0
        ).sum()

        total_stake = validation[
            "PORTFOLIO_STAKE"
        ].sum()

        total_return = validation[
            "PORTFOLIO_RETURN"
        ].sum()

        total_profit = (
            total_return
            -
            total_stake
        )

        total_roi = (
            total_profit
            /
            total_stake
            if total_stake > 0
            else 0
        )

        print(
            f"Temporadas validación   : {seasons}"
        )

        print(
            f"CORE positivas          : "
            f"{positive_core}/{seasons}"
        )

        print(
            f"RARE HOME positivas     : "
            f"{positive_rare_home}/{seasons}"
        )

        print(
            f"RARE AWAY positivas     : "
            f"{positive_rare_away}/{seasons}"
        )

        print(
            f"PORTFOLIO positivas     : "
            f"{positive_portfolio}/{seasons}"
        )

        print()

        print(
            f"Stake validación        : "
            f"{total_stake:.2f}"
        )

        print(
            f"Retorno validación      : "
            f"{total_return:.2f}"
        )

        print(
            f"Beneficio validación    : "
            f"{total_profit:+.2f}"
        )

        print(
            f"ROI validación          : "
            f"{total_roi:+.2%}"
        )

    print()
    print(
        f"Registro guardado en:\n"
        f"{RESULTS_FILE}"
    )

    return history