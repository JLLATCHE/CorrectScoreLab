from loader import load_data
from validator import validate
from features import build_goal_features
from predictor import predict_scores
from ranking_dataset import export_ranking_dataset
from ranking_trainer import train_ranking_engine
from ranking_analysis import export_ranking_analysis
from backtest import evaluate


def main():

    print("=" * 60)
    print("CorrectScoreLab V0.2")
    print("=" * 60)

    df = load_data()

    validate(df)

    df = build_goal_features(df)

    df = predict_scores(df)

    # Exportar dataset del Ranking Engine
    export_ranking_dataset(df)

    # Entrenar Ranking Engine
    train_ranking_engine()

    # Análisis del laboratorio
    export_ranking_analysis(df)

    # Backtest principal
    result = evaluate(df)

    print()

    print(f"Partidos : {result['matches']:,}")
    print(f"TOP1     : {result['top1']:.2%}")
    print(f"TOP3     : {result['top3']:.2%}")
    print(f"TOP5     : {result['top5']:.2%}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()