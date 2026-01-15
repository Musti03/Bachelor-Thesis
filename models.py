from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class RiskForecast:
    """
    Repräsentiert eine überprüfbare Risiko-Prognose im CSRA-Kontext.

    Idee: Binäres, beobachtbares Ereignis (tritt ein / tritt nicht ein)
    innerhalb eines klar definierten Prognosehorizonts.
    """

    # Identifikation & Kernfelder (bewertungsrelevant)
    forecast_id: str
    event_description: str
    event_criteria: str
    forecast_timestamp: datetime
    forecast_horizon_start: datetime
    forecast_horizon_end: datetime
    probability: float

    # Optionale Metadaten (nicht bewertungsrelevant)
    forecast_name: str = "Unbenannte Prognose"
    author: Optional[str] = None
    team: Optional[str] = None
    rationale: Optional[str] = None

    # Bewertung
    outcome: Optional[int] = None  # 0/1
    evaluation_timestamp: Optional[datetime] = None

    # Factory-Methode
    @classmethod
    def create(
        cls,
        *,
        event_description: str,
        event_criteria: str,
        forecast_horizon_start: datetime,
        forecast_horizon_end: datetime,
        probability: float,
        forecast_name: Optional[str] = None,
        author: Optional[str] = None,
        team: Optional[str] = None,
        rationale: Optional[str] = None,
    ) -> "RiskForecast":
        """
        Erstellt eine neue Risiko-Prognose mit automatisch erzeugter ID
        und Prognosezeitpunkt.

        Enthält minimale Validierungen, damit nur "saubere" Prognosen
        gespeichert werden können.
        """

        if not event_description.strip():
            raise ValueError("event_description darf nicht leer sein.")
        if not event_criteria.strip():
            raise ValueError("event_criteria darf nicht leer sein.")

        if forecast_horizon_end < forecast_horizon_start:
            raise ValueError("forecast_horizon_end muss >= forecast_horizon_start sein.")

        if not (0.0 <= probability <= 1.0):
            raise ValueError("probability muss im Bereich [0,1] liegen.")

        name = (forecast_name or "").strip() or "Unbenannte Prognose"
        auth = (author or "").strip() or None
        tm = (team or "").strip() or None
        rat = (rationale or "").strip() or None

        return cls(
            forecast_id=str(uuid.uuid4()),
            forecast_name=name,
            author=auth,
            team=tm,
            event_description=event_description.strip(),
            event_criteria=event_criteria.strip(),
            forecast_timestamp=datetime.utcnow(),
            forecast_horizon_start=forecast_horizon_start,
            forecast_horizon_end=forecast_horizon_end,
            probability=float(probability),
            rationale=rat,
            outcome=None,
            evaluation_timestamp=None,
        )

    def set_outcome(self, outcome: int) -> None:
        """
        Setzt den Ereignisausgang (0/1) und den Bewertungszeitpunkt.
        """
        if outcome not in (0, 1):
            raise ValueError("outcome muss 0 oder 1 sein.")
        self.outcome = outcome
        self.evaluation_timestamp = datetime.utcnow()
