"""AgriTwin AI Router — /api/v1/soil Endpoints.
Provides Soil Physics, ISRIC SoilGrids 2.0 Data, Saxton-Rawls Hydraulics, USDA & Punjabi Texture Classifications.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Farm, SoilProfile, User
from app.routers.auth import get_current_user, get_optional_current_user
from app.services.soil_service import soil_service
from app.core.engine import soil_engine

router = APIRouter(prefix="/soil", tags=["soil_physics"])


@router.get("")
@router.get("/")
async def get_soil_physics(
    latitude: float | None = Query(None, description="Latitude (e.g. 30.81 for Okara)"),
    longitude: float | None = Query(None, description="Longitude (e.g. 73.45 for Okara)"),
    farm_id: int | None = Query(None, description="Optional Farm ID"),
    user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch comprehensive soil physics, texture classification (USDA & Punjabi),
    and Saxton-Rawls hydraulics (Field Capacity, Wilting Point, AWC).
    """
    lat, lon = latitude, longitude

    if farm_id is not None:
        farm = db.get(Farm, farm_id)
        if farm:
            # Farm-scoped lookups require authentication and ownership
            if user is None or farm.user_id != user.id:
                raise HTTPException(status_code=404, detail="Farm not found")
            if farm.latitude and farm.longitude:
                lat, lon = farm.latitude, farm.longitude
            
            # Check for stored SoilProfile
            soil_prof = db.query(SoilProfile).filter(SoilProfile.farm_id == farm.id).first()
            if soil_prof:
                usda, punjabi = soil_engine.classify_usda_texture(
                    sand=soil_prof.sand_pct or 40.0,
                    silt=soil_prof.silt_pct or 30.0,
                    clay=soil_prof.clay_pct or 30.0,
                )
                hydraulics = soil_engine.compute_saxton_rawls_hydraulics(
                    sand_pct=soil_prof.sand_pct or 40.0,
                    clay_pct=soil_prof.clay_pct or 30.0,
                    organic_matter_pct=(soil_prof.organic_carbon_g_per_kg or 8.0) * 0.172,
                )
                return {
                    "status": "success",
                    "farm_id": farm.id,
                    "farm_name": farm.name,
                    "district": farm.district,
                    "latitude": lat,
                    "longitude": lon,
                    "soil_physics": {
                        "ph_topsoil": soil_prof.ph_topsoil or 7.2,
                        "organic_carbon_g_per_kg": soil_prof.organic_carbon_g_per_kg or 8.0,
                        "clay_pct": soil_prof.clay_pct or 30.0,
                        "sand_pct": soil_prof.sand_pct or 40.0,
                        "silt_pct": soil_prof.silt_pct or 30.0,
                        "bulk_density_kg_dm3": soil_prof.bulk_density_kg_dm3 or 1.35,
                        "usda_texture": usda,
                        "punjabi_texture": punjabi,
                        "field_capacity_m3m3": hydraulics["field_capacity"],
                        "wilting_point_m3m3": hydraulics["wilting_point"],
                        "available_water_capacity_mm_m": hydraulics["awc_mm_m"],
                        "saturation_m3m3": hydraulics["saturation"],
                    },
                    "source": "Database SoilProfile Record",
                }

    # Default to Okara, Punjab baseline coords if omitted
    if lat is None or lon is None:
        lat, lon = 30.81, 73.45

    # Query ISRIC SoilGrids and Saxton-Rawls engine
    props = await soil_engine.evaluate_soil_physics(lat, lon)

    return {
        "status": "success",
        "farm_id": farm_id,
        "latitude": lat,
        "longitude": lon,
        "soil_physics": {
            "ph_topsoil": 7.2,
            "organic_carbon_g_per_kg": round((props.organic_matter_pct or 1.2) / 0.172, 1),
            "clay_pct": props.clay_pct,
            "sand_pct": props.sand_pct,
            "silt_pct": props.silt_pct,
            "bulk_density_kg_dm3": 1.35,
            "usda_texture": props.usda_texture,
            "punjabi_texture": props.punjabi_texture,
            "field_capacity_m3m3": props.field_capacity_m3m3,
            "wilting_point_m3m3": props.wilting_point_m3m3,
            "available_water_capacity_mm_m": props.available_water_capacity_mm_m,
            "saturation_m3m3": props.saturation_m3m3,
        },
        "source": props.data_source,
    }


@router.get("/{farm_id}")
async def get_farm_soil_physics(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch soil physics for a specific registered farm ID."""
    return await get_soil_physics(farm_id=farm_id, user=user, db=db)
