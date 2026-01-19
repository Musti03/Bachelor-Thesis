from datetime import datetime, timedelta
from typing import Optional

from models import RiskForecast


DEFAULT_REFERENCE_HORIZON_DAYS = 365


def normalize_time_horizon(
    forecast: RiskForecast,
    *,
    reference_horizon_days: int = DEFAULT_REFERENCE_HORIZON_DAYS,
    assumption: Optional[str] = None,
) -> RiskForecast:
    """
    Normalisiert eine Prognose auf einen gemeinsamen Referenzhorizont.

    Die Funktion:
    - erzeugt eine neue Prognoseinstanz
    - verändert keine Wahrscheinlichkeit
    - dokumentiert explizit die zugrunde liegende Annahme
    - hebt die Vergleichsebene auf E2

    Diese Normalisierung stellt keine statistische Extrapolation dar,
    sondern dient ausschließlich der formalen Vergleichbarkeit.
    """

    if forecast.forecast_horizon_start is None or forecast.forecast_horizon_end is None:
        raise ValueError("Prognosehorizont muss vollständig angegeben sein.")

    # neuer Referenzhorizont
    start = forecast.forecast_horizon_start
    end = start + timedelta(days=reference_horizon_days)

    return RiskForecast(
        forecast_id=forecast.forecast_id,
        forecast_timestamp=forecast.forecast_timestamp,
        forecast_type=forecast.forecast_type,

        event_description=forecast.event_description,
        event_criteria=forecast.event_criteria,

        outcome_class=forecast.outcome_class,

        forecast_horizon_start=start,
        forecast_horizon_end=end,

        probability=forecast.probability,

        forecast_name=forecast.forecast_name,
        author=forecast.author,
        team=forecast.team,
        rationale=forecast.rationale,

        comparison_level="E2",

        normalization_applied=True,
        normalization_assumption=assumption
        or "Zeitliche Normalisierung auf Referenzhorizont zur formalen Vergleichbarkeit.",

        threshold_definition=forecast.threshold_definition,

        outcome=forecast.outcome,
        evaluation_timestamp=forecast.evaluation_timestamp,
    )
