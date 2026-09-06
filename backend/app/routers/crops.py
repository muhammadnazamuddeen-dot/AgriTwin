"""AgriTwin AI Router — /api/v1/crops Endpoints.
Crop Recommendation Engine — agronomic suitability scoring decoupled from market prices.
"""

import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Farm, SoilProfile
from app.services.weather_service import weather_service
from app.core.engine import suitability_engine, crop_knowledge
from app.schemas import CropSuitabilityItem, CropSuitabilityResponse

from app.services.soil_service import soil_service

router = APIRouter(prefix="/crops", tags=["crop_recommendations"])


@router.get("")
@router.get("/")
def list_available_crops():
    """List all supported agricultural crops with their standardized crop_id and agronomic profiles."""
    crops_list = []
    for entry in crop_knowledge.CROP_KNOWLEDGE_BASE:
        crops_list.append({
            "crop_id": entry["crop_id"],
            "crop_name": entry["crop"],
            "season": entry["season"],
            "sowing_window": entry["sowing_window"],
            "harvest_window": entry["harvest_window"],
            "water_requirement_mm": entry["water_requirement_mm"],
            "mandi_rate_avg_pkr_40kg": entry["mandi_rate_pkr_per_40kg"]["avg"],
            "common_pests": entry.get("common_pests", []),
        })
    return {
        "status": "success",
        "crops_count": len(crops_list),
        "crops": crops_list,
    }


