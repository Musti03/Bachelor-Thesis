import json
from pathlib import Path
from typing import List
from datetime import datetime

from models import RiskForecast

# Persistenter Speicher (lokale Datei)
DATA_FILE = Path("forecasts.json")


def _serialize_datetime(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def forecast_to_dict(forecast: RiskForecast) -> dict:
    return {
        "forecast_id": forecast.forecast_id,
        "author": forecast.author,
        "team": forecast.team,
        "event_description": forecast.event_description,
        "event_criteria": forecast.event_criteria,
        "forecast_timestamp": _serialize_datetime(forecast.forecast_timestamp),
        "forecast_horizon_start": _serialize_datetime(forecast.forecast_horizon_start),
        "forecast_horizon_end": _serialize_datetime(forecast.forecast_horizon_end),
        "probability": forecast.probability,
        "rationale": forecast.rationale,
        "outcome": forecast.outcome,
        "evaluation_timestamp": _serialize_datetime(forecast.evaluation_timestamp),
    }


def dict_to_forecast(data: dict) -> RiskForecast:
    return RiskForecast(
        forecast_id=data["forecast_id"],
        author=data.get("author", "unbekannt"),
        team=data.get("team"),
        event_description=data["event_description"],
        event_criteria=data["event_criteria"],
        forecast_timestamp=datetime.fromisoformat(data["forecast_timestamp"]),
        forecast_horizon_start=datetime.fromisoformat(data["forecast_horizon_start"]),
        forecast_horizon_end=datetime.fromisoformat(data["forecast_horizon_end"]),
        probability=data["probability"],
        rationale=data.get("rationale"),
        outcome=data.get("outcome"),
        evaluation_timestamp=(
            datetime.fromisoformat(data["evaluation_timestamp"])
            if data.get("evaluation_timestamp")
            else None
        ),
    )



def load_forecasts() -> List[RiskForecast]:
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)

    return [dict_to_forecast(item) for item in raw_data]


def save_forecast(forecast: RiskForecast) -> None:
    """
    Speichert eine NEUE Prognose.
    Bestehende Prognosen bleiben unverändert.
    """
    forecasts = load_forecasts()
    forecasts.append(forecast)
    save_all_forecasts(forecasts)


def save_all_forecasts(forecasts: List[RiskForecast]) -> None:
    """
    Speichert den vollständigen Systemzustand aller Prognosen.
    Wird z. B. nach der Bewertung (Outcome-Setzung) verwendet.
    """
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            [forecast_to_dict(f) for f in forecasts],
            f,
            indent=2,
            ensure_ascii=False,
        )
