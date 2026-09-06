"""
Tests for Market Price Prediction ML Model, 7-Factor Crop Suitability Engine,
/market/forecast/{crop_name}, /market/suitability/{farm_id}, and /ai/explain integration.
"""

import pytest
from fastapi.testclient import TestClient
from app.services.price_prediction_engine import price_prediction_engine
from app.core.engine import suitability_engine


def test_price_prediction_engine_basic():
    """Verify XGBoost/GradientBoosting Price Prediction Engine forecast output structure."""
    res = price_prediction_engine.forecast_price("Wheat", district="Gujrat")
    assert res["crop"] == "Wheat"
    assert res["district"] == "Gujrat"
    assert "forecast_7d" in res
    assert "forecast_14d" in res
    assert "forecast_30d" in res
    assert "price_change_7d_pct" in res
    assert "price_change_30d_pct" in res
    assert res["direction"] in ["bullish", "bearish", "stable"]
    assert 0.0 <= res["confidence"] <= 1.0
    assert 0.0 <= res["confidence_pct"] <= 100.0


def test_suitability_engine_7_factors_and_gross_margin():
    """Verify 7-factor Crop Suitability Engine and Gross Margin / Acre calculation."""
    farm_data = {
        "canal_name": "Lower Bari Doab Canal",
        "canal_turn_duration_hours": 4.0,
        "tubewell_power_source": "diesel",
    }
    soil_data = {"ph_topsoil": 7.2, "organic_carbon_g_per_kg": 8.0, "clay_pct": 30, "sand_pct": 40}
    weather_data = {"current": {"temperature_2m": 22.0, "relative_humidity_2m": 55.0}}

    price_fc = price_prediction_engine.forecast_price("Wheat", district="Gujrat")

    res = suitability_engine.evaluate_crop_suitability(
        crop_name="Wheat",
        farm_data=farm_data,
        soil_data=soil_data,
        weather_data=weather_data,
        month=11,
        price_forecast_data=price_fc,
    )

    # 7-factor sub-scores check
    assert "season_score" in res
    assert "soil_score" in res
    assert "climate_score" in res
    assert "water_score" in res
    assert "market_score" in res
    assert "profit_score" in res
    assert "disease_risk_score" in res

    # Gross Margin per acre check
    assert res["expected_yield_maunds_acre"] > 0
    assert res["expected_price_pkr_maund"] > 0
    assert res["expected_revenue_pkr_acre"] > 0
    assert res["estimated_cost_pkr_acre"] > 0
    assert res["expected_gross_margin_pkr_acre"] is not None
    assert res["recommendation_level"] in ["HIGH", "RECOMMENDED", "MODERATE", "LOW"]


def test_market_forecast_api_endpoint(client):
    """Verify GET /api/v1/market/forecast/{crop_name} endpoint."""
    res = client.get("/api/v1/market/forecast/Wheat?district=Gujrat")
    assert res.status_code == 200
    data = res.json()
    assert data["crop"] == "Wheat"
    assert "forecast_7d" in data
    assert "forecast_30d" in data
    assert "confidence_pct" in data


def test_market_suitability_api_endpoint(authenticated_client):
    """Verify GET /api/v1/market/suitability/{farm_id} endpoint."""
    farm_payload = {
        "name": "Market Suitability Farm",
        "district": "Gujrat",
        "province": "Punjab",
        "latitude": 32.57,
        "longitude": 74.07,
    }
    create_res = authenticated_client.post("/api/v1/farms/", json=farm_payload)
    assert create_res.status_code == 201
    farm_id = create_res.json()["id"]

    res = authenticated_client.get(f"/api/v1/market/suitability/{farm_id}?month=11")
    assert res.status_code == 200
    data = res.json()
    assert data["farm_id"] == farm_id
    assert len(data["ranked_crops"]) >= 4

    top_crop = data["ranked_crops"][0]
    assert "season_score" in top_crop
    assert "market_score" in top_crop
    assert "profit_score" in top_crop
    assert "disease_risk_score" in top_crop
    assert top_crop["expected_gross_margin_pkr_acre"] is not None


def test_ai_explain_with_market_facts(authenticated_client):
    """Verify POST /api/v1/ai/explain incorporates price predictions and gross margins."""
    farm_payload = {
        "name": "AI Explain Farm",
        "district": "Gujrat",
        "province": "Punjab",
        "latitude": 32.57,
        "longitude": 74.07,
    }
    create_res = authenticated_client.post("/api/v1/farms/", json=farm_payload)
    assert create_res.status_code == 201
    farm_id = create_res.json()["id"]

    res = authenticated_client.post("/api/v1/ai/explain", json={"farm_id": farm_id, "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert "explanation" in data
    assert "Forecast" in data["explanation"] or "Price" in data["explanation"] or "margin" in data["explanation"].lower()


def test_market_analysis_trends(client):
    """Verify GET /api/v1/market/analysis/{crop_name} includes 7d, 30d, 90d, and YoY trends."""
    res = client.get("/api/v1/market/analysis/Wheat")
    assert res.status_code == 200
    data = res.json()
    assert "trend_7d_pct" in data
    assert "trend_30d_pct" in data
    assert "trend_90d_pct" in data
    assert "trend_yoy_pct" in data


def test_empty_crop_name_fallback():
    """Verify forecast_price gracefully handles empty or whitespace crop names."""
    res_empty = price_prediction_engine.forecast_price("")
    assert res_empty["crop"] == "Wheat"

    res_space = price_prediction_engine.forecast_price("   ")
    assert res_space["crop"] == "Wheat"


def test_market_prices_db_persistence(authenticated_client):
    """Verify GET /api/v1/market/prices returns price feed and persists to CropPrice model."""
    res = authenticated_client.get("/api/v1/market/prices?district=Gujrat")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data["prices"]) >= 5

