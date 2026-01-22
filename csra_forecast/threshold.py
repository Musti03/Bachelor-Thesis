from typing import Optional

from csra_forecast.models import RiskForecast


def apply_threshold(
    forecast: RiskForecast,
    *,
    threshold_definition: str,
    assumption: Optional[str] = None,
) -> RiskForecast:
    """
    Transformiert eine häufigkeitsbasierte Prognose in eine binäre Ereignisprognose,
    indem eine explizite Schwelle definiert wird.

    Die Transformation:
    - erzeugt eine neue Prognoseinstanz
    - verändert keine Wahrscheinlichkeit
    - dokumentiert die Schwellenannahme explizit
    - hebt die Vergleichsebene auf E2

    Diese Abbildung dient ausschließlich der formalen Vergleichbarkeit
    und stellt keine inhaltliche Neubewertung dar.
    """

    if not threshold_definition or not threshold_definition.strip():
        raise ValueError("threshold_definition muss explizit angegeben werden.")

    # Schwellenbasierte Prognosen müssen explizit als solche gekennzeichnet sein
    if forecast.forecast_type != "PT2":
        raise ValueError("apply_threshold ist nur für Prognosetyp PT2 zulässig.")

    return RiskForecast(
        forecast_id=forecast.forecast_id,
        forecast_timestamp=forecast.forecast_timestamp,

        # Prognosetyp wird auf Ereigniseintritt abgebildet
        forecast_type="PT1",

        event_description=forecast.event_description,
        event_criteria=forecast.event_criteria,

        # Outcome-Klasse bleibt erhalten (z. B. O3 → Schwellenereignis)
        outcome_class=forecast.outcome_class,

        forecast_horizon_start=forecast.forecast_horizon_start,
        forecast_horizon_end=forecast.forecast_horizon_end,

        probability=forecast.probability,

        forecast_name=forecast.forecast_name,
        author=forecast.author,
        team=forecast.team,
        rationale=forecast.rationale,

        comparison_level="E2",

        normalization_applied=forecast.normalization_applied,
        normalization_assumption=forecast.normalization_assumption,

        threshold_definition=threshold_definition,

        outcome=forecast.outcome,
        evaluation_timestamp=forecast.evaluation_timestamp,
    )
