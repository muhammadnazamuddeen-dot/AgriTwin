"""
Comprehensive pytest suite for Decoupled Crop Recommendation Engine & Crop Price Intelligence Engine.
Tests:
- Permanent Crop ID Key System (13 crops: WHEAT_001, RICE_001, RICE_COARSE_001, COTTON_001, etc.)
- 5 Agricultural Zones of Pakistan (Punjab, Sindh, KPK, Balochistan, AJK/GB)
- Window metrics (days_until_window, days_remaining_in_window, days_since_window)
- GET /api/v1/crops/recommendations (decoupled agronomic recommendations)
- GET /api/v1/prices/{crop_id} (current/historical market prices)
- GET /api/v1/prices/{crop_id}/forecast (7d, 14d, 30d predictions)
- GET /api/v1/opportunities/{farm_id} (combined Opportunity Score)
- Database ORM models CropMarketPrice and CropPricePrediction
"""

import datetime
import pytest
from app.core.engine.crop_knowledge import (
    CROP_ID_MAP,
    AGRICULTURAL_ZONES,
    REGION_PLANTING_WINDOWS,
    get_crop_id,
    get_crop_name,
)
from app.core.engine import suitability_engine
from app.models import CropMarketPrice, CropPricePrediction


def test_permanent_crop_id_key_system():
    """Verify all 13 permanent crop IDs match standard crop names."""
    expected_ids = [
        "WHEAT_001",
        "RICE_001",
        "RICE_COARSE_001",
        "COTTON_001",
        "MAIZE_001",
        "SUGARCANE_001",
        "POTATO_001",
        "CHICKPEA_001",
        "CANOLA_001",
        "SUNFLOWER_001",
        "BARLEY_001",
        "LENTIL_001",
        "PEAS_001",
    ]
    for cid in expected_ids:
        assert cid in CROP_ID_MAP
        cname = get_crop_name(cid)
        assert get_crop_id(cname) == cid


def test_agricultural_zones_and_regional_windows():
    """Verify 5 agricultural zones of Pakistan and region-specific planting window calculations."""
    for zone in ["Punjab", "Sindh", "KPK", "Balochistan", "AJK/GB"]:
        assert zone in AGRICULTURAL_ZONES
        pw_res = suitability_engine.calculate_planting_window_status(
            "Wheat", ref_date=datetime.date(2026, 11, 10), province=zone
        )
        assert pw_res.score >= 80
        assert pw_res.status == "PLANT NOW 🟢"


def test_exact_window_calculations_days():
    """Verify days_until_window, days_remaining_in_window, and days_since_window calculations."""
    # Sept 6, 2026: before Wheat planting window (Oct 15 - Dec 15 in Punjab)
    sept_6 = datetime.date(2026, 9, 6)
    pw_before = suitability_engine.calculate_planting_window_status("Wheat", ref_date=sept_6, province="Punjab")
    assert pw_before.days_until_window > 0
    assert pw_before.days_remaining_in_window == 0

    # Nov 15, 2026: inside Wheat planting window
    nov_15 = datetime.date(2026, 11, 15)
    pw_inside = suitability_engine.calculate_planting_window_status("Wheat", ref_date=nov_15, province="Punjab")
    assert pw_inside.days_until_window == 0
    assert pw_inside.days_remaining_in_window > 0
    assert pw_inside.days_since_window == 0
    assert pw_inside.status == "PLANT NOW 🟢"

    # Dec 25, 2026: past Wheat planting window
    dec_25 = datetime.date(2026, 12, 25)
    pw_past = suitability_engine.calculate_planting_window_status("Wheat", ref_date=dec_25, province="Punjab")
    assert pw_past.days_since_window > 0


def test_crops_recommendations_decoupled_api(client):
    """Verify GET /api/v1/crops/recommendations returns pure agronomic recommendations without requiring price data."""
    res = client.get("/api/v1/crops/recommendations?province=Punjab&month=11")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["province"] == "Punjab"
    assert len(data["ranked_crops"]) >= 10

    top_crop = data["ranked_crops"][0]
    assert "crop_id" in top_crop
    assert "status_code" in top_crop
    assert "days_until_window" in top_crop
    assert "days_remaining_in_window" in top_crop
    assert "days_since_window" in top_crop
    assert "season_score" in top_crop
    assert "soil_score" in top_crop
    assert "climate_score" in top_crop
    assert "water_score" in top_crop
    assert "disease_risk_score" in top_crop
    assert "yield_score" in top_crop
    assert "timeline" in top_crop
    assert "todays_farm_action" in top_crop


def test_prices_by_crop_id_api(client):
    """Verify GET /api/v1/prices/{crop_id} returns market prices by crop_id."""
    res = client.get("/api/v1/prices/WHEAT_001?district=Gujrat")
    assert res.status_code == 200
    data = res.json()
    assert data["crop_id"] == "WHEAT_001"
    assert data["crop_name"] == "Wheat"
    assert "current_market_rates" in data
    assert "market_analysis" in data


def test_prices_forecast_by_crop_id_api(client):
    """Verify GET /api/v1/prices/{crop_id}/forecast returns 7d, 14d, 30d forecasts by crop_id."""
    res = client.get("/api/v1/prices/WHEAT_001/forecast?district=Gujrat")
    assert res.status_code == 200
    data = res.json()
    assert data["crop_id"] == "WHEAT_001"
    assert data["crop_name"] == "Wheat"
    assert "forecast_7d" in data
    assert "forecast_14d" in data
    assert "forecast_30d" in data
    assert "direction" in data
    assert "confidence_pct" in data


