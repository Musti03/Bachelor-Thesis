from typing import List, Dict, Optional
from models import RiskForecast


def brier_score(probability: float, outcome: int) -> float:
    """
    Berechnet den Brier Score für eine einzelne binäre Prognose.

    Der Brier Score misst die quadratische Abweichung zwischen
    prognostizierter Wahrscheinlichkeit p ∈ [0,1]
    und beobachtetem Ereignisausgang o ∈ {0,1}.
    """
    return (probability - outcome) ** 2


def evaluate_forecasts(
    forecasts: List[RiskForecast]
) -> List[Dict[str, float]]:
    """
    Berechnet Brier Scores für alle bewertbaren Prognosen.

    Diese Funktion dient ausschließlich der exemplarischen Evaluation
    des Prognoseformats und nicht der Leistungsbewertung einzelner Personen.
    """
    results: List[Dict[str, float]] = []

    for forecast in forecasts:
        if forecast.outcome is None:
            continue

        results.append(
            {
                "forecast_id": forecast.forecast_id,
                "brier_score": brier_score(
                    forecast.probability,
                    forecast.outcome
                ),
            }
        )

    return results


def mean_brier_score(
    forecasts: List[RiskForecast]
) -> Optional[float]:
    """
    Berechnet den durchschnittlichen Brier Score über alle bewerteten Prognosen.

    Der Mittelwert dient lediglich als aggregierte Kennzahl zur Illustration
    der quantitativen Auswertbarkeit des Prognoseformats.
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
    Aggregiert durchschnittliche Brier Scores nach einem Attribut
    (z. B. 'author' oder 'team').

    Diese Funktion ist optional und dient ausschließlich der Demonstration,
    dass aggregierte Auswertungen auf Basis des Prognoseformats möglich sind.
    Sie stellt keine Bewertung oder Rangordnung von Prognostizierenden dar.
    """
    scores: Dict[str, float] = {}
    counts: Dict[str, int] = {}

    for forecast in forecasts:
        if forecast.outcome is None:
            continue

        key = getattr(forecast, by, None)
        if not isinstance(key, str) or not key.strip():
            continue

        score = brier_score(forecast.probability, forecast.outcome)

        scores[key] = scores.get(key, 0.0) + score
        counts[key] = counts.get(key, 0) + 1

    return {
        key: scores[key] / counts[key]
        for key in scores
        if counts[key] > 0
    }
