"""Tests for Phase 8 — Pest & Disease Risk Engine."""

import pytest
from app.core.engine import pest_engine


def test_wheat_rust_high_risk():
    # Cool, highly humid weather during booting stage -> High Rust risk
    overall, risks = pest_engine.evaluate_pest_disease_risks(
        crop_name="Wheat",
        growth_stage="Booting",
        temp_c=15.0,
        humidity_pct=85.0,
        rainfall_mm=2.5,
        ndvi=0.82,
    )
    assert overall in ["High Risk", "Moderate Risk"]
    rust = next((r for r in risks if "Rust" in r["pest_or_disease_name"]), None)
    assert rust is not None
    assert rust["risk_level"] == "High"
    assert rust["risk_score"] >= 80
    assert "organic_control" in rust
    assert "chemical_control" in rust


def test_rice_blast_risk():
    # High humidity & rain during panicle initiation -> High Blast risk
    overall, risks = pest_engine.evaluate_pest_disease_risks(
        crop_name="Rice (Basmati)",
        growth_stage="Panicle Initiation",
        temp_c=24.0,
        humidity_pct=90.0,
        rainfall_mm=5.0,
    )
    blast = next((r for r in risks if "Blast" in r["pest_or_disease_name"]), None)
    assert blast is not None
    assert blast["risk_score"] >= 75
    assert "Tricyclazole" in blast["chemical_control"]


def test_cotton_whitefly_risk():
    # Hot, moderate humidity during squaring stage -> High Whitefly risk
    overall, risks = pest_engine.evaluate_pest_disease_risks(
        crop_name="Cotton",
        growth_stage="Squaring",
        temp_c=36.0,
        humidity_pct=55.0,
    )
    whitefly = next((r for r in risks if "Whitefly" in r["pest_or_disease_name"]), None)
    assert whitefly is not None
    assert whitefly["risk_score"] >= 70
    assert "Pyriproxyfen" in whitefly["chemical_control"]


def test_maize_fall_armyworm_risk():
    overall, risks = pest_engine.evaluate_pest_disease_risks(
        crop_name="Maize",
        growth_stage="Vegetative",
        temp_c=28.0,
        humidity_pct=60.0,
    )
    faw = next((r for r in risks if "Fall Armyworm" in r["pest_or_disease_name"]), None)
    assert faw is not None
    assert faw["category"] == "Pest"
    assert "Emamectin" in faw["chemical_control"] or "Spinetoram" in faw["chemical_control"]


def test_api_pest_risk_endpoint(authenticated_client):
    # Register farm
    farm_payload = {
        "name": "Pest Risk Test Farm",
        "district": "Multan",
        "province": "Punjab",
        "latitude": 30.15,
        "longitude": 71.52,
    }
    create_res = authenticated_client.post("/api/v1/farms/", json=farm_payload)
    assert create_res.status_code == 201
    farm_id = create_res.json()["id"]

    # Call endpoint
    res = authenticated_client.get(f"/api/v1/analytics/pest-disease-risk/{farm_id}?crop=Wheat")
    assert res.status_code == 200
    data = res.json()
    assert data["farm_id"] == farm_id
    assert data["crop_name"] == "Wheat"
    assert "overall_pest_risk" in data
    assert len(data["risks"]) >= 2
