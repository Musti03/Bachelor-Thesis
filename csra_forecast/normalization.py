from __future__ import annotations
from typing import Optional
from csra_forecast.models import RiskForecast


def normalize_probability_to_window(
    *,
    forecast: RiskForecast,
    target_window_days: int,
    assumption: str,
) -> RiskForecast:
    """
    Normalisiert eine Eintrittswahrscheinlichkeit auf einen
    gemeinsamen Zeitrahmen (z. B. 365 Tage).

    WICHTIG:
    - Dies ist KEIN Risikomodell.
    - Es handelt sich um eine dokumentierte Vergleichsannahme.

    Voraussetzungen:
    - explizite Wahrscheinlichkeit vorhanden
    - fixer Prognosehorizont (Start + Ende)
    - PT1 (binär)
    """

    if forecast.probability is None:
        raise ValueError("Normalisierung benötigt eine explizite Wahrscheinlichkeit.")

    if forecast.forecast_horizon_start is None or forecast.forecast_horizon_end is None:
        raise ValueError("Normalisierung benötigt einen festen Prognosehorizont.")

    if forecast.forecast_type != "PT1":
        raise ValueError("Normalisierung ist nur für PT1 sinnvoll.")

    delta_days = (forecast.forecast_horizon_end - forecast.forecast_horizon_start).days
    if delta_days <= 0:
        raise ValueError("Ungültiger Prognosehorizont.")

    # --- Annahme: konstante Hazard-Rate ---
    # sehr einfache, bewusst transparente Annahme
    # p_window = 1 - (1 - p_original)^(target / original)

    original_p = forecast.probability
    factor = target_window_days / delta_days

    normalized_p = 1 - (1 - original_p) ** factor
    normalized_p = min(max(normalized_p, 0.0), 1.0)

    # Forecast NICHT neu erzeugen → wir verändern bewusst den bestehenden
    forecast.probability = normalized_p
    forecast.normalization_applied = True
    forecast.normalization_assumption = assumption
    forecast.normalized_window_days = target_window_days
    forecast.comparison_level = "E2"

    return forecast