def test_opportunities_combines_suitability_and_market(authenticated_client):
    """Verify GET /api/v1/opportunities/{farm_id} combines Suitability + Market Outlook into Opportunity Score (0-100)."""
    farm_payload = {
        "name": "Opportunity Test Farm",
        "district": "Sahiwal",
        "province": "Punjab",
        "latitude": 30.67,
        "longitude": 73.10,
    }
    create_res = authenticated_client.post("/api/v1/farms/", json=farm_payload)
    assert create_res.status_code == 201
    farm_id = create_res.json()["id"]

    res = authenticated_client.get(f"/api/v1/opportunities/{farm_id}?month=11")
    assert res.status_code == 200
    data = res.json()
    assert data["farm_id"] == farm_id
    assert len(data["opportunities"]) >= 10

    top_opp = data["opportunities"][0]
    assert "crop_id" in top_opp
    assert "opportunity_score" in top_opp
    assert 0 <= top_opp["opportunity_score"] <= 100
    assert "agronomic_suitability_score" in top_opp
    assert "market_outlook_score" in top_opp
    assert "profitability_score" in top_opp
    assert "action_recommendation" in top_opp


def test_crop_market_prices_and_predictions_db_models(db_session):
    """Verify CropMarketPrice and CropPricePrediction ORM models can be instantiated and saved to database."""
    now = datetime.datetime.now()
    cmp = CropMarketPrice(
        crop_id="WHEAT_001",
        crop_name="Wheat",
        variety="Certified",
        province="Punjab",
        district="Gujrat",
        market="Gujrat Mandi",
        date=now,
        min_price_pkr_40kg=3000.0,
        max_price_pkr_40kg=4000.0,
        average_price_pkr_40kg=3500.0,
        average_price_pkr_100kg=8750.0,
        unit="40 kg",
        source="AMIS Test",
    )
    db_session.add(cmp)

    cpp = CropPricePrediction(
        crop_id="WHEAT_001",
        crop_name="Wheat",
        province="Punjab",
        district="Gujrat",
        market="Gujrat Mandi",
        prediction_date=now,
        current_price_pkr_100kg=8750.0,
        current_price_pkr_40kg=3500.0,
        forecast_7d_pkr_100kg=8900.0,
        forecast_14d_pkr_100kg=9100.0,
        forecast_30d_pkr_100kg=9500.0,
        price_change_7d_pct=1.7,
        price_change_30d_pct=8.5,
        trend_direction="bullish",
        confidence=0.74,
        confidence_pct=74.0,
    )
    db_session.add(cpp)
    db_session.commit()

    saved_cmp = db_session.query(CropMarketPrice).filter(CropMarketPrice.crop_id == "WHEAT_001").first()
    assert saved_cmp is not None
    assert saved_cmp.average_price_pkr_40kg == 3500.0

    saved_cpp = db_session.query(CropPricePrediction).filter(CropPricePrediction.crop_id == "WHEAT_001").first()
    assert saved_cpp is not None
    assert saved_cpp.forecast_30d_pkr_100kg == 9500.0


def test_province_normalization_and_district_inference():
    """Verify normalize_province handles raw names and infers province from district names."""
    from app.core.engine.crop_knowledge import normalize_province

    assert normalize_province("Khyber Pakhtunkhwa") == "KPK"
    assert normalize_province("Gilgit Baltistan") == "AJK/GB"
    assert normalize_province(district_str="Peshawar") == "KPK"
    assert normalize_province(district_str="Quetta") == "Balochistan"
    assert normalize_province(district_str="Hyderabad") == "Sindh"
    assert normalize_province(district_str="Muzaffarabad") == "AJK/GB"


def test_region_specific_potato_kpk_vs_punjab():
    """Verify region-specific planting window calculation for Potato in KPK (March) vs Punjab (October)."""
    march_15 = datetime.date(2026, 3, 15)

    # In KPK, Potato sowing window is March 1 -> April 15 (SPRING/RABI)
    kpk_res = suitability_engine.calculate_planting_window_status("Potato", ref_date=march_15, province="KPK")
    assert kpk_res.status == "PLANT NOW 🟢"
    assert kpk_res.score == 100

    # In Punjab, Potato sowing window is Oct 1 -> Oct 31. On March 15 in Punjab, it should NOT be PLANT NOW.
    punjab_res = suitability_engine.calculate_planting_window_status("Potato", ref_date=march_15, province="Punjab")
    assert punjab_res.status != "PLANT NOW 🟢"


def test_late_sowing_status():
    """Verify LATE SOWING status is correctly triggered when current date is 10 days past window end."""
    # Wheat planting window in Punjab ends Dec 15. Dec 25 is 10 days late.
    dec_25 = datetime.date(2026, 12, 25)
    pw_res = suitability_engine.calculate_planting_window_status("Wheat", ref_date=dec_25, province="Punjab")

    assert "LATE" in pw_res.status
    assert pw_res.days_since_window == 10
    assert pw_res.score == 60


def test_crops_recommendations_with_day_of_year_and_lat_lon(client):
    """Verify GET /api/v1/crops/recommendations with day_of_year and direct latitude/longitude parameters."""
    res = client.get("/api/v1/crops/recommendations?district=Peshawar&latitude=34.015&longitude=71.524&day_of_year=315")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["province"] == "KPK"
    assert len(data["ranked_crops"]) >= 10

