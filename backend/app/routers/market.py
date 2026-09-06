"""
AgriTwin AI Router — /api/v1/market Endpoints.
Provides real-time market price analysis, AMIS commodity rates, ML price forecasting,
7-factor crop suitability scoring, and expected gross margin estimations.
"""

import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Farm, SoilProfile
from app.services.market_price_service import market_price_service
from app.services.price_prediction_engine import price_prediction_engine
from app.services.weather_service import weather_service
from app.core.engine import suitability_engine, crop_knowledge
from app.schemas import CropSuitabilityItem, CropSuitabilityResponse

router = APIRouter(prefix="/market", tags=["market_prices"])

class ProfitEstimateRequest(BaseModel):
    crop_name: str
    predicted_yield_t_ha: float
    field_area_acres: float = 10.0
    custom_mandi_rate_pkr: float | None = None

@router.get("/prices")
async def get_realtime_market_prices(
    district: str | None = Query(None, description="Optional Punjab District filter"),
    db: Session = Depends(get_db)
):
    """
    Fetch real-time wholesale commodity market prices across Punjab Mandis.
    Queries live AMIS / PAR third-party feeds with automated fallback to verified ground-truth benchmark data.
    """
    return await market_price_service.fetch_live_commodity_prices(district=district, db=db)

@router.get("/analysis/{crop_name}")
def get_crop_market_analysis(
    crop_name: str,
    yield_t_ha: float | None = Query(None, description="Optional predicted yield in tonnes/ha"),
    area_acres: float = Query(10.0, description="Field area in acres")
):
    """
    Returns real-time price trend analysis, cost vs profit margins, and harvest marketing advisories for a crop.
    """
    return market_price_service.analyze_crop_market(
        crop_name=crop_name,
        predicted_yield_t_ha=yield_t_ha,
        field_area_acres=area_acres
    )

@router.post("/profit-estimate")
def estimate_farm_net_profit(payload: ProfitEstimateRequest):
    """
    Calculate estimated net profit, gross revenue, and cost of production for a crop given yield prediction.
    """
    return market_price_service.analyze_crop_market(
        crop_name=payload.crop_name,
        predicted_yield_t_ha=payload.predicted_yield_t_ha,
        field_area_acres=payload.field_area_acres
    )

@router.get("/forecast/{crop_name}")
def forecast_crop_prices(
    crop_name: str,
    district: str | None = Query("Gujrat", description="Punjab district"),
    market: str | None = Query(None, description="Local Mandi name"),
    current_price: float | None = Query(None, description="Current price per 100kg (optional)"),
    temp_c: float = Query(28.0, description="Current ambient temperature °C"),
    humidity_pct: float = Query(55.0, description="Current relative humidity %"),
):
    """
    Computes ML 7-day, 14-day, and 30-day commodity price forecasts, direction, and confidence %.
    Uses GradientBoosting Machine Learning model.
    """
    return price_prediction_engine.forecast_price(
        crop_name=crop_name,
        district=district or "Gujrat",
        market=market or f"{district or 'Gujrat'} Mandi",
        current_price_100kg=current_price,
        temperature_c=temp_c,
        humidity_pct=humidity_pct,
    )

@router.get("/suitability/{farm_id}", response_model=CropSuitabilityResponse)
async def get_farm_crop_suitability(
    farm_id: int,
    crop: str | None = Query(None, description="Target crop filter (optional)"),
    month: int | None = Query(None, description="Sowing month 1-12 (defaults to current month)"),
    db: Session = Depends(get_db),
):
    """
    Evaluates 7-factor Crop Suitability (Season, Soil, Weather, Water, Market, Profit, Disease Risk)
    and computes Expected Gross Margin per Acre.
    """
    farm = db.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    soil_prof = db.query(SoilProfile).filter(SoilProfile.farm_id == farm.id).first()
    soil_data = {}
    if soil_prof:
        soil_data = {
            "ph_topsoil": soil_prof.ph_topsoil,
            "organic_carbon_g_per_kg": soil_prof.organic_carbon_g_per_kg,
            "clay_pct": soil_prof.clay_pct,
            "sand_pct": soil_prof.sand_pct,
            "silt_pct": soil_prof.silt_pct,
            "bulk_density_kg_dm3": soil_prof.bulk_density_kg_dm3,
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
        "canal_name": farm.canal_name,
        "canal_turn_duration_hours": farm.canal_turn_duration_hours,
        "tubewell_power_source": farm.tubewell_power_source,
    }

    district = farm.district or "Gujrat"

    if crop:
        p_forecast = price_prediction_engine.forecast_price(
            crop_name=crop, district=district
        )
        res = suitability_engine.evaluate_crop_suitability(
            crop_name=crop,
            farm_data=farm_data,
            soil_data=soil_data,
            weather_data=weather_data,
            month=month,
            price_forecast_data=p_forecast,
        )
        ranked = [CropSuitabilityItem(**res)]
    else:
        price_forecasts = {}
        for entry in crop_knowledge.CROP_KNOWLEDGE_BASE:
            c_name = entry["crop"]
            price_forecasts[c_name] = price_prediction_engine.forecast_price(
                crop_name=c_name, district=district
            )

        results = suitability_engine.evaluate_all_crops(
            farm_data=farm_data,
            soil_data=soil_data,
            weather_data=weather_data,
            month=month,
            price_forecasts=price_forecasts,
        )
        ranked = [CropSuitabilityItem(**r) for r in results]

    return CropSuitabilityResponse(
        farm_id=farm.id,
        evaluated_at=datetime.datetime.now(datetime.timezone.utc),
        target_crop=crop,
        ranked_crops=ranked,
    )
