from datetime import datetime, timedelta

from csra_forecast.models import RiskForecast
from csra_forecast.storage import (
    save_forecast,
    load_forecasts,
)



def test_roundtrip_storage(tmp_path, monkeypatch):
    test_file = tmp_path / "forecasts.json"
    monkeypatch.setattr("csra_forecast.storage.DATA_FILE", test_file)

    f = RiskForecast.create(
        forecast_type="PT2",
        outcome_class="O2",
        event_description="Mehrere Phishing-Vorfälle",
        event_criteria="≥ 3 Incidents",
        evaluation_mode="FIXED",
        forecast_horizon_start=datetime.utcnow(),
        forecast_horizon_end=datetime.utcnow() + timedelta(days=90),
        probability_source="expert",
        probability=0.4,
        threshold_definition=">=3",
    )

    save_forecast(f)

    loaded = load_forecasts()
    assert len(loaded) == 1
    assert loaded[0].event_description == f.event_description
    assert loaded[0].threshold_definition == ">=3"
