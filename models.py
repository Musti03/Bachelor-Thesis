from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class RiskForecast:
    forecast_id: str

    # Metadaten
    author: str
    team: Optional[str]

    # Ereignisdefinition
    event_description: str
    event_criteria: str

    # Zeit
    forecast_timestamp: datetime
    forecast_horizon_start: datetime
    forecast_horizon_end: datetime

    # Prognose
    probability: float

    # Kontext
    rationale: Optional[str] = None

    # Bewertung
    outcome: Optional[int] = None
    evaluation_timestamp: Optional[datetime] = None

    @staticmethod
    def create(
        author: str,
        team: Optional[str],
        event_description: str,
        event_criteria: str,
        forecast_horizon_start: datetime,
        forecast_horizon_end: datetime,
        probability: float,
        rationale: Optional[str] = None,
    ) -> "RiskForecast":
        return RiskForecast(
            forecast_id=str(uuid.uuid4()),
            author=author,
            team=team,
            event_description=event_description,
            event_criteria=event_criteria,
            forecast_timestamp=datetime.utcnow(),
            forecast_horizon_start=forecast_horizon_start,
            forecast_horizon_end=forecast_horizon_end,
            probability=probability,
            rationale=rationale,
        )
