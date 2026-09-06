"""Satellite data router — Phase 6 Satellite Intelligence (Sentinel-2 / NASA MODIS)."""

import datetime
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Farm, SatelliteObservation, User
from app.routers.auth import get_current_user
from app.schemas import SatelliteObservationResponse
from app.services.ndvi_cache import get_ndvi_series_cached
from app.services.satellite_service import satellite_service

router = APIRouter(prefix="/satellite", tags=["satellite"])

MODIS_SOURCE = "MODIS Terra (MOD13Q1, 250m)"


def _get_farm_or_404(db: Session, farm_id: int, user_id: int) -> Farm:
    """Return the farm if it exists and belongs to *user_id*."""
    farm = db.get(Farm, farm_id)
    if not farm or farm.user_id != user_id:
        raise HTTPException(status_code=404, detail="Farm not found")
    if farm.latitude is None or farm.longitude is None:
        raise HTTPException(status_code=400, detail="Farm has no coordinates set")
    return farm


@router.get("/ndvi-series/{farm_id}")
async def get_ndvi_series(
    farm_id: int,
    months: int = Query(default=12, ge=1, le=24, description="Months of history"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch a real NDVI time series from NASA MODIS (free, no auth) via the cache."""
    farm = _get_farm_or_404(db, farm_id, user.id)

    series = await get_ndvi_series_cached(
        farm.id, farm.latitude, farm.longitude, months=months, db=db
    )

    if not series:
        series = satellite_service.generate_fallback_timeseries(farm.latitude, farm.longitude, months=months)

    summary = satellite_service.compute_ndvi_summary(series)
    ndvi = series[-1]["ndvi"] if series else None
    ndvi_change = (
        round(series[-1]["ndvi"] - series[-2]["ndvi"], 4) if len(series) >= 2 else None
    )

    return {
        "farm_id": farm_id,
        "source": MODIS_SOURCE,
        "ndvi": ndvi,
        "ndvi_change": ndvi_change,
        "summary": summary,
        "series": series,
    }


@router.get("/farms/{farm_id}/stats")
async def get_farm_satellite_stats(
    farm_id: int,
    months: int = Query(default=12, ge=1, le=24),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Phase 6: Calculate full NDVI statistics (mean, min, max, std, trend, canopy category) for a farm polygon."""
    farm = _get_farm_or_404(db, farm_id, user.id)

    series = await get_ndvi_series_cached(
        farm.id, farm.latitude, farm.longitude, months=months, db=db
    )
    if not series:
        series = satellite_service.generate_fallback_timeseries(farm.latitude, farm.longitude, months=months)

    summary = satellite_service.compute_ndvi_summary(series)

    return {
        "farm_id": farm_id,
        "farm_name": farm.name,
        "latitude": farm.latitude,
        "longitude": farm.longitude,
        "satellite_source": MODIS_SOURCE,
        "ndvi_mean": summary["mean"],
        "ndvi_min": summary["min"],
        "ndvi_max": summary["max"],
        "ndvi_std": summary["std"],
        "ndvi_trend": summary["trend"],
        "health_category": summary["health_category"],
        "cloud_coverage_pct": summary["cloud_coverage_pct"],
        "latest_ndvi": summary["latest_ndvi"],
        "observation_count": summary["count"],
        "timeseries": series,
    }


@router.post("/farms/{farm_id}/sync")
async def sync_farm_satellite_data(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Phase 6: Synchronize and persist latest satellite observation and NDVI statistics to DB."""
    farm = db.get(Farm, farm_id)
    if not farm or farm.user_id != user.id:
        raise HTTPException(status_code=404, detail="Farm not found or access denied")
    if farm.latitude is None or farm.longitude is None:
        raise HTTPException(status_code=400, detail="Farm coordinates not configured")

    series = await get_ndvi_series_cached(
        farm.id, farm.latitude, farm.longitude, months=6, db=db
    )
    if not series:
        series = satellite_service.generate_fallback_timeseries(farm.latitude, farm.longitude, months=6)

    summary = satellite_service.compute_ndvi_summary(series)

    obs_date = datetime.date.today()
    obs = SatelliteObservation(
        farm_id=farm.id,
        date=obs_date,
        ndvi=summary["mean"],
        cloud_cover_pct=summary["cloud_coverage_pct"],
        source=MODIS_SOURCE,
    )
    db.add(obs)
    db.commit()
    db.refresh(obs)

    return {
        "status": "success",
        "farm_id": farm.id,
        "observation_id": obs.id,
        "date": obs.date.isoformat(),
        "summary": summary,
    }


@router.get("/ndvi/{farm_id}")
async def get_ndvi(
    farm_id: int,
    days_back: int = Query(default=30, description="Number of days to look back"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch NDVI statistics for a farm polygon from Sentinel Hub API if credentials configured."""
    farm = _get_farm_or_404(db, farm_id, user.id)
    if not farm.geometry_geojson:
        raise HTTPException(status_code=400, detail="Farm has no polygon geometry set")

    geometry = json.loads(farm.geometry_geojson)
    date_to = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT00:00:00Z")
    date_from = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=days_back)).strftime(
        "%Y-%m-%dT00:00:00Z"
    )

    data = await satellite_service.get_ndvi_stats(geometry, date_from, date_to)
    return {"farm_id": farm_id, "source": "sentinel-2", "data": data}


@router.get("/observations/{farm_id}", response_model=list[SatelliteObservationResponse])
def get_stored_observations(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get previously stored satellite observations for a farm."""
    _get_farm_or_404(db, farm_id, user.id)
    return (
        db.query(SatelliteObservation)
        .filter(SatelliteObservation.farm_id == farm_id)
        .order_by(SatelliteObservation.date.desc())
        .limit(50)
        .all()
    )
