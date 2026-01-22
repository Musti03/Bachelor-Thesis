from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal, Dict, Any
import uuid


# -------------------------------------------------
# Typdefinitionen
# -------------------------------------------------

ForecastType = Literal["PT1", "PT2", "PT3", "PT4"]
OutcomeClass = Literal["O1", "O2", "O3", "O4"]
ComparisonLevel = Literal["E1", "E2", "E3"]

EvaluationMode = Literal[
    "FIXED",     # fester Zeitraum (Start/Ende)
    "OPEN",      # Start bekannt, Ende offen
    "EVENT",     # ereignisgetrieben
    "UNKNOWN",   # zeitlich unbestimmt
]

ProbabilitySource = Literal[
    "expert",    # Expertenschätzung
    "data",      # aus Daten abgeleitet
    "mixed",     # Kombination
    "derived",   # automatisch (Wizard)
    "none",      # keine explizite Wahrscheinlichkeit
]


# -------------------------------------------------
# Datenmodell
# -------------------------------------------------

@dataclass
class RiskForecast:
    """
    Kanonisches Prognoseformat der Arbeit.

    Zentrale Idee:
    - Prognosen können unterschiedlich "reif" sein (E1–E3)
    - Nicht jede Aussage ist sofort quantitativ bewertbar
    - Dennoch wird jede Prognose so dokumentiert,
      dass spätere Transformation und Evaluation möglich ist
    """

    # -----------------------------
    # Identität & Zeitstempel
    # -----------------------------
    forecast_id: str
    forecast_timestamp: datetime

    # -----------------------------
    # Typisierung
    # -----------------------------
    forecast_type: ForecastType
    outcome_class: OutcomeClass

    # -----------------------------
    # Ereignisdefinition
    # -----------------------------
    event_description: str
    event_criteria: str

    # -----------------------------
    # Evaluation / Prognosehorizont
    # -----------------------------
    evaluation_mode: EvaluationMode
    forecast_horizon_start: Optional[datetime]
    forecast_horizon_end: Optional[datetime]

    # -----------------------------
    # Wahrscheinlichkeit
    # -----------------------------
    probability_source: ProbabilitySource
    probability: Optional[float]
    probability_derivation: Optional[Dict[str, Any]] = None

    # -----------------------------
    # Transformation / Schwellen
    # -----------------------------
    threshold_definition: Optional[str] = None

    comparison_level: ComparisonLevel = "E1"

    normalization_applied: bool = False
    normalization_assumption: Optional[str] = None
    normalized_window_days: Optional[int] = None

    # -----------------------------
    # Metadaten
    # -----------------------------
    forecast_name: str = "Unbenannte Prognose"
    author: Optional[str] = None
    team: Optional[str] = None
    rationale: Optional[str] = None

    # -----------------------------
    # Bewertung (ex post)
    # -----------------------------
    outcome: Optional[int] = None
    evaluation_timestamp: Optional[datetime] = None

    # -------------------------------------------------
    # Factory-Methode
    # -------------------------------------------------
    @classmethod
    def create(
        cls,
        *,
        forecast_type: ForecastType,
        outcome_class: OutcomeClass,
        event_description: str,
        event_criteria: str,

        # 🔽 Defaults für Rückwärtskompatibilität
        evaluation_mode: EvaluationMode = "FIXED",
        forecast_horizon_start: Optional[datetime] = None,
        forecast_horizon_end: Optional[datetime] = None,

        probability_source: ProbabilitySource = "expert",
        probability: Optional[float] = None,
        probability_derivation: Optional[Dict[str, Any]] = None,

        forecast_name: Optional[str] = None,
        author: Optional[str] = None,
        team: Optional[str] = None,
        rationale: Optional[str] = None,
        threshold_definition: Optional[str] = None,

        normalization_applied: bool = False,
        normalization_assumption: Optional[str] = None,
        normalized_window_days: Optional[int] = None,
    ) -> "RiskForecast":

        # -----------------------------
        # Basisvalidierung
        # -----------------------------
        if not (event_description or "").strip():
            raise ValueError("event_description darf nicht leer sein.")
        if not (event_criteria or "").strip():
            raise ValueError("event_criteria darf nicht leer sein.")

        # -----------------------------
        # Horizont-Logik
        # -----------------------------
        if evaluation_mode == "FIXED":
            if forecast_horizon_start is None or forecast_horizon_end is None:
                raise ValueError("FIXED benötigt Start- und Enddatum.")
            if forecast_horizon_end < forecast_horizon_start:
                raise ValueError("forecast_horizon_end muss >= forecast_horizon_start sein.")

        elif evaluation_mode == "OPEN":
            if forecast_horizon_start is None:
                raise ValueError("OPEN benötigt mindestens forecast_horizon_start.")
            forecast_horizon_end = None

        elif evaluation_mode in ("EVENT", "UNKNOWN"):
            forecast_horizon_start = forecast_horizon_start
            forecast_horizon_end = None

        # -----------------------------
        # Wahrscheinlichkeit
        # -----------------------------
        if probability_source == "none":
            probability = None

        if probability is not None:
            probability = float(probability)
            if not (0.0 <= probability <= 1.0):
                raise ValueError("probability muss im Bereich [0,1] liegen.")

        # -----------------------------
        # Schwellenlogik
        # -----------------------------
        if forecast_type == "PT2" or outcome_class == "O2":
            if not (threshold_definition or "").strip():
                raise ValueError("PT2/O2 benötigt eine threshold_definition.")

        # -----------------------------
        # Vergleichsebene
        # -----------------------------
        comparison_level: ComparisonLevel = "E2" if normalization_applied else "E1"

        return cls(
            forecast_id=str(uuid.uuid4()),
            forecast_timestamp=datetime.utcnow(),

            forecast_type=forecast_type,
            outcome_class=outcome_class,

            event_description=event_description.strip(),
            event_criteria=event_criteria.strip(),

            evaluation_mode=evaluation_mode,
            forecast_horizon_start=forecast_horizon_start,
            forecast_horizon_end=forecast_horizon_end,

            probability_source=probability_source,
            probability=probability,
            probability_derivation=probability_derivation,

            threshold_definition=(
                threshold_definition.strip()
                if isinstance(threshold_definition, str) and threshold_definition.strip()
                else None
            ),

            comparison_level=comparison_level,
            normalization_applied=bool(normalization_applied),
            normalization_assumption=normalization_assumption,
            normalized_window_days=normalized_window_days,

            forecast_name=(forecast_name or "").strip() or "Unbenannte Prognose",
            author=(author or "").strip() or None,
            team=(team or "").strip() or None,
            rationale=(rationale or "").strip() or None,

            outcome=None,
            evaluation_timestamp=None,
        )

    # -------------------------------------------------
    # Outcome setzen
    # -------------------------------------------------
    def set_outcome(self, outcome: int) -> None:
        if outcome not in (0, 1):
            raise ValueError("outcome muss 0 oder 1 sein.")
        self.outcome = outcome
        self.evaluation_timestamp = datetime.utcnow()
