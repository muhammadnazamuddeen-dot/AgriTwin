"""Tests for Phase 6 — Satellite Intelligence & Polygon NDVI Engine."""

import datetime
import pytest
from unittest.mock import patch
from app.models import Farm, SatelliteObservation
from app.services.satellite_service import satellite_service


def test_ndvi_summary_statistics_calculation():
    """Verify mean, min, max, std, trend, and canopy health category calculations."""
    sample_series = [
        {"date": "2026-01-01", "ndvi": 0.40},
        {"date": "2026-01-15", "ndvi": 0.45},
        {"date": "2026-02-01", "ndvi": 0.55},
        {"date": "2026-02-15", "ndvi": 0.70},
        {"date": "2026-03-01", "ndvi": 0.75},
    ]

    summary = satellite_service.compute_ndvi_summary(sample_series)

    assert summary["count"] == 5
    assert summary["min"] == 0.40
    assert summary["max"] == 0.75
    assert summary["mean"] == 0.57
    assert summary["trend"] == "increasing"
    assert summary["health_category"] == "Excellent Canopy"
    assert summary["cloud_coverage_pct"] == 5.0


def test_ndvi_summary_vegetation_stress_classification():
    """Verify vegetation stress health classification for low NDVI."""
    stressed_series = [
        {"date": "2026-05-01", "ndvi": 0.35},
        {"date": "2026-05-15", "ndvi": 0.28},
        {"date": "2026-06-01", "ndvi": 0.22},
    ]

    summary = satellite_service.compute_ndvi_summary(stressed_series)
    assert summary["trend"] == "declining"
    assert summary["health_category"] in ["Vegetation Stress", "Bare Soil / Water"]


def test_fallback_timeseries_generation():
    """Verify fallback seasonal NDVI generator for Punjab coordinates."""
    series = satellite_service.generate_fallback_timeseries(lat=30.81, lon=73.45, months=12)
    assert len(series) > 10
    assert "date" in series[0]
    assert "ndvi" in series[0]
    assert 0.10 <= series[0]["ndvi"] <= 0.90


def test_satellite_stats_endpoint(authenticated_client, db_session):
    """Test GET /api/v1/satellite/farms/{farm_id}/stats endpoint."""
    farm = Farm(
        id=501,
        user_id=1,
        name="Vehari Satellite Twin",
        district="Vehari",
        province="Punjab",
        latitude=30.04,
        longitude=72.35,
        area_acres=18.0,
    )
    db_session.add(farm)
    db_session.commit()

    mock_series = [
        {"date": "2026-01-01", "ndvi": 0.45},
        {"date": "2026-02-01", "ndvi": 0.65},
    ]
    with patch("app.routers.satellite.get_ndvi_series_cached") as mock_cache:
        mock_cache.return_value = mock_series
        res = authenticated_client.get(f"/api/v1/satellite/farms/{farm.id}/stats?months=6")
        assert res.status_code == 200
        data = res.json()

        assert data["farm_id"] == farm.id
        assert data["farm_name"] == "Vehari Satellite Twin"
        assert "ndvi_mean" in data
        assert "ndvi_min" in data
        assert "ndvi_max" in data
        assert "ndvi_trend" in data
        assert "health_category" in data
        assert len(data["timeseries"]) == 2


def test_satellite_sync_and_observations_flow(authenticated_client, db_session):
    """Test POST /api/v1/satellite/farms/{farm_id}/sync and GET observations history."""
    farm = Farm(
        id=502,
        user_id=1,
        name="Kasur Satellite Sync Twin",
        district="Kasur",
        province="Punjab",
        latitude=31.11,
        longitude=74.45,
        area_acres=12.5,
    )
    db_session.add(farm)
    db_session.commit()

    mock_series = [
        {"date": "2026-01-01", "ndvi": 0.50},
        {"date": "2026-02-01", "ndvi": 0.70},
    ]
    with patch("app.routers.satellite.get_ndvi_series_cached") as mock_cache:
        mock_cache.return_value = mock_series
        # 1. Trigger Satellite Sync
        sync_res = authenticated_client.post(f"/api/v1/satellite/farms/{farm.id}/sync")
        assert sync_res.status_code == 200
        sync_data = sync_res.json()

        assert sync_data["status"] == "success"
        assert sync_data["farm_id"] == farm.id
        assert "observation_id" in sync_data

    # 2. Verify stored observation in DB history endpoint
    obs_res = authenticated_client.get(f"/api/v1/satellite/observations/{farm.id}")
    assert obs_res.status_code == 200
    records = obs_res.json()

    assert len(records) >= 1
    assert records[0]["farm_id"] == farm.id
    assert records[0]["ndvi"] > 0
