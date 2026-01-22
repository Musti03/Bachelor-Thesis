from typing import List, Dict, Optional
from csra_forecast.models import RiskForecast


def brier_score(probability: float, outcome: int) -> float:
    return (probability - outcome) ** 2


def is_brier_applicable(f: RiskForecast) -> bool:
    """
    Minimal & ausreichend für Brier:
    - probability vorhanden
    - PT1 (binär)
    - O1 (eindeutig beobachtbar)
    - outcome gesetzt (0/1)

    Horizon ist NICHT Voraussetzung, weil:
    - EVENT / UNKNOWN kann später bewertet werden
    - Bewertbarkeit wird durch ex-post outcome hergestellt
    """
    if f.probability is None:
        return False
    if f.forecast_type != "PT1":
        return False
    if f.outcome_class != "O1":
        return False
    if f.outcome not in (0, 1):
        return False
    return True


def evaluate_forecasts(forecasts: List[RiskForecast]) -> List[Dict[str, float]]:
    results: List[Dict[str, float]] = []
    for f in forecasts:
        if not is_brier_applicable(f):
            continue
        results.append({"forecast_id": f.forecast_id, "brier_score": brier_score(f.probability, f.outcome)})
    return results


def mean_brier_score(forecasts: List[RiskForecast]) -> Optional[float]:
    scores = [brier_score(f.probability, f.outcome) for f in forecasts if is_brier_applicable(f)]
    if not scores:
        return None
    return sum(scores) / len(scores)


def aggregate_brier_scores(forecasts: List[RiskForecast], by: str = "author") -> Dict[str, float]:
    scores: Dict[str, float] = {}
    counts: Dict[str, int] = {}

    for f in forecasts:
        if not is_brier_applicable(f):
            continue

        key = getattr(f, by, None)
        if not isinstance(key, str) or not key.strip():
            continue

        s = brier_score(f.probability, f.outcome)
        scores[key] = scores.get(key, 0.0) + s
        counts[key] = counts.get(key, 0) + 1

    return {k: scores[k] / counts[k] for k in scores if counts.get(k, 0) > 0}
