"""
Rare Score Lab

Laboratorio para estudiar partidos cuyo marcador real
tenía una cuota prepartido elevada.

Objetivos:

1. Analizar la distribución de partidos por rango de cuota.
2. Ver qué marcadores generan las cuotas altas.
3. Medir si el marcador real estaba en TOP1 / TOP3 / TOP5.
4. Analizar qué predijo TOP1 en partidos de cuota alta.
5. Comparar variables CS entre partidos normales y partidos
   con resultados de cuota elevada.

IMPORTANTE:
Este laboratorio NO modifica el predictor ni la BASE.
Es únicamente una herramienta de investigación.
"""


def analyze_rare_scores(df):

    print()
    print("=" * 60)
    print("RARE SCORE LAB")
    print("=" * 60)

    data = df.copy()

    # ==========================================================
    # VALIDACIÓN
    # ==========================================================

    required_columns = [

        "ODDS_REAL_SCORE",
        "CUOTA",
        "TOP1",
        "P_TOP1",
        "ODDS_TOP1_HIT",
        "ODDS_TOP3_HIT",
        "ODDS_TOP5_HIT",

    ]

    missing = [

        column

        for column in required_columns

        if column not in data.columns

    ]

    if missing:

        raise ValueError(
            f"Faltan columnas para RareScoreLab: {missing}"
        )

    # ==========================================================
    # LIMPIAR CUOTAS
    # ==========================================================

    data["CUOTA"] = data["CUOTA"].astype(float)

    # ==========================================================
    # FUNCIÓN DE ANÁLISIS
    # ==========================================================

    def analyze_group(
        label,
        group
    ):

        matches = len(group)

        if matches == 0:

            return

        top1_hits = int(
            group["ODDS_TOP1_HIT"].sum()
        )

        top3_hits = int(
            group["ODDS_TOP3_HIT"].sum()
        )

        top5_hits = int(
            group["ODDS_TOP5_HIT"].sum()
        )

        print()
        print(label)
        print("-" * 60)

        print(
            f"Partidos       : "
            f"{matches}"
        )

        print(
            f"Cuota media    : "
            f"{group['CUOTA'].mean():.2f}"
        )

        print(
            f"Cuota máxima   : "
            f"{group['CUOTA'].max():.2f}"
        )

        print(
            f"TOP1           : "
            f"{top1_hits}/{matches} "
            f"({top1_hits / matches:.2%})"
        )

        print(
            f"TOP3           : "
            f"{top3_hits}/{matches} "
            f"({top3_hits / matches:.2%})"
        )

        print(
            f"TOP5           : "
            f"{top5_hits}/{matches} "
            f"({top5_hits / matches:.2%})"
        )

        print(
            f"P_TOP1 media   : "
            f"{group['P_TOP1'].mean():.4f}"
        )

    # ==========================================================
    # RANGOS DE CUOTA
    # ==========================================================

    print()
    print("RENDIMIENTO POR RANGO DE CUOTA REAL")
    print("=" * 60)

    ranges = [

        (
            "CUOTA < 10",
            data[
                data["CUOTA"] < 10
            ]
        ),

        (
            "CUOTA 10 - 14.99",
            data[
                (data["CUOTA"] >= 10)
                &
                (data["CUOTA"] < 15)
            ]
        ),

        (
            "CUOTA 15 - 24.99",
            data[
                (data["CUOTA"] >= 15)
                &
                (data["CUOTA"] < 25)
            ]
        ),

        (
            "CUOTA 25 - 49.99",
            data[
                (data["CUOTA"] >= 25)
                &
                (data["CUOTA"] < 50)
            ]
        ),

        (
            "CUOTA >= 50",
            data[
                data["CUOTA"] >= 50
            ]
        ),

    ]

    for label, group in ranges:

        analyze_group(
            label,
            group
        )

    # ==========================================================
    # MARCADORES REALES DE CUOTA >= 15
    # ==========================================================

    rare = data[
        data["CUOTA"] >= 15
    ].copy()

    print()
    print("=" * 60)
    print("MARCADORES REALES CON CUOTA >= 15")
    print("=" * 60)

    rare_scores = (

        rare
        .groupby("ODDS_REAL_SCORE")
        .agg(

            PARTIDOS=(
                "ODDS_REAL_SCORE",
                "size"
            ),

            CUOTA_MEDIA=(
                "CUOTA",
                "mean"
            ),

            CUOTA_MAX=(
                "CUOTA",
                "max"
            ),

            TOP1_HITS=(
                "ODDS_TOP1_HIT",
                "sum"
            ),

            TOP3_HITS=(
                "ODDS_TOP3_HIT",
                "sum"
            ),

            TOP5_HITS=(
                "ODDS_TOP5_HIT",
                "sum"
            ),

        )
        .reset_index()

        .sort_values(

            by=[

                "PARTIDOS",
                "CUOTA_MEDIA",

            ],

            ascending=[

                False,
                False,

            ]

        )

    )

    for _, row in rare_scores.iterrows():

        print(

            f"{str(row['ODDS_REAL_SCORE']):6}"

            f"{int(row['PARTIDOS']):4} partidos   "

            f"avg {row['CUOTA_MEDIA']:7.2f}   "

            f"max {row['CUOTA_MAX']:7.2f}   "

            f"T1 {int(row['TOP1_HITS']):3}   "

            f"T3 {int(row['TOP3_HITS']):3}   "

            f"T5 {int(row['TOP5_HITS']):3}"

        )

    # ==========================================================
    # QUÉ PREDICE EL MODELO CUANDO OCURRE UN RESULTADO RARO
    # ==========================================================

    print()
    print("=" * 60)
    print("TOP1 PREDICHO CUANDO CUOTA REAL >= 15")
    print("=" * 60)

    predicted_scores = (

        rare["TOP1"]
        .value_counts()

    )

    for score, count in predicted_scores.items():

        percentage = (

            count / len(rare)

            if len(rare) > 0

            else 0

        )

        print(

            f"{str(score):6}"

            f"{count:4} predicciones   "

            f"{percentage:6.2%}"

        )

    # ==========================================================
    # TOP5 COMO DETECTOR DE RESULTADOS RAROS
    # ==========================================================

    print()
    print("=" * 60)
    print("CAPACIDAD DE DETECCIÓN DE CUOTAS ALTAS")
    print("=" * 60)

    thresholds = [

        10,
        15,
        20,
        25,
        30,
        50,

    ]

    print(
        f"{'CUOTA':<10}"
        f"{'MATCHES':>10}"
        f"{'TOP1':>10}"
        f"{'TOP3':>10}"
        f"{'TOP5':>10}"
    )

    for threshold in thresholds:

        group = data[
            data["CUOTA"] >= threshold
        ]

        matches = len(group)

        if matches == 0:

            continue

        top1 = (
            group["ODDS_TOP1_HIT"].mean()
        )

        top3 = (
            group["ODDS_TOP3_HIT"].mean()
        )

        top5 = (
            group["ODDS_TOP5_HIT"].mean()
        )

        print(

            f">= {threshold:<7}"

            f"{matches:>10}"

            f"{top1:>9.2%}"

            f"{top3:>9.2%}"

            f"{top5:>9.2%}"

        )

    # ==========================================================
    # VARIABLES CS
    #
    # Comparamos:
    #
    # NORMAL = cuota < 15
    # RARE   = cuota >= 15
    # ==========================================================

    print()
    print("=" * 60)
    print("VARIABLES CS - NORMAL VS CUOTA ALTA")
    print("=" * 60)

    normal = data[
        data["CUOTA"] < 15
    ]

    rare = data[
        data["CUOTA"] >= 15
    ]

    cs_columns = sorted([

        column

        for column in data.columns

        if column.startswith("CS")

    ])

    print(

        f"{'VARIABLE':35}"

        f"{'NORMAL':>12}"

        f"{'RARE':>12}"

        f"{'DIFF':>12}"

    )

    for column in cs_columns:

        normal_mean = (
            normal[column].mean()
        )

        rare_mean = (
            rare[column].mean()
        )

        diff = (
            rare_mean
            -
            normal_mean
        )

        print(

            f"{column:35}"

            f"{normal_mean:>12.4f}"

            f"{rare_mean:>12.4f}"

            f"{diff:>+12.4f}"

        )

    # ==========================================================
    # PARTIDOS DE CUOTA MUY ALTA
    # ==========================================================

    print()
    print("=" * 60)
    print("PARTIDOS CON CUOTA >= 25")
    print("=" * 60)

    very_rare = data[
        data["CUOTA"] >= 25
    ].copy()

    very_rare = very_rare.sort_values(

        by="CUOTA",

        ascending=False

    )

    columns_to_show = [

        column

        for column in [

            "FECHA",
            "LOCAL",
            "VISITANTE",
            "ODDS_REAL_SCORE",
            "CUOTA",
            "TOP1",
            "P_TOP1",
            "ODDS_TOP1_HIT",
            "ODDS_TOP3_HIT",
            "ODDS_TOP5_HIT",

        ]

        if column in very_rare.columns

    ]

    if len(very_rare) > 0:

        print()

        print(

            very_rare[
                columns_to_show
            ].to_string(

                index=False

            )

        )

    else:

        print()
        print(
            "No existen partidos con cuota >= 25"
        )