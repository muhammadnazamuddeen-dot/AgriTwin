"""
AgriTwin AI Router — /api/v1/ai/explain endpoint.
Takes structured farm facts + numerical ML metrics (Price & Suitability Engines)
and returns natural bilingual explanations.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Farm, Crop, SoilProfile
from app.services.yield_engine import get_yield_prediction
from app.services.weather_service import weather_service
from app.services.price_prediction_engine import price_prediction_engine
from app.core.engine import suitability_engine
from app.services.rag_service import rag_service
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.inference.agritwin_llm import llm_engine

router = APIRouter(prefix="/ai", tags=["ai_explain"])

class AIExplainRequest(BaseModel):
    farm_id: int | None = None
    query: str | None = None
    language: str = "en"  # "en", "ur", "pa"


class AIExplainResponse(BaseModel):
    summary: str
    health_status: str
    risks: list[str]
    recommendations: list[str]
    explanation: str
    confidence: float


@router.post("/explain", response_model=AIExplainResponse)
@router.post("/assistant", response_model=AIExplainResponse)
async def explain_farm_intelligence(req: AIExplainRequest, db: Session = Depends(get_db)):
    farm = None
    if req.farm_id is not None:
        farm = db.get(Farm, req.farm_id)
    if not farm:
        farm = db.query(Farm).first()

    if farm and farm.latitude and farm.longitude:
        weather = await weather_service.get_current_weather_open_meteo(farm.latitude, farm.longitude)
        current = weather.get("current", {})
        temp = current.get("temperature_2m", 30.0)
        hum = current.get("relative_humidity_2m", 55.0)
        soil_m = current.get("soil_moisture_0_to_7cm", 0.22)
        district = farm.district or "Gujrat"
        latest_crop = db.query(Crop).filter(Crop.farm_id == farm.id).order_by(Crop.id.desc()).first()
        crop_name = latest_crop.crop_name if latest_crop else "Wheat"
    else:
        temp = 30.0
        hum = 55.0
        soil_m = 0.22
        district = "Okara"
        crop_name = "Wheat"
        weather = {}

    # Numerical ML Yield
    telemetry_payload = {"temperature_c": temp, "humidity_pct": hum, "soil_moisture": soil_m}
    yield_pred = get_yield_prediction(district, crop_name, telemetry=telemetry_payload)
    rag_context = rag_service.retrieve_advisory(crop_name, district, telemetry=telemetry_payload, language=req.language)

    # ML Market Price Forecast
    price_fc = price_prediction_engine.forecast_price(
        crop_name=crop_name, district=district, temperature_c=temp, humidity_pct=hum
    )

    # 7-Factor Crop Suitability & Gross Margin Engine
    soil_prof = db.query(SoilProfile).filter(SoilProfile.farm_id == farm.id).first()
    soil_data = {
        "ph_topsoil": soil_prof.ph_topsoil if soil_prof else 7.2,
        "organic_carbon_g_per_kg": soil_prof.organic_carbon_g_per_kg if soil_prof else 8.0,
        "clay_pct": soil_prof.clay_pct if soil_prof else 30,
        "sand_pct": soil_prof.sand_pct if soil_prof else 40,
    }
    farm_data = {
        "canal_name": farm.canal_name,
        "canal_turn_duration_hours": farm.canal_turn_duration_hours,
        "tubewell_power_source": farm.tubewell_power_source,
    }
    suitability_res = suitability_engine.evaluate_crop_suitability(
        crop_name=crop_name,
        farm_data=farm_data,
        soil_data=soil_data,
        weather_data=weather,
        price_forecast_data=price_fc,
    )

    import datetime
    today_str = str(datetime.date.today())
    cal_entry = suitability_engine.get_crop_calendar_entry(crop_name)
    season_val = cal_entry.get("season", "Rabi" if datetime.date.today().month in [10, 11, 12, 1, 2, 3] else "Kharif") if cal_entry else ("Rabi" if datetime.date.today().month in [10, 11, 12, 1, 2, 3] else "Kharif")
    p_window_str = f"{cal_entry['planting_window']['start']} to {cal_entry['planting_window']['end']}" if cal_entry and "planting_window" in cal_entry else "In Season"

    structured_facts = {
        "date": today_str,
        "season": season_val,
        "planting_window": p_window_str,
        "district": district,
        "location": f"{district}, Punjab",
        "crop": crop_name,
        "growth_stage": latest_crop.growth_stage if latest_crop else "Vegetative",
        "temperature_c": temp,
        "humidity_pct": hum,
        "soil_moisture": soil_m,
        "ndvi": 0.65,
        "health_score": 82,
        "water_stress": 20,
        "heat_stress": 15,
        "yield_prediction_t_ha": yield_pred,
        "mandi_rate": f"PKR {price_fc['current_price_maund']:,} / 40kg maund",
        "price_forecast_7d": price_fc["forecast_7d"],
        "price_forecast_30d": price_fc["forecast_30d"],
        "price_direction": price_fc["direction"],
        "price_confidence_pct": price_fc["confidence_pct"],
        "suitability_score": suitability_res["suitability_score"],
        "status": suitability_res.get("status", "PLANT NOW 🟢"),
        "days_until_window": suitability_res.get("days_until_window", 0),
        "season_score": suitability_res.get("season_score", 80),
        "planting_window_score": suitability_res.get("planting_window_score", 80),
        "weather_score": suitability_res.get("weather_score", 80),
        "soil_score": suitability_res.get("soil_score", 80),
        "water_score": suitability_res.get("water_score", 80),
        "disease_risk_score": suitability_res.get("disease_risk_score", 85),
        "yield_score": suitability_res.get("yield_score", 80),
        "market_score": suitability_res.get("market_score", 80),
        "profit_score": suitability_res.get("profit_score", 80),
        "crop_recommendation_level": suitability_res["recommendation_level"],
        "expected_yield_maunds_acre": suitability_res["expected_yield_maunds_acre"],
        "expected_price_pkr_maund": suitability_res["expected_price_pkr_maund"],
        "expected_revenue_pkr_acre": suitability_res["expected_revenue_pkr_acre"],
        "estimated_cost_pkr_acre": suitability_res["estimated_cost_pkr_acre"],
        "expected_gross_margin_pkr_acre": suitability_res["expected_gross_margin_pkr_acre"],
        "todays_farm_action": suitability_res.get("todays_farm_action", []),
        "timeline": suitability_res.get("timeline", []),
        "rag_context": rag_context,
    }

    explanation = llm_engine.generate_explanation(structured_facts, language=req.language)

    risks = []
    if temp > 35:
        risks.append("High Temperature Thermal Stress")
    if soil_m < 0.18:
        risks.append("Root Zone Soil Moisture Deficit")

    return AIExplainResponse(
        summary=f"Diagnostic & financial decision report for {crop_name} in {district}.",
        health_status="Optimal Condition" if structured_facts["health_score"] >= 75 else "Moderate Stress",
        risks=risks or ["No Critical Environmental Risks Detected"],
        recommendations=[rag_context],
        explanation=explanation,
        confidence=0.96
    )
