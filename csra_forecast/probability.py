from typing import Dict, Optional


def derive_probability_from_factors(
    *,
    base_rate: float,
    exposure: float,
    control_strength: float,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """
    Leitet eine Eintrittswahrscheinlichkeit aus mehreren Einflussfaktoren ab.

    Diese Funktion implementiert eine bewusst einfache, transparente
    und erklärbare Ableitungslogik (kein ML, kein Black Box Modell).

    Parameter
    ----------
    base_rate : float
        Grundwahrscheinlichkeit des Ereignisses (z. B. Branchenbasisrate).
    exposure : float
        Exposition / Angriffsfläche (0 = keine, 1 = maximal).
    control_strength : float
        Wirksamkeit der Kontrollen (0 = keine, 1 = sehr stark).
    weights : dict, optional
        Gewichtung der Faktoren (Standard = gleichgewichtet).

    Returns
    -------
    dict
        Enthält:
        - result_probability: float
        - normalized_inputs: dict
        - applied_weights: dict
        - explanation: str
    """

    # ----------------------------
    # Validierung
    # ----------------------------
    for name, value in {
        "base_rate": base_rate,
        "exposure": exposure,
        "control_strength": control_strength,
    }.items():
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"{name} muss im Bereich [0,1] liegen.")

    # ----------------------------
    # Standard-Gewichte
    # ----------------------------
    if weights is None:
        weights = {
            "base_rate": 0.4,
            "exposure": 0.4,
            "control_strength": 0.2,
        }

    weight_sum = sum(weights.values())
    if abs(weight_sum - 1.0) > 1e-6:
        raise ValueError("Gewichte müssen in Summe 1.0 ergeben.")

    # ----------------------------
    # Logik
    # ----------------------------
    # Kontrollen wirken risikomindernd → invertieren
    control_effect = 1.0 - control_strength

    raw_score = (
        weights["base_rate"] * base_rate +
        weights["exposure"] * exposure +
        weights["control_strength"] * control_effect
    )

    # Sicherheitshalber clampen
    result_probability = max(0.0, min(1.0, raw_score))

    # ----------------------------
    # Rückgabe mit Dokumentation
    # ----------------------------
    return {
        "result_probability": round(result_probability, 4),
        "normalized_inputs": {
            "base_rate": base_rate,
            "exposure": exposure,
            "control_strength": control_strength,
        },
        "applied_weights": weights,
        "explanation": (
            "Die Wahrscheinlichkeit wurde als gewichtete Kombination "
            "aus Basisrate, Exposition und inverser Kontrollstärke abgeleitet. "
            "Die Ableitung ist heuristisch, transparent und nachvollziehbar."
        ),
    }
