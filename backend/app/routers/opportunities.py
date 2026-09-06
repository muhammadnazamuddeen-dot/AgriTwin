"""AgriTwin AI Router — /api/v1/opportunities Endpoints.
Opportunity Engine — combines Crop Suitability Score + Market Outlook + Profitability into an Opportunity Score (0-100).
"""

import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Farm, SoilProfile, User
from app.routers.auth import get_current_user
from app.services.weather_service import weather_service
from app.services.price_prediction_engine import price_prediction_engine
from app.core.engine import suitability_engine, crop_knowledge

router = APIRouter(prefix="/opportunities", tags=["market_opportunities"])


def _calculate_opportunity(
    suitability_res: dict[str, Any],
    price_forecast_res: dict[str, Any],
) -> dict[str, Any]:
    """
    Combines agronomic suitability score, market outlook score, and profitability score
    into a composite Opportunity Score (0-100).
    """
    agronomic_score = suitability_res.get("suitability_score", 75)
    
    # Market Outlook Score based on price direction and 30-day forecast change %
    direction = price_forecast_res.get("direction", "stable").lower()
    change_30d_pct = price_forecast_res.get("price_change_30d_pct", 0.0)

    if direction == "bullish" or change_30d_pct > 3.0:
        market_outlook_score = 90
    elif direction == "bearish" or change_30d_pct < -3.0:
        market_outlook_score = 60
    else:
        market_outlook_score = 75

    # Profitability Score based on expected gross margin per acre
    gross_margin = suitability_res.get("expected_gross_margin_pkr_acre") or 50000.0
    if gross_margin >= 150000:
        profitability_score = 95
    elif gross_margin >= 100000:
        profitability_score = 85
    elif gross_margin >= 50000:
        profitability_score = 75
    else:
        profitability_score = 60

    # Composite Opportunity Score (0-100):
    # 50% Agronomic Suitability + 25% Market Outlook + 25% Profitability
    opportunity_score = round(
        0.50 * agronomic_score + 0.25 * market_outlook_score + 0.25 * profitability_score
    )
    opportunity_score = max(0, min(100, opportunity_score))

    if opportunity_score >= 85:
        tier = "HIGH OPPORTUNITY 🚀"
        action = "High profit potential with strong agronomic alignment. Recommended for immediate sowing."
    elif opportunity_score >= 70:
        tier = "GOOD OPPORTUNITY 📈"
        action = "Favorable returns and solid suitability. Good option for the upcoming planting window."
    elif opportunity_score >= 50:
        tier = "MODERATE OPPORTUNITY ⚖️"
        action = "Moderate risk/return balance. Evaluate water and input costs before committing."
    else:
        tier = "LOW OPPORTUNITY ⚠️"
        action = "Off-season or lower market profitability relative to alternative crops."

    return {
        "crop_id": suitability_res.get("crop_id"),
        "crop_name": suitability_res.get("crop_name"),
        "opportunity_score": opportunity_score,
        "opportunity_tier": tier,
        "agronomic_suitability_score": agronomic_score,
        "market_outlook_score": market_outlook_score,
        "profitability_score": profitability_score,
        "expected_gross_margin_pkr_acre": gross_margin,
        "forecast_30d_maund_pkr": price_forecast_res.get("forecast_30d_maund"),
        "forecast_30d_change_pct": change_30d_pct,
        "status": suitability_res.get("status"),
        "status_code": suitability_res.get("status_code"),
        "days_until_window": suitability_res.get("days_until_window", 0),
        "days_remaining_in_window": suitability_res.get("days_remaining_in_window", 0),
        "action_recommendation": action,
    }


@router.get("/{farm_id}")
async def get_farm_market_opportunities(
    farm_id: int,
    month: int | None = Query(None, description="Sowing month 1-12"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Evaluates market opportunities for a farm by combining pure agronomic suitability score,
    ML price predictions, and gross profit estimates into an Opportunity Score (0-100).
    """
    farm = db.get(Farm, farm_id)
    if not farm or farm.user_id != user.id:
        raise HTTPException(status_code=404, detail="Farm not found")

    district = farm.district or "Gujrat"
    province = farm.province or "Punjab"

    soil_prof = db.query(SoilProfile).filter(SoilProfile.farm_id == farm.id).first()
    soil_data = {}
    if soil_prof:
        soil_data = {
            "ph_topsoil": soil_prof.ph_topsoil,
            "organic_carbon_g_per_kg": soil_prof.organic_carbon_g_per_kg,
            "clay_pct": soil_prof.clay_pct,
            "sand_pct": soil_prof.sand_pct,
            "silt_pct": soil_prof.silt_pct,
        }

    weather_data = {}
    if farm.latitude and farm.longitude:
        try:
            weather_data = await weather_service.get_forecast_open_meteo(
                farm.latitude, farm.longitude, forecast_days=1
            )
        except Exception:
            pass

    farm_data = {
        "province": province,
        "district": district,
        "canal_name": farm.canal_name,
        "canal_turn_duration_hours": farm.canal_turn_duration_hours,
        "tubewell_power_source": farm.tubewell_power_source,
    }

    # Evaluate suitability for all crops
    suitability_list = suitability_engine.evaluate_all_crops(
        farm_data=farm_data,
        soil_data=soil_data,
        weather_data=weather_data,
        month=month,
        price_forecasts=None,  # pure agronomic suitability input
    )

    opportunities = []
    for s_res in suitability_list:
        c_name = s_res["crop_name"]
        p_fc = price_prediction_engine.forecast_price(crop_name=c_name, district=district, db=db)
        opp = _calculate_opportunity(s_res, p_fc)
        opportunities.append(opp)

    opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)

    return {
        "farm_id": farm.id,
        "farm_name": farm.name,
        "district": district,
        "province": province,
        "evaluated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "opportunities_count": len(opportunities),
        "opportunities": opportunities,
    }


@router.get("")
@router.get("/")
async def get_general_market_opportunities(
    province: str | None = Query("Punjab", description="Province"),
    district: str | None = Query("Gujrat", description="District"),
    month: int | None = Query(None, description="Sowing month 1-12"),
    db: Session = Depends(get_db),
):
    """
    Returns general agricultural market opportunities for a region without requiring a registered farm_id.
    """
    farm_data = {"province": province or "Punjab", "district": district or "Gujrat"}
    suitability_list = suitability_engine.evaluate_all_crops(
        farm_data=farm_data, month=month, price_forecasts=None
    )

    opportunities = []
    for s_res in suitability_list:
        c_name = s_res["crop_name"]
        p_fc = price_prediction_engine.forecast_price(crop_name=c_name, district=district or "Gujrat", db=db)
        opp = _calculate_opportunity(s_res, p_fc)
        opportunities.append(opp)

    opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)

    return {
        "district": district or "Gujrat",
        "province": province or "Punjab",
        "evaluated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "opportunities_count": len(opportunities),
        "opportunities": opportunities,
    }
