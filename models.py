from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal
import uuid


@dataclass
class RiskForecast:
    """
    Repräsentiert eine überprüfbare Risiko-Prognose im CSRA-Kontext.

    Die Klasse bildet das kanonische Prognoseformat dieser Arbeit ab.
    Sie ist bewusst rein deklarativ und enthält keine automatische
    Bewertungs- oder Transformationslogik.
    """

    # -----------------------------
    # Prognosekern (immer vorhanden)
    # -----------------------------

    forecast_id: str
    forecast_timestamp: datetime

    # Prognosetyp (PT1–PT4)
    forecast_type: Literal["PT1", "PT2", "PT3", "PT4"]

    # Ereignisdefinition
    event_description: str
    event_criteria: str

    # Outcome-Operationalisierung
    outcome_class: Literal["O1", "O2", "O3", "O4"]

    # Prognosehorizont
    forecast_horizon_start: datetime
    forecast_horizon_end: datetime

    # Eintrittswahrscheinlichkeit
    probability: Optional[float]

    # ------------------------------------
    # Optionale Metadaten (nicht bewertungsrelevant)
    # ------------------------------------

    forecast_name: str = "Unbenannte Prognose"
    author: Optional[str] = None
    team: Optional[str] = None
    rationale: Optional[str] = None

    # ------------------------------------
    # Transformations- & Vergleichsmetadaten
    # ------------------------------------

    # Vergleichsebene gemäß Option-2-Logik
    # E1: strukturell
    # E2: transformiert
    # E3: quantitativ bewertbar
    comparison_level: Literal["E1", "E2", "E3"] = "E1"

    # Dokumentation von Transformationsannahmen (falls zutreffend)
    normalization_applied: bool = False
    normalization_assumption: Optional[str] = None

    threshold_definition: Optional[str] = None

    # -----------------------------
    # Bewertung (ex post)
    # -----------------------------

    outcome: Optional[int] = None  # 0 = nicht eingetreten, 1 = eingetreten
    evaluation_timestamp: Optional[datetime] = None

    # -----------------------------
    # Factory-Methode
    # -----------------------------

    @classmethod
    def create(
        cls,
        *,
        forecast_type: Literal["PT1", "PT2", "PT3", "PT4"],
        outcome_class: Literal["O1", "O2", "O3", "O4"],
        event_description: str,
        event_criteria: str,
        forecast_horizon_start: datetime,
        forecast_horizon_end: datetime,
        probability: float,
        forecast_name: Optional[str] = None,
        author: Optional[str] = None,
        team: Optional[str] = None,
        rationale: Optional[str] = None,
        threshold_definition: Optional[str] = None,
        normalization_applied: bool = False,
        normalization_assumption: Optional[str] = None,
    ) -> "RiskForecast":
        """
        Erstellt eine neue Risiko-Prognose mit automatisch erzeugter ID
        und Prognosezeitpunkt.

        Enthält nur minimale Validierungen auf strukturelle Korrektheit.
        """

        if not event_description.strip():
            raise ValueError("event_description darf nicht leer sein.")
        if not event_criteria.strip():
            raise ValueError("event_criteria darf nicht leer sein.")
        if forecast_horizon_end < forecast_horizon_start:
            raise ValueError("forecast_horizon_end muss >= forecast_horizon_start sein.")
        if not (0.0 <= probability <= 1.0):
            raise ValueError("probability muss im Bereich [0,1] liegen.")

        return cls(
            forecast_id=str(uuid.uuid4()),
            forecast_timestamp=datetime.utcnow(),
            forecast_type=forecast_type,
            event_description=event_description.strip(),
            event_criteria=event_criteria.strip(),
            outcome_class=outcome_class,
            forecast_horizon_start=forecast_horizon_start,
            forecast_horizon_end=forecast_horizon_end,
            probability=float(probability),
            forecast_name=(forecast_name or "").strip() or "Unbenannte Prognose",
            author=(author or "").strip() or None,
            team=(team or "").strip() or None,
            rationale=(rationale or "").strip() or None,
            comparison_level = "E2" if normalization_applied else "E1",
            normalization_applied=normalization_applied,
            normalization_assumption=normalization_assumption,
            threshold_definition=threshold_definition,
            outcome=None,
            evaluation_timestamp=None,
        )
