"""
Tests for all 11 required versioned API endpoints in AgriTwin AI MVP:
- /api/v1/weather
- /api/v1/soil
- /api/v1/crops
- /api/v1/crops/recommendations
- /api/v1/crops/{crop_id}
- /api/v1/prices/{crop_id}
- /api/v1/prices/{crop_id}/history
- /api/v1/prices/{crop_id}/forecast
- /api/v1/opportunities
- /api/v1/assistant (and /api/v1/ai/explain)
- /health & /ready
"""

import pytest


def test_endpoint_weather(client):
    """Verify GET /api/v1/weather responds cleanly."""
    res = client.get("/api/v1/weather?latitude=30.81&longitude=73.45")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "data" in data


def test_endpoint_soil(client):
    """Verify GET /api/v1/soil responds cleanly."""
    res = client.get("/api/v1/soil?latitude=30.81&longitude=73.45")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "soil_physics" in data


def test_endpoint_crops_list(client):
    """Verify GET /api/v1/crops returns all supported crops."""
    res = client.get("/api/v1/crops")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["crops_count"] >= 13


def test_endpoint_crops_recommendations(client):
    """Verify GET /api/v1/crops/recommendations returns ranked recommendations."""
    res = client.get("/api/v1/crops/recommendations?province=Punjab&month=11")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data["ranked_crops"]) >= 10


def test_endpoint_crops_by_id(client):
    """Verify GET /api/v1/crops/{crop_id} returns detailed crop profile."""
    res = client.get("/api/v1/crops/WHEAT_001")
    assert res.status_code == 200
    data = res.json()
    assert data["crop_id"] == "WHEAT_001"
    assert data["crop_name"] == "Wheat"


def test_endpoint_prices_by_id(client):
    """Verify GET /api/v1/prices/{crop_id} returns current prices."""
    res = client.get("/api/v1/prices/WHEAT_001")
    assert res.status_code == 200
    data = res.json()
    assert data["crop_id"] == "WHEAT_001"
    assert "current_market_rates" in data


def test_endpoint_prices_history(client):
    """Verify GET /api/v1/prices/{crop_id}/history returns historical trend data."""
    res = client.get("/api/v1/prices/WHEAT_001/history")
    assert res.status_code == 200
    data = res.json()
    assert data["crop_id"] == "WHEAT_001"
    assert "trend_30d_pct" in data


def test_endpoint_prices_forecast(client):
    """Verify GET /api/v1/prices/{crop_id}/forecast returns 7d/14d/30d forecasts."""
    res = client.get("/api/v1/prices/WHEAT_001/forecast")
    assert res.status_code == 200
    data = res.json()
    assert data["crop_id"] == "WHEAT_001"
    assert "forecast_30d" in data


def test_endpoint_opportunities(client):
    """Verify GET /api/v1/opportunities returns general market opportunities."""
    res = client.get("/api/v1/opportunities")
    assert res.status_code == 200
    data = res.json()
    assert "opportunities" in data
    assert len(data["opportunities"]) >= 10


def test_endpoint_assistant_and_ai_explain(client, authenticated_client):
    """Verify POST /api/v1/assistant and /api/v1/ai/explain return explanations."""
    farm_res = authenticated_client.post(
        "/api/v1/farms/",
        json={"name": "Assistant Test Farm", "district": "Okara", "latitude": 30.81, "longitude": 73.45},
    )
    farm_id = farm_res.json()["id"]

    res1 = client.post("/api/v1/ai/explain", json={"farm_id": farm_id, "language": "en"})
    assert res1.status_code == 200
    assert "explanation" in res1.json()

    res2 = client.post("/api/v1/assistant", json={"farm_id": farm_id, "language": "ur"})
    assert res2.status_code == 200
    assert "explanation" in res2.json()


def test_health_and_ready_endpoints(client):
    """Verify /health and /ready endpoints respond cleanly."""
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_ready = client.get("/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "ready"

    res_api_ready = client.get("/api/v1/ready")
    assert res_api_ready.status_code == 200
    assert res_api_ready.json()["status"] == "ready"
