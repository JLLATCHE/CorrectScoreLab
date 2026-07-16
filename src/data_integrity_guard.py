"""
Data Integrity Guard V0.1

Protege las validaciones de CorrectScoreLab frente a:

- Temporadas incompletas.
- Partidos de cuotas no encontrados.
- Duplicados.
- Fechas inválidas.
- Cuotas inválidas.
- Cruces parciales.

Una validación NO debe continuar si la integridad
de los datos no es correcta.
"""


def validate_season_integrity(
    odds_df,
    matched_df,
    season_name,
    expected_matches=380
):

    print()
    print("=" * 100)
    print("DATA INTEGRITY GUARD V0.1")
    print("=" * 100)

    errors = []

    # ======================================================
    # PARTIDOS ESPERADOS
    # ======================================================

    odds_matches = len(odds_df)

    if odds_matches != expected_matches:

        errors.append(
            f"Partidos en cuotas: "
            f"{odds_matches} "
            f"(esperados: {expected_matches})"
        )

    # ======================================================
    # FECHAS INVÁLIDAS
    # ======================================================

    if "FECHA" in odds_df.columns:

        invalid_dates = (
            odds_df["FECHA"]
            .isna()
            .sum()
        )

        if invalid_dates > 0:

            errors.append(
                f"Fechas inválidas: "
                f"{invalid_dates}"
            )

    # ======================================================
    # CUOTAS INVÁLIDAS
    # ======================================================

    if "CUOTA" in odds_df.columns:

        invalid_odds = (
            odds_df["CUOTA"]
            .isna()
            .sum()
        )

        if invalid_odds > 0:

            errors.append(
                f"Cuotas inválidas: "
                f"{invalid_odds}"
            )

    # ======================================================
    # DUPLICADOS
    # ======================================================

    duplicate_columns = [
        "FECHA",
        "LOCAL",
        "VISITANTE",
    ]

    if all(
        column in odds_df.columns
        for column in duplicate_columns
    ):

        duplicates = odds_df.duplicated(
            subset=duplicate_columns
        ).sum()

        if duplicates > 0:

            errors.append(
                f"Partidos duplicados: "
                f"{duplicates}"
            )

    # ======================================================
    # PARTIDOS ENCONTRADOS POR MATCHER
    # ======================================================

    if "_merge" not in matched_df.columns:

        errors.append(
            "El Odds Matcher no contiene "
            "la columna de control '_merge'."
        )

        matched_matches = 0
        missing_matches = odds_matches

    else:

        matched_matches = (
            matched_df["_merge"]
            == "both"
        ).sum()

        missing_matches = (
            matched_df["_merge"]
            == "left_only"
        ).sum()

        if matched_matches != odds_matches:

            errors.append(
                f"Partidos cruzados: "
                f"{matched_matches}/{odds_matches}"
            )

        if missing_matches > 0:

            errors.append(
                f"Partidos no encontrados: "
                f"{missing_matches}"
            )

    # ======================================================
    # RESUMEN
    # ======================================================

    print()
    print(f"Temporada          : {season_name}")
    print(f"Partidos esperados : {expected_matches}")
    print(f"Partidos cuotas    : {odds_matches}")
    print(f"Partidos cruzados  : {matched_matches}")
    print(f"No encontrados     : {missing_matches}")

    # ======================================================
    # BLOQUEAR SI HAY ERRORES
    # ======================================================

    if errors:

        print()
        print("ESTADO             : BLOQUEADO")
        print()
        print("ERRORES DETECTADOS")
        print("-" * 60)

        for error in errors:

            print(
                f"- {error}"
            )

        print()
        print(
            "La temporada NO puede continuar "
            "hacia el backtest ni registrarse "
            "como validación."
        )

        raise ValueError(
            f"Data Integrity Guard bloqueó "
            f"la temporada {season_name}."
        )

    # ======================================================
    # OK
    # ======================================================

    print()
    print("ESTADO             : OK")
    print()
    print(
        "Integridad confirmada. "
        "La temporada puede continuar."
    )

    return True