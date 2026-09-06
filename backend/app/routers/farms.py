"""Farm management router — CRUD for farms and crops."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Crop, Farm, User
from app.routers.auth import get_current_user
from app.schemas import CropCreate, CropResponse, CropUpdate, FarmCreate, FarmResponse, FarmUpdate
from app.services.geo import compute_area_and_centroid, get_ip_location, reverse_geocode
from app.core.engine import warabandi_engine, crop_knowledge

router = APIRouter(prefix="/farms", tags=["farms"])


# ── Helpers ──────────────────────────────────────────────────────────────────
def _get_farm_or_404(db: Session, farm_id: int, user_id: int) -> Farm:
    """Return the farm if it exists and belongs to *user_id*."""
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == user_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


async def _enrich_geo_fields(data: dict) -> dict:
    """If a GeoJSON polygon is present, auto-compute area, centroid, district, province.
    If lat/lon is provided without district, auto-reverse geocode."""
    geojson = data.get("geometry_geojson")
    if geojson:
        geo = compute_area_and_centroid(geojson)
        data.setdefault("area_acres", geo["area_acres"])
        data.setdefault("latitude", geo["latitude"])
        data.setdefault("longitude", geo["longitude"])
        # Always prefer server-calculated values when geometry is provided
        data["area_acres"] = geo["area_acres"]
        data["latitude"] = geo["latitude"]
        data["longitude"] = geo["longitude"]

    # Reverse geocode district / province if lat/lon available and district missing or geometry present
    lat = data.get("latitude")
    lon = data.get("longitude")
    if lat is not None and lon is not None and (geojson or not data.get("district")):
        location = await reverse_geocode(lat, lon)
        if location["district"] and not data.get("district"):
            data["district"] = location["district"]
        if location["province"] and not data.get("province"):
            data["province"] = location["province"]

    return data


@router.get("/reverse-geocode")
async def reverse_geocode_location(lat: float, lon: float):
    """Reverse geocode lat/lon to Pakistani district and province with nearest-centroid fallback."""
    return await reverse_geocode(lat, lon)


@router.get("/ip-location")
async def ip_location_endpoint():
    """Get location estimate from client IP with Pakistani fallback."""
    return await get_ip_location()



# ── Farm CRUD ────────────────────────────────────────────────────────────────
@router.post("/", response_model=FarmResponse, status_code=201)
async def create_farm(
    payload: FarmCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new farm.  Area, centroid, district and province are computed
    server-side when a GeoJSON polygon is provided."""
    data = payload.model_dump()

    if not data.get("canal_name"):
        data["canal_name"] = warabandi_engine.infer_canal_from_location(
            district=data.get("district"),
            lat=data.get("latitude"),
            lon=data.get("longitude"),
        )

    data = await _enrich_geo_fields(data)

    farm = Farm(user_id=user.id, **data)
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@router.get("/", response_model=list[FarmResponse])
def list_farms(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all farms belonging to the authenticated user."""
    return db.query(Farm).filter(Farm.user_id == user.id).all()


@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a single farm (must belong to the authenticated user)."""
    return _get_farm_or_404(db, farm_id, user.id)


@router.put("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: int,
    payload: FarmUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing farm.  Re-computes area, centroid, district and
    province when a new GeoJSON polygon is supplied."""
    farm = _get_farm_or_404(db, farm_id, user.id)

    data = payload.model_dump(exclude_unset=True)

    # Infer canal if not explicitly set and location data is present
    if "canal_name" not in data:
        lat = data.get("latitude", farm.latitude)
        lon = data.get("longitude", farm.longitude)
        district = data.get("district", farm.district)
        inferred = warabandi_engine.infer_canal_from_location(
            district=district, lat=lat, lon=lon
        )
        if inferred:
            data["canal_name"] = inferred

    data = await _enrich_geo_fields(data)

    for field, value in data.items():
        setattr(farm, field, value)

    db.commit()
    db.refresh(farm)
    return farm


@router.delete("/{farm_id}", status_code=204)
def delete_farm(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farm = _get_farm_or_404(db, farm_id, user.id)
    db.delete(farm)
    db.commit()


# ── Crop CRUD ────────────────────────────────────────────────────────────────


@router.post("/{farm_id}/crops", response_model=CropResponse, status_code=201)
def add_crop(
    farm_id: int,
    payload: CropCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farm = _get_farm_or_404(db, farm_id, user.id)
    data = payload.model_dump()
    if not data.get("growth_stage") and data.get("sowing_date"):
        stage_info = crop_knowledge.derive_growth_stage(data["crop_name"], data["sowing_date"])
        data["growth_stage"] = stage_info["stage"]
    crop = Crop(farm_id=farm.id, **data)
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop


@router.put("/{farm_id}/crops/{crop_id}", response_model=CropResponse)
def update_crop(
    farm_id: int,
    crop_id: int,
    payload: CropUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing crop entry.  Re-derives growth stage when
    crop_name or sowing_date changes and growth_stage is not explicitly set."""
    farm = _get_farm_or_404(db, farm_id, user.id)
    crop = db.query(Crop).filter(Crop.id == crop_id, Crop.farm_id == farm.id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    data = payload.model_dump(exclude_unset=True)

    # Re-derive growth stage if sowing_date or crop_name changed and stage not explicit
    if "growth_stage" not in data:
        new_name = data.get("crop_name", crop.crop_name)
        new_sowing = data.get("sowing_date", crop.sowing_date)
        if "crop_name" in data or "sowing_date" in data:
            if new_sowing:
                stage_info = derive_growth_stage(new_name, new_sowing)
                data["growth_stage"] = stage_info["stage"]

    for field, value in data.items():
        setattr(crop, field, value)

    db.commit()
    db.refresh(crop)
    return crop


@router.get("/{farm_id}/crops", response_model=list[CropResponse])
def list_crops(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farm = _get_farm_or_404(db, farm_id, user.id)
    crops = db.query(Crop).filter(Crop.farm_id == farm.id).all()
    # Dynamic sync of current growth stage based on elapsed days
    for c in crops:
        if c.sowing_date:
            stage_info = crop_knowledge.derive_growth_stage(c.crop_name, c.sowing_date)
            if c.growth_stage != stage_info["stage"]:
                c.growth_stage = stage_info["stage"]
                db.add(c)
    db.commit()
    return crops
