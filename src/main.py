from loader import load_data
from validator import validate
from features import build_goal_features
from predictor import predict_scores
from backtest import evaluate

from method_analyzer import analyze
from score_analyzer import analyze_scores
from confusion_analyzer import analyze_confusions
from one_one_analyzer import analyze_one_one
from odds_loader import load_odds, ODDS_SHEET
from odds_matcher import match_odds
from odds_backtest import evaluate_odds
from odds_analyzer import analyze_odds
from odds_filter_analyzer import analyze_odds_filters
from season_exporter import export_season_results
from one_one_season_lab import analyze_one_one_season
from one_zero_season_lab import analyze_one_zero_season
from rare_score_lab import analyze_rare_scores
from extreme_score_lab import analyze_extreme_scores
from blowout_detector_lab import analyze_blowout_detector
from rare_strategy_backtest import backtest_rare_strategies
from core_selector_lab import analyze_core_selectors
from portfolio_backtest import backtest_portfolio
from multileague_validation import register_validation


def main():

    print("=" * 60)
    print("CorrectScoreLab V0.2")
    print("=" * 60)

    df = load_data()

    validate(df)

    df = build_goal_features(df)

    df = predict_scores(df)

    analyze(df)

    analyze_scores(df)

    analyze_confusions(df)

    analyze_one_one(df)

    odds_df = load_odds()

    matched_df = match_odds(df, odds_df)

    odds_result = evaluate_odds(matched_df)

    analyze_odds(odds_result)

    analyze_odds_filters(odds_result)

    season_results = export_season_results(odds_result)

    analyze_one_one_season(odds_result)

    analyze_one_zero_season(odds_result)

    analyze_rare_scores(odds_result)

    analyze_extreme_scores(odds_result)

    analyze_blowout_detector(odds_result)

    backtest_rare_strategies(odds_result)

    analyze_core_selectors(odds_result)

    portfolio_result = backtest_portfolio(
        odds_result
    )

    register_validation(
         ODDS_SHEET,
        portfolio_result
    )

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