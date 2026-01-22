import pytest
from datetime import datetime, timedelta

from csra_forecast.models import RiskForecast


def test_create_valid_fixed_forecast():
    f = RiskForecast.create(
        forecast_type="PT1",
        outcome_class="O1",
        event_description="Ransomware-Angriff auf System X",
        event_criteria="Incident im Ticketsystem",
        evaluation_mode="FIXED",
        forecast_horizon_start=datetime.utcnow(),
        forecast_horizon_end=datetime.utcnow() + timedelta(days=30),
        probability_source="expert",
        probability=0.3,
        author="Analyst A",
    )

    assert f.forecast_type == "PT1"
    assert f.outcome_class == "O1"
    assert f.probability == 0.3
    assert f.evaluation_mode == "FIXED"


def test_invalid_probability_raises():
    with pytest.raises(ValueError):
        RiskForecast.create(
            forecast_type="PT1",
            outcome_class="O1",
            event_description="Test",
            event_criteria="Test",
            evaluation_mode="FIXED",
            forecast_horizon_start=datetime.utcnow(),
            forecast_horizon_end=datetime.utcnow() + timedelta(days=1),
            probability_source="expert",
            probability=1.5,
        )


def test_invalid_horizon_order_raises():
    with pytest.raises(ValueError):
        RiskForecast.create(
            forecast_type="PT1",
            outcome_class="O1",
            event_description="Test",
            event_criteria="Test",
            evaluation_mode="FIXED",
            forecast_horizon_start=datetime.utcnow(),
            forecast_horizon_end=datetime.utcnow() - timedelta(days=1),
            probability_source="expert",
            probability=0.2,
        )


def test_open_horizon_allows_missing_end():
    f = RiskForecast.create(
        forecast_type="PT1",
        outcome_class="O1",
        event_description="Offene Prognose",
        event_criteria="Incident",
        evaluation_mode="OPEN",
        forecast_horizon_start=datetime.utcnow(),
        forecast_horizon_end=None,
        probability_source="expert",
        probability=0.4,
    )

    assert f.forecast_horizon_end is None
    assert f.evaluation_mode == "OPEN"


def test_unknown_horizon_allows_none():
    f = RiskForecast.create(
        forecast_type="PT4",
        outcome_class="O4",
        event_description="Qualitative Einschätzung",
        event_criteria="Subjektiv",
        evaluation_mode="UNKNOWN",
        forecast_horizon_start=None,
        forecast_horizon_end=None,
        probability_source="none",
        probability=None,
    )

    assert f.probability is None
    assert f.evaluation_mode == "UNKNOWN"


def test_pt2_requires_threshold():
    with pytest.raises(ValueError):
        RiskForecast.create(
            forecast_type="PT2",
            outcome_class="O2",
            event_description="Mehrere Vorfälle",
            event_criteria="Incidents",
            evaluation_mode="FIXED",
            forecast_horizon_start=datetime.utcnow(),
            forecast_horizon_end=datetime.utcnow() + timedelta(days=90),
            probability_source="expert",
            probability=0.5,
        )
