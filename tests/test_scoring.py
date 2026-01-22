from datetime import datetime, timedelta

from csra_forecast.models import RiskForecast
from csra_forecast.scoring import (
    brier_score,
    is_brier_applicable,
)



def create_base_forecast(
    *,
    forecast_type="PT1",
    outcome_class="O1",
    probability=0.7,
):
    return RiskForecast.create(
        forecast_type=forecast_type,
        outcome_class=outcome_class,
        event_description="Testereignis",
        event_criteria="Eindeutig beobachtbar",
        evaluation_mode="FIXED",
        forecast_horizon_start=datetime.utcnow(),
        forecast_horizon_end=datetime.utcnow() + timedelta(days=30),
        probability_source="expert",
        probability=probability,
        author="Tester",
    )


def test_brier_score_basic():
    score = brier_score(0.7, 1)
    assert abs(score - 0.09) < 1e-6


def test_brier_score_zero():
    assert brier_score(0.0, 0) == 0.0


def test_brier_score_worst_case():
    assert brier_score(1.0, 0) == 1.0


def test_brier_applicable_for_pt1_o1():
    f = create_base_forecast()
    f.set_outcome(1)
    assert is_brier_applicable(f) is True


def test_brier_not_applicable_without_outcome():
    f = create_base_forecast()
    assert is_brier_applicable(f) is False


def test_brier_not_applicable_for_non_binary_forecast():
    """
    PT2 ist keine binäre Ereignisprognose → kein Brier Score
    """
    f = RiskForecast.create(
        forecast_type="PT2",
        outcome_class="O2",
        event_description="Mehrere Phishing-Vorfälle",
        event_criteria="Zählung von Incidents",
        evaluation_mode="FIXED",
        forecast_horizon_start=datetime.utcnow(),
        forecast_horizon_end=datetime.utcnow() + timedelta(days=30),
        probability_source="expert",
        probability=0.7,
        threshold_definition=">=3",
        author="Tester",
    )
    f.outcome = 1

    assert is_brier_applicable(f) is False



def test_brier_not_applicable_for_uncertain_outcome():
    f = create_base_forecast(outcome_class="O3")
    f.set_outcome(1)
    assert is_brier_applicable(f) is False


def test_brier_not_applicable_without_probability():
    f = create_base_forecast(probability=0.7)
    f.probability = None
    f.set_outcome(1)
    assert is_brier_applicable(f) is False


def test_brier_independent_of_comparison_level():
    f = create_base_forecast()
    f.comparison_level = "E1"
    f.set_outcome(1)
    assert is_brier_applicable(f) is True
