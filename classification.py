from typing import Tuple, Literal


ForecastType = Literal["PT1", "PT2", "PT3", "PT4"]
OutcomeClass = Literal["O1", "O2", "O3", "O4"]


def classify_forecast(
    statement_type: str,
    observability: str,
) -> Tuple[ForecastType, OutcomeClass]:
    """
    Leitet Prognosetyp (PT) und Outcome-Klasse (O)
    aus strukturierten Vorfragen ab.

    Diese Funktion implementiert die konzeptionelle
    Klassifikationslogik der Arbeit.
    """

    # Prognosetyp ableiten
    if statement_type == "Ereignis tritt ein / tritt nicht ein":
        forecast_type = "PT1"
    elif statement_type == "Ereignis tritt mehrfach auf (Häufigkeit)":
        forecast_type = "PT2"
    elif statement_type == "Ereignis möglicherweise / unklar":
        forecast_type = "PT3"
    else:
        forecast_type = "PT4"

    # Outcome-Klasse ableiten
    if observability == "Eindeutig feststellbar (ja / nein)":
        outcome_class = "O1"
    elif observability == "Über Zählung / Anzahl von Vorfällen":
        outcome_class = "O2"
    elif observability == "Mit Unsicherheit / Interpretationsspielraum":
        outcome_class = "O3"
    else:
        outcome_class = "O4"

    return forecast_type, outcome_class
