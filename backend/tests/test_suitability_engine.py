"""Tests for Phase 7 — Crop Suitability Engine."""

import pytest
from app.core.engine import suitability_engine


def test_soil_suitability_basic():
    # Optimal conditions
    score, limits, recs = suitability_engine.calculate_soil_suitability(
        crop_name="Wheat",
        ph=7.2,
        organic_carbon_g_kg=8.5,
        clay_pct=30,
        sand_pct=40,
        silt_pct=30,
    )
    assert score == 100
    assert len(limits) == 0

    # Alkaline and low organic carbon soil
    score_alk, limits_alk, recs_alk = suitability_engine.calculate_soil_suitability(
        crop_name="Wheat",
        ph=8.6,
        organic_carbon_g_kg=3.5,
    )
    assert score_alk < 60
    assert any("alkalinity" in l.lower() for l in limits_alk)
    assert any("organic carbon" in l.lower() for l in limits_alk)


def test_climate_suitability_heat_stress():
    crop_info = {
        "crop": "Cotton",
        "optimal_temperature_c": {"min": 21, "max": 35, "critical_high": 42},
        "water_requirement_mm": 700,
    }

    # High heat stress (45°C)
    score_heat, limits_heat, _ = suitability_engine.calculate_climate_suitability(
        crop_info=crop_info, temp_c=45.0
    )
    assert score_heat <= 60
    assert any("heat stress" in l.lower() for l in limits_heat)

    # Optimal temperature (28°C)
    score_opt, limits_opt, _ = suitability_engine.calculate_climate_suitability(
        crop_info=crop_info, temp_c=28.0
    )
    assert score_opt == 100
    assert len(limits_opt) == 0


def test_water_suitability():
    crop_rice = {"crop": "Rice (Basmati)", "water_requirement_mm": 1200}

    # No canal, no tubewell -> huge penalty for high water demand
    score_dry, limits_dry, _ = suitability_engine.calculate_water_suitability(
        crop_info=crop_rice, canal_name=None, canal_turn_hours=0, tubewell_power=None
    )
    assert score_dry <= 40
    assert any("high crop water requirement" in l.lower() for l in limits_dry)

    # Canal + tubewell available
    score_wet, limits_wet, _ = suitability_engine.calculate_water_suitability(
        crop_info=crop_rice, canal_name="LBDC", canal_turn_hours=4.0, tubewell_power="diesel"
    )
    assert score_wet == 100


def test_season_suitability():
    wheat_info = {"crop": "Wheat"}

    # November (11) is peak Rabi sowing window
    score_nov, limits_nov, _ = suitability_engine.calculate_season_suitability(wheat_info, month=11)
    assert score_nov == 100

    # July (7) is completely outside Rabi window
    score_jul, limits_jul, _ = suitability_engine.calculate_season_suitability(wheat_info, month=7)
    assert score_jul <= 30
    assert any("outside the wheat" in l.lower() for l in limits_jul)


def test_evaluate_all_crops_ranking():
    farm_data = {
        "canal_name": "Lower Bari Doab Canal",
        "canal_turn_duration_hours": 4.0,
        "tubewell_power_source": "diesel",
    }
    soil_data = {"ph_topsoil": 7.2, "organic_carbon_g_per_kg": 8.0, "clay_pct": 30, "sand_pct": 40}
    weather_data = {"current": {"temperature_2m": 22.0, "relative_humidity_2m": 55.0}}

    # November ranking (Rabi season)
    results = suitability_engine.evaluate_all_crops(
        farm_data=farm_data, soil_data=soil_data, weather_data=weather_data, month=11
    )
    assert len(results) >= 4
    # Wheat should be ranked #1 or highly suitable in November
    top_crop = results[0]
    assert top_crop["crop_name"] == "Wheat"
    assert top_crop["suitability_score"] >= 85
    assert top_crop["category"] == "Highly Suitable"


