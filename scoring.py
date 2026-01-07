from typing import List, Dict, Optional
from models import RiskForecast


def brier_score(probability: float, outcome: int) -> float:
    """
    Berechnet den Brier Score für eine einzelne binäre Prognose.
    """
    return (probability - outcome) ** 2


def evaluate_forecasts(forecasts: List[RiskForecast]) -> List[dict]:
    """
    Berechnet Brier Scores für alle bewerteten Prognosen.

    Rückgabe:
    Liste von Dictionaries mit Prognose-ID und Brier Score.
    """
    results = []

    for forecast in forecasts:
        if forecast.outcome is None:
            continue

        score = brier_score(forecast.probability, forecast.outcome)

        results.append(
            {
                "forecast_id": forecast.forecast_id,
                "brier_score": score,
            }
        )

    return results


def mean_brier_score(forecasts: List[RiskForecast]) -> Optional[float]:
    """
    Berechnet den durchschnittlichen Brier Score über alle bewerteten Prognosen.
    """
    scores = [
        brier_score(f.probability, f.outcome)
        for f in forecasts
        if f.outcome is not None
    ]

    if not scores:
        return None

    return sum(scores) / len(scores)


def aggregate_brier_scores(
    forecasts: List[RiskForecast],
    by: str = "author"
) -> Dict[str, float]:
    """
    Aggregiert durchschnittliche Brier Scores nach Urheber oder Team.
    """

    scores: Dict[str, float] = {}
    counts: Dict[str, int] = {}

    for f in forecasts:
        if f.outcome is None:
            continue

        key = getattr(f, by, None)
        if not key:
            continue

        score = brier_score(f.probability, f.outcome)

        scores[key] = scores.get(key, 0.0) + score
        counts[key] = counts.get(key, 0) + 1

    return {
        k: scores[k] / counts[k]
        for k in scores
        if counts[k] > 0
    }