@router.get("/recommendations")
async def get_crop_recommendations(
    farm_id: int | None = Query(None, description="Optional Farm ID"),
    crop_id: str | None = Query(None, description="Optional Crop ID (e.g. WHEAT_001) or crop name filter"),
    province: str | None = Query(None, description="Pakistani agricultural zone / province"),
    district: str | None = Query(None, description="District name"),
    tehsil: str | None = Query(None, description="Tehsil name"),
    latitude: float | None = Query(None, description="Latitude"),
    longitude: float | None = Query(None, description="Longitude"),
    month: int | None = Query(None, description="Sowing month 1-12"),
    day: int | None = Query(None, description="Day of month 1-31"),
    year: int | None = Query(None, description="Year"),
    day_of_year: int | None = Query(None, description="Day of year 1-366"),
    season: str | None = Query(None, description="Agricultural season (Rabi / Kharif / Zaid)"),
    irrigation: str | None = Query(None, description="Irrigation method (irrigated / rainfed / canal / tubewell)"),
    soil_type: str | None = Query(None, description="Soil texture type"),
    ph: float | None = Query(None, description="Soil pH"),
    organic_carbon: float | None = Query(None, description="Organic Carbon g/kg"),
    clay_pct: float | None = Query(None, description="Clay %"),
    sand_pct: float | None = Query(None, description="Sand %"),
    silt_pct: float | None = Query(None, description="Silt %"),
    temp_c: float | None = Query(None, description="Current/Forecast temp °C"),
    humidity_pct: float | None = Query(None, description="Humidity %"),
    rainfall_mm: float | None = Query(None, description="Rainfall mm"),
    water_availability: str | None = Query("Medium", description="Water access: Low / Medium / High"),
    risk_preference: str | None = Query("Moderate", description="Risk tolerance"),
    db: Session = Depends(get_db),
):
    """
    Returns ranked crop recommendations purely on agronomic suitability without requiring price data.
    Includes 9 sub-scores, status (PREPARE, PLANT, WAIT, LATE, NOT_RECOMMENDED), timeline, and Today's Farm Action.
    """
    norm_province = crop_knowledge.normalize_province(province, district)

    farm_data = {
        "province": norm_province,
        "district": district or "Gujrat",
        "tehsil": tehsil,
        "canal_name": "Lower Bari Doab Canal",
        "canal_turn_duration_hours": 4.0 if (water_availability or "").lower() != "low" else 1.0,
        "tubewell_power_source": "diesel" if (water_availability or "").lower() != "low" else None,
        "water_availability": water_availability,
        "risk_preference": risk_preference,
        "irrigation": irrigation,
        "season": season,
    }

    soil_data = {
        "ph_topsoil": ph or 7.2,
        "organic_carbon_g_per_kg": organic_carbon or 7.5,
        "clay_pct": clay_pct or 30.0,
        "sand_pct": sand_pct or 40.0,
        "silt_pct": silt_pct or 30.0,
    }

    weather_data = {
        "current": {
            "temperature_2m": temp_c or 24.0,
            "relative_humidity_2m": humidity_pct or 55.0,
            "precipitation": rainfall_mm or 0.0,
        }
    }

    lat, lon = latitude, longitude

    # If farm_id provided, fetch farm record telemetry from database
    if farm_id is not None:
        farm = db.get(Farm, farm_id)
        if farm:
            norm_province = crop_knowledge.normalize_province(farm.province or province, farm.district or district)
            farm_data["province"] = norm_province
            farm_data["district"] = farm.district or district or "Gujrat"
            farm_data["canal_name"] = farm.canal_name
            farm_data["canal_turn_duration_hours"] = farm.canal_turn_duration_hours
            farm_data["tubewell_power_source"] = farm.tubewell_power_source
            if farm.latitude and farm.longitude:
                lat, lon = farm.latitude, farm.longitude

            soil_prof = db.query(SoilProfile).filter(SoilProfile.farm_id == farm.id).first()
            if soil_prof:
                soil_data = {
                    "ph_topsoil": soil_prof.ph_topsoil or ph or 7.2,
                    "organic_carbon_g_per_kg": soil_prof.organic_carbon_g_per_kg or organic_carbon or 7.5,
                    "clay_pct": soil_prof.clay_pct or clay_pct or 30.0,
                    "sand_pct": soil_prof.sand_pct or sand_pct or 40.0,
                    "silt_pct": soil_prof.silt_pct or silt_pct or 30.0,
                }

    # Integration with Open-Meteo & SoilGrids APIs if lat/lon available
    if lat is not None and lon is not None:
        if temp_c is None or humidity_pct is None or rainfall_mm is None:
            try:
                w_res = await weather_service.get_forecast_open_meteo(lat, lon, forecast_days=1)
                if w_res and "current" in w_res:
                    weather_data = w_res
            except Exception:
                pass

        if ph is None and organic_carbon is None and clay_pct is None:
            try:
                sg_res = await soil_service.get_soil_profile(lat, lon)
                if sg_res:
                    if sg_res.get("ph_topsoil") is not None:
                        soil_data["ph_topsoil"] = sg_res["ph_topsoil"]
                    if sg_res.get("organic_carbon_g_per_kg") is not None:
                        soil_data["organic_carbon_g_per_kg"] = sg_res["organic_carbon_g_per_kg"]
                    if sg_res.get("clay_pct") is not None:
                        soil_data["clay_pct"] = sg_res["clay_pct"]
                    if sg_res.get("sand_pct") is not None:
                        soil_data["sand_pct"] = sg_res["sand_pct"]
                    if sg_res.get("silt_pct") is not None:
                        soil_data["silt_pct"] = sg_res["silt_pct"]
            except Exception:
                pass

    # Reference Date calculation
    ref_date = None
    curr_yr = year or datetime.date.today().year
    if year and month and day:
        try:
            ref_date = datetime.date(year, month, day)
        except Exception:
            pass
    elif month and day:
        try:
            ref_date = datetime.date(curr_yr, month, day)
        except Exception:
            pass
    elif day_of_year:
        try:
            ref_date = datetime.date(curr_yr, 1, 1) + datetime.timedelta(days=max(1, min(366, day_of_year)) - 1)
        except Exception:
            pass

    eval_month = month or (ref_date.month if ref_date else datetime.date.today().month)

    target_crop_name = crop_knowledge.get_crop_name(crop_id) if crop_id else None

    if target_crop_name:
        res = suitability_engine.evaluate_crop_suitability(
            crop_name=target_crop_name,
            farm_data=farm_data,
            soil_data=soil_data,
            weather_data=weather_data,
            month=eval_month,
            price_forecast_data=None,  # Decoupled — no price data required
            ref_date=ref_date,
        )
        ranked = [CropSuitabilityItem(**res)]
    else:
        results = suitability_engine.evaluate_all_crops(
            farm_data=farm_data,
            soil_data=soil_data,
            weather_data=weather_data,
            month=eval_month,
            price_forecasts=None,  # Decoupled — pure agronomic suitability
            ref_date=ref_date,
        )
        ranked = [CropSuitabilityItem(**r) for r in results]

    return {
        "status": "success",
        "province": farm_data["province"],
        "district": farm_data["district"],
        "month": eval_month,
        "evaluated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "target_crop_id": crop_knowledge.get_crop_id(crop_id) if crop_id else None,
        "recommendations_count": len(ranked),
        "ranked_crops": ranked,
    }


@router.get("/{crop_id}")
def get_crop_by_id(crop_id: str):
    """Fetch detailed knowledge base profile and regional planting windows for a specific crop_id."""
    canonical_id = crop_knowledge.get_crop_id(crop_id)
    info = crop_knowledge.get_crop_info(crop_id)
    if not info:
        raise HTTPException(status_code=404, detail=f"Crop with ID/name '{crop_id}' not found")

    regional_windows = crop_knowledge.REGION_PLANTING_WINDOWS.get(canonical_id, {})
    return {
        "status": "success",
        "crop_id": canonical_id,
        "crop_name": info["crop"],
        "season": info.get("season"),
        "sowing_window": info.get("sowing_window"),
        "harvest_window": info.get("harvest_window"),
        "optimal_temperature_c": info.get("optimal_temperature_c"),
        "water_requirement_mm": info.get("water_requirement_mm"),
        "mandi_rate_pkr_per_40kg": info.get("mandi_rate_pkr_per_40kg"),
        "growth_stages": info.get("growth_stages", []),
        "common_pests": info.get("common_pests", []),
        "advisory_2026": info.get("advisory_2026"),
        "regional_planting_windows": regional_windows,
    }