def test_api_crop_suitability_endpoint(authenticated_client):
    # First register a farm
    farm_payload = {
        "name": "Suitability Test Farm",
        "district": "Khanewal",
        "province": "Punjab",
        "latitude": 30.3,
        "longitude": 71.9,
    }
    create_res = authenticated_client.post("/api/v1/farms/", json=farm_payload)
    assert create_res.status_code == 201
    farm_id = create_res.json()["id"]

    # Call endpoint without crop query (rank all)
    res_all = authenticated_client.get(f"/api/v1/analytics/crop-suitability/{farm_id}?month=11")
    assert res_all.status_code == 200
    data_all = res_all.json()
    assert data_all["farm_id"] == farm_id
    assert len(data_all["ranked_crops"]) >= 4

    # Call endpoint with target crop
    res_wheat = authenticated_client.get(f"/api/v1/analytics/crop-suitability/{farm_id}?crop=Wheat&month=11")
    assert res_wheat.status_code == 200
    data_wheat = res_wheat.json()
    assert data_wheat["target_crop"] == "Wheat"
    assert len(data_wheat["ranked_crops"]) == 1
    assert data_wheat["ranked_crops"][0]["crop_name"] == "Wheat"
    item = data_wheat["ranked_crops"][0]
    assert "status" in item
    assert "days_until_window" in item
    assert "planting_window_score" in item
    assert "yield_score" in item
    assert "timeline" in item
    assert "todays_farm_action" in item


def test_crop_calendar_json_structure():
    """Verify crop_calendar.json contains all required schema fields."""
    calendar = suitability_engine.load_crop_calendar()
    assert len(calendar) >= 10
    required_keys = [
        "crop", "province", "district", "season", "planting_window",
        "harvest_window", "optimal_temp_min", "optimal_temp_max",
        "rainfall_min", "rainfall_max", "soil_ph_min", "soil_ph_max",
        "water_requirement", "growth_days"
    ]
    for entry in calendar:
        for k in required_keys:
            assert k in entry, f"Missing key {k} in crop {entry.get('crop')}"
        assert "start" in entry["planting_window"]
        assert "end" in entry["planting_window"]
        assert "start" in entry["harvest_window"]
        assert "end" in entry["harvest_window"]


def test_dynamic_dates_days_until_window():
    """Verify reference date Sept 6 -> Oct 25 calculation (49 days until wheat window opens)."""
    import datetime
    sept_6 = datetime.date(2026, 9, 6)
    score, days, status = suitability_engine.calculate_planting_window_status("Wheat", ref_date=sept_6)
    assert days == 49
    assert status in ["WAIT 🔵", "PREPARE NOW 🟡"]


def test_9_component_suitability_subscores():
    """Verify 9-component weighted Crop Suitability Score breakdown."""
    import datetime
    farm_data = {"canal_name": "LBDC", "canal_turn_duration_hours": 4.0, "tubewell_power_source": "diesel"}
    soil_data = {"ph_topsoil": 7.2, "organic_carbon_g_per_kg": 8.0, "clay_pct": 30, "sand_pct": 40}
    weather_data = {"current": {"temperature_2m": 22.0, "relative_humidity_2m": 55.0}}

    ref_date = datetime.date(2026, 11, 15) # Peak Rabi window for Wheat
    res = suitability_engine.evaluate_crop_suitability(
        crop_name="Wheat",
        farm_data=farm_data,
        soil_data=soil_data,
        weather_data=weather_data,
        ref_date=ref_date,
    )

    # 9-component sub-scores check
    assert "season_score" in res
    assert "planting_window_score" in res
    assert "climate_score" in res
    assert "soil_score" in res
    assert "water_score" in res
    assert "disease_risk_score" in res
    assert "yield_score" in res
    assert "market_score" in res
    assert "profit_score" in res

    assert res["days_until_window"] == 0
    assert res["status"] == "PLANT NOW 🟢"
    assert res["suitability_score"] >= 80


def test_crop_timeline_and_todays_farm_action():
    """Verify timeline and todays_farm_action checklist generation."""
    import datetime
    res = suitability_engine.evaluate_crop_suitability(
        crop_name="Wheat",
        farm_data={},
        ref_date=datetime.date(2026, 9, 6),
    )
    assert len(res["timeline"]) >= 4
    assert len(res["todays_farm_action"]) >= 2
    assert any("Wheat" in action or "sowing" in action.lower() or "prepare" in action.lower() or "hold" in action.lower() for action in res["todays_farm_action"])


