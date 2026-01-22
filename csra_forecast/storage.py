import json
from pathlib import Path
from typing import List, Optional, Any, Dict
from datetime import datetime

from csra_forecast.models import RiskForecast


DATA_FILE = Path("forecasts.json")


def _serialize_datetime(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def forecast_to_dict(f: RiskForecast) -> Dict[str, Any]:
    return {
        "forecast_id": f.forecast_id,
        "forecast_timestamp": _serialize_datetime(f.forecast_timestamp),

        "forecast_type": f.forecast_type,
        "outcome_class": f.outcome_class,

        "event_description": f.event_description,
        "event_criteria": f.event_criteria,

        "evaluation_mode": f.evaluation_mode,
        "forecast_horizon_start": _serialize_datetime(f.forecast_horizon_start),
        "forecast_horizon_end": _serialize_datetime(f.forecast_horizon_end),

        "probability_source": f.probability_source,
        "probability": f.probability,
        "probability_derivation": f.probability_derivation,

        "threshold_definition": f.threshold_definition,

        "comparison_level": f.comparison_level,
        "normalization_applied": f.normalization_applied,
        "normalization_assumption": f.normalization_assumption,
        "normalized_window_days": f.normalized_window_days,

        "forecast_name": f.forecast_name,
        "author": f.author,
        "team": f.team,
        "rationale": f.rationale,

        "outcome": f.outcome,
        "evaluation_timestamp": _serialize_datetime(f.evaluation_timestamp),
    }


def dict_to_forecast(data: Dict[str, Any]) -> RiskForecast:
    """
    Backward compatible:
    - alte Versionen hatten horizon immer
    - alte Versionen hatten probability immer (float)
    """

    raw_name = data.get("forecast_name") or data.get("forecast_title")
    forecast_name = (raw_name or "").strip() or "Unbenannte Prognose"

    # horizon fallback
    evaluation_mode = data.get("evaluation_mode")
    if evaluation_mode not in ("FIXED", "OPEN", "EVENT", "UNKNOWN"):
        # alte Daten => FIXED annehmen, wenn horizon vorhanden
        evaluation_mode = "FIXED"

    p = data.get("probability")
    probability = float(p) if p is not None else None

    return RiskForecast(
        forecast_id=data["forecast_id"],
        forecast_timestamp=_parse_datetime(data.get("forecast_timestamp")) or datetime.utcnow(),

        forecast_type=data.get("forecast_type", "PT1"),
        outcome_class=data.get("outcome_class", "O1"),

        event_description=(data.get("event_description") or "").strip(),
        event_criteria=(data.get("event_criteria") or "").strip(),

        evaluation_mode=evaluation_mode,
        forecast_horizon_start=_parse_datetime(data.get("forecast_horizon_start")),
        forecast_horizon_end=_parse_datetime(data.get("forecast_horizon_end")),

        probability_source=data.get("probability_source", "expert"),
        probability=probability,
        probability_derivation=data.get("probability_derivation"),

        threshold_definition=data.get("threshold_definition"),

        comparison_level=data.get("comparison_level", "E1"),
        normalization_applied=bool(data.get("normalization_applied", False)),
        normalization_assumption=data.get("normalization_assumption"),
        normalized_window_days=data.get("normalized_window_days"),

        forecast_name=forecast_name,
        author=(data.get("author") or "").strip() or None,
        team=(data.get("team") or "").strip() or None,
        rationale=(data.get("rationale") or "").strip() or None,

        outcome=int(data["outcome"]) if data.get("outcome") in (0, 1, "0", "1") else None,
        evaluation_timestamp=_parse_datetime(data.get("evaluation_timestamp")),
    )


def load_forecasts() -> List[RiskForecast]:
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        return []
    return [dict_to_forecast(x) for x in raw if isinstance(x, dict)]


def save_all_forecasts(forecasts: List[RiskForecast]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump([forecast_to_dict(x) for x in forecasts], f, indent=2, ensure_ascii=False)


def save_forecast(forecast: RiskForecast) -> None:
    forecasts = load_forecasts()
    forecasts.append(forecast)
    save_all_forecasts(forecasts)
