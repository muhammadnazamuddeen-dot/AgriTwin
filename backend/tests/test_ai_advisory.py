"""Tests for Phase 9 — AI Advisory Engine."""

import pytest
from app.core.engine import agricore


@pytest.mark.asyncio
async def test_generate_recommendation_rule_based():
    ctx = agricore.FarmContext(
        farm_id=1,
        crop_name="Wheat",
        growth_stage="Booting",
        temperature_c=22.0,
        humidity_pct=75.0,
        soil_moisture_m3m3=0.10,  # Low moisture -> water alert (water score < 50)
        canal_name="Lower Bari Doab Canal",
        canal_turn_day="Thursday",
    )
    health = agricore.compute_health_score(ctx)

    rec = await agricore.generate_recommendation(ctx, health)
    assert rec.text != ""
    assert rec.text_ur is not None
    assert "آبپاشی" in rec.text_ur or "نمی" in rec.text_ur or "پانی" in rec.text_ur
    assert rec.confidence >= 0.5
    assert rec.risk_level in ["low", "moderate", "high", "critical"]


@pytest.mark.asyncio
async def test_generate_recommendation_question():
    ctx = agricore.FarmContext(
        farm_id=1,
        crop_name="Wheat",
        growth_stage="Jointing",
        temperature_c=18.0,
        humidity_pct=82.0,
        pest_risks_summary="High Risk: Yellow Rust",
    )
    health = agricore.compute_health_score(ctx)

    # Ask pest question
    rec_pest = await agricore.generate_recommendation(ctx, health, question="Should I spray for yellow rust?")
    assert "pest" in rec_pest.text.lower() or "rust" in rec_pest.text.lower() or "disease" in rec_pest.text.lower()
    assert rec_pest.text_ur is not None

    # Ask water question
    rec_water = await agricore.generate_recommendation(ctx, health, question="When to irrigate?")
    assert "irrigat" in rec_water.text.lower() or "water" in rec_water.text.lower() or "moisture" in rec_water.text.lower()


def test_api_ask_ai_endpoint(authenticated_client):
    # Register farm
    farm_payload = {
        "name": "Advisory Test Farm",
        "district": "Sahiwal",
        "province": "Punjab",
        "latitude": 30.66,
        "longitude": 73.10,
        "canal_name": "Lower Bari Doab Canal",
        "canal_turn_day": "Thursday",
        "canal_turn_time": "04:00",
    }
    create_res = authenticated_client.post("/api/v1/farms/", json=farm_payload)
    assert create_res.status_code == 201
    farm_id = create_res.json()["id"]

    # Ask AI endpoint
    ask_payload = {
        "farm_id": farm_id,
        "question": "گندم نوں کدو پانی لایا جائے؟",  # When to irrigate wheat?
    }
    res = authenticated_client.post("/api/v1/analytics/ask-ai", json=ask_payload)
    assert res.status_code == 200
    data = res.json()
    assert "recommendation" in data
    assert "reasoning" in data
    assert data["recommendation_ur"] is not None
    assert "confidence" in data
    assert "risk_level" in data
    assert data["data_summary"]["farm_id"] == farm_id