def test_agritwin_llm_bilingual_explanation():
    """Verify agritwin_llm receives structured facts and generates English & Shahmukhi Punjabi explanations."""
    from ai.inference.agritwin_llm import llm_engine

    structured_facts = {
        "location": "Gujrat, Punjab",
        "district": "Gujrat",
        "crop": "Wheat",
        "status": "WAIT 🔵",
        "days_until_window": 49,
        "suitability_score": 88,
        "season_score": 90,
        "planting_window_score": 50,
        "weather_score": 90,
        "soil_score": 95,
        "water_score": 85,
        "disease_risk_score": 90,
        "yield_score": 90,
        "market_score": 85,
        "profit_score": 88,
        "expected_gross_margin_pkr_acre": 85000,
        "price_forecast_7d": 3800,
        "price_forecast_30d": 3950,
        "todays_farm_action": ["Prepare land for upcoming Wheat sowing window", "Inspect canal water turn schedule"],
    }

    explanation_en = llm_engine.generate_explanation(structured_facts, language="en")
    assert "Wheat" in explanation_en
    assert "Suitability Engine" in explanation_en or "9-Component" in explanation_en or "Status:" in explanation_en

    explanation_pa = llm_engine.generate_explanation(structured_facts, language="pa")
    assert "تجزیہ" in explanation_pa or "فارم" in explanation_pa or "Wheat" in explanation_pa


def test_cross_year_planting_window_calculation():
    """Verify cross-year planting window (e.g. Nov 15 - Feb 15) behaves correctly prior to start date."""
    import datetime, unittest.mock
    with unittest.mock.patch("app.core.engine.suitability_engine.get_crop_calendar_entry", return_value={"planting_window": {"start": "11-15", "end": "02-15"}}):
        # 31 days before window opens
        oct_15 = datetime.date(2026, 10, 15)
        score_oct, days_oct, status_oct = suitability_engine.calculate_planting_window_status("CrossYearCrop", ref_date=oct_15)
        assert days_oct == 31
        assert score_oct == 50
        assert status_oct == "WAIT 🔵"

        # Inside window (Dec 1)
        dec_1 = datetime.date(2026, 12, 1)
        score_dec, days_dec, status_dec = suitability_engine.calculate_planting_window_status("CrossYearCrop", ref_date=dec_1)
        assert days_dec == 0
        assert score_dec == 100
        assert status_dec == "PLANT NOW 🟢"

        # Inside window cross-year (Jan 15)
        jan_15 = datetime.date(2027, 1, 15)
        score_jan, days_jan, status_jan = suitability_engine.calculate_planting_window_status("CrossYearCrop", ref_date=jan_15)
        assert days_jan == 0
        assert score_jan == 100
        assert status_jan == "PLANT NOW 🟢"


def test_evaluate_all_crops_comprehensive():
    """Verify evaluate_all_crops returns all 13 crops from the crop calendar database."""
    farm_data = {"canal_name": "LBDC", "canal_turn_duration_hours": 4.0, "tubewell_power_source": "diesel"}
    results = suitability_engine.evaluate_all_crops(farm_data=farm_data, month=11)
    assert len(results) >= 13
    crop_names = [r["crop_name"] for r in results]
    assert "Wheat" in crop_names
    assert "Potato" in crop_names
    assert "Canola / Mustard" in crop_names
    assert "Gram (Chickpea)" in crop_names
    assert "Barley" in crop_names
    assert "Lentil" in crop_names
    assert "Peas" in crop_names


def test_season_suitability_all_crops():
    """Verify season suitability accurately scores off-season crops (e.g. Barley/Peas in July)."""
    score_barley_jul, limits_barley, _ = suitability_engine.calculate_season_suitability({"crop": "Barley"}, month=7)
    assert score_barley_jul <= 30
    assert any("outside" in l.lower() for l in limits_barley)

    score_peas_jul, limits_peas, _ = suitability_engine.calculate_season_suitability({"crop": "Peas"}, month=7)
    assert score_peas_jul <= 30
    assert any("outside" in l.lower() for l in limits_peas)


def test_soil_ph_bounds_crop_specific():
    """Verify soil suitability respects crop-specific pH ranges."""
    # Cotton (optimal pH 6.0 - 8.2) with pH 8.0 should not be penalized
    score_cotton, limits_cotton, _ = suitability_engine.calculate_soil_suitability("Cotton", ph=8.0, organic_carbon_g_kg=8.0)
    assert score_cotton == 100
    assert len(limits_cotton) == 0

    # Potato (optimal pH 5.2 - 6.8) with pH 7.8 should be penalized
    score_potato, limits_potato, _ = suitability_engine.calculate_soil_suitability("Potato", ph=7.8, organic_carbon_g_kg=8.0)
    assert score_potato < 80
    assert any("exceeds" in l.lower() or "alkaline" in l.lower() for l in limits_potato)


