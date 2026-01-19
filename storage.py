import json
from pathlib import Path
from typing import List, Optional, Any
from datetime import datetime

from models import RiskForecast

# Persistenter Speicher (lokale Datei)
DATA_FILE = Path("forecasts.json")


# Hilfsfunktionen
def _serialize_datetime(value: Optional[datetime]) -> Optional[str]:
    if isinstance(value, datetime):
        return value.isoformat()
    return None if value is None else value


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value)


def forecast_to_dict(forecast: RiskForecast) -> dict:
    """
    Wandelt ein RiskForecast-Objekt in ein JSON-serialisierbares Dictionary um.
    """
    return {
        "forecast_id": forecast.forecast_id,
        "forecast_name": forecast.forecast_name,
        "author": forecast.author,
        "team": forecast.team,

        # Kernfelder
        "forecast_type": forecast.forecast_type,
        "outcome_class": forecast.outcome_class,
        "comparison_level": forecast.comparison_level,

        "event_description": forecast.event_description,
        "event_criteria": forecast.event_criteria,

        "forecast_timestamp": _serialize_datetime(forecast.forecast_timestamp),
        "forecast_horizon_start": _serialize_datetime(forecast.forecast_horizon_start),
        "forecast_horizon_end": _serialize_datetime(forecast.forecast_horizon_end),

        "probability": forecast.probability,
        "rationale": forecast.rationale,

        # Transformations-Metadaten
        "normalization_applied": forecast.normalization_applied,
        "normalization_assumption": forecast.normalization_assumption,
        "threshold_definition": forecast.threshold_definition,

        # Bewertung
        "outcome": forecast.outcome,
        "evaluation_timestamp": _serialize_datetime(forecast.evaluation_timestamp),
    }


def dict_to_forecast(data: dict) -> RiskForecast:
    """
    Rekonstruiert ein RiskForecast-Objekt aus einem gespeicherten Dictionary.

    Abwärtskompatibilität:
    - ältere Dateien enthalten neue Modellfelder noch nicht
    """

    # Name-Fallback
    raw_name = data.get("forecast_name") or data.get("forecast_title")
    forecast_name = (raw_name or "").strip() or "Unbenannte Prognose"

    author = (data.get("author") or "").strip() or None
    team = (data.get("team") or "").strip() or None
    rationale = data.get("rationale")

    outcome_raw: Any = data.get("outcome")
    outcome = int(outcome_raw) if outcome_raw in (0, 1, "0", "1") else None

    return RiskForecast(
        forecast_id=data["forecast_id"],
        forecast_name=forecast_name,
        author=author,
        team=team,

        # --- neue Modellfelder ---
        forecast_type=data.get("forecast_type", "PT1"),
        outcome_class=data.get("outcome_class", "O1"),
        comparison_level=data.get("comparison_level", "E1"),

        normalization_applied=bool(data.get("normalization_applied", False)),
        normalization_assumption=data.get("normalization_assumption"),
        threshold_definition=data.get("threshold_definition"),

        # --- Kern ---
        event_description=(data.get("event_description") or "").strip(),
        event_criteria=(data.get("event_criteria") or "").strip(),

        forecast_timestamp=_parse_datetime(
            data.get("forecast_timestamp")
        ) or datetime.utcnow(),

        forecast_horizon_start=_parse_datetime(
            data.get("forecast_horizon_start")
        ) or datetime.utcnow(),

        forecast_horizon_end=_parse_datetime(
            data.get("forecast_horizon_end")
        ) or datetime.utcnow(),

        probability=float(data["probability"]),
        rationale=(rationale.strip() if isinstance(rationale, str) and rationale.strip() else None),

        # --- Bewertung ---
        outcome=outcome,
        evaluation_timestamp=_parse_datetime(data.get("evaluation_timestamp")),
    )



# Öffentliche API
def load_forecasts() -> List[RiskForecast]:
    """
    Lädt alle gespeicherten Prognosen aus der persistenten JSON-Datei.
    """
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # robust: falls Datei leer/kaputt ist, lieber nicht crashen
    if not isinstance(raw_data, list):
        return []

    return [dict_to_forecast(item) for item in raw_data if isinstance(item, dict)]


def save_forecast(forecast: RiskForecast) -> None:
    """
    Speichert eine neue Prognose persistent.

    Bestehende Prognosen werden bewusst nicht überschrieben,
    um Nachvollziehbarkeit/Historisierung zu gewährleisten.
    """
    forecasts = load_forecasts()
    forecasts.append(forecast)
    save_all_forecasts(forecasts)


def save_all_forecasts(forecasts: List[RiskForecast]) -> None:
    """
    Speichert den vollständigen Systemzustand aller Prognosen.
    (z.B. nach Outcome-Setzung)
    """
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            [forecast_to_dict(f) for f in forecasts],
            f,
            indent=2,
            ensure_ascii=False,
        )
