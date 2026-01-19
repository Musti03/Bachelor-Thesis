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


def is_brier_applicable(forecast: RiskForecast) -> bool:
    """
    Prüft, ob eine Prognose gemäß dem konzeptionellen Modell
    quantitativ mittels Brier Score bewertet werden darf.
    """

    # Bewertung nur auf Ebene E3
    if forecast.comparison_level != "E3":
        return False

    # Qualitative Prognosen sind nicht binär bewertbar
    if forecast.forecast_type == "PT4":
        return False

    # Outcome muss beobachtbar sein
    if forecast.outcome is None:
        return False

    # Wahrscheinlichkeit muss vorhanden sein
    if forecast.probability is None:
        return False

    # Häufigkeitsbasierte Outcomes benötigen eine Schwelle
    if forecast.outcome_class == "O2" and not forecast.threshold_definition:
        return False

    return True


def evaluate_forecasts(
    forecasts: List[RiskForecast]
) -> List[Dict[str, float]]:
    """
    Berechnet Brier Scores für alle zulässig bewertbaren Prognosen.

    Die Funktion dient ausschließlich der exemplarischen Evaluation
    des Prognoseformats und nicht der Leistungsbewertung einzelner Personen.
    """
    results: List[Dict[str, float]] = []

    for forecast in forecasts:
        if not is_brier_applicable(forecast):
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
    Berechnet den durchschnittlichen Brier Score über alle
    zulässig bewerteten Prognosen.
    """
    scores = [
        brier_score(f.probability, f.outcome)
        for f in forecasts
        if is_brier_applicable(f)
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

    Aggregationen erfolgen ausschließlich über Prognosen,
    die die Voraussetzungen für eine quantitative Bewertung erfüllen.
    """
    scores: Dict[str, float] = {}
    counts: Dict[str, int] = {}

    for forecast in forecasts:
        if not is_brier_applicable(forecast):
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
