"""Weather data router — proxy to Open-Meteo and NASA POWER."""

import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models import ClimateSnapshot, Farm, User, WeatherRecord
from app.routers.auth import get_current_user
from app.schemas import ClimateSnapshotResponse, WeatherRecordResponse
from app.services.weather_service import persist_current_weather, weather_service

router = APIRouter(prefix="/weather", tags=["weather"])


def _get_farm_or_404(db, farm_id: int, user_id: int) -> Farm:
    """Return the farm if it exists and belongs to *user_id*."""
    farm = db.query(Farm).get(farm_id)
    if not farm or farm.user_id != user_id:
        raise HTTPException(status_code=404, detail="Farm not found")
    if farm.latitude is None or farm.longitude is None:
        raise HTTPException(status_code=400, detail="Farm has no coordinates set")
    return farm


@router.get("")
@router.get("/")
async def get_weather(
    farm_id: int | None = Query(None, description="Optional Farm ID"),
    latitude: float | None = Query(None, description="Latitude (e.g. 30.81 for Okara)"),
    longitude: float | None = Query(None, description="Longitude (e.g. 73.45 for Okara)"),
    days: int = Query(7, ge=1, le=16),
    db: Session = Depends(get_db),
):
    """Fetch live weather forecast and current conditions for a location or farm."""
    lat, lon = latitude, longitude
    if farm_id is not None:
        farm = db.get(Farm, farm_id)
        if farm and farm.latitude and farm.longitude:
            lat, lon = farm.latitude, farm.longitude
    if lat is None or lon is None:
        lat, lon = 30.81, 73.45
    data = await weather_service.get_forecast_open_meteo(lat, lon, forecast_days=days)
    return {"status": "success", "latitude": lat, "longitude": lon, "source": "open-meteo", "data": data}


@router.get("/forecast/{farm_id}")
async def get_weather_forecast(
    farm_id: int,
    days: int = 7,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch live weather forecast for a farm from Open-Meteo."""
    farm = _get_farm_or_404(db, farm_id, user.id)
    data = await weather_service.get_forecast_open_meteo(farm.latitude, farm.longitude, forecast_days=days)
    # Auto-persist current conditions embedded in forecast response
    current_data = data.get("current", {})
    if current_data:
        persist_current_weather(farm, current_data, db)
    return {"farm_id": farm_id, "source": "open-meteo", "data": data}


@router.get("/current/{farm_id}")
async def get_current_weather(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch current weather conditions for a farm."""
    farm = _get_farm_or_404(db, farm_id, user.id)
    data = await weather_service.get_current_weather_open_meteo(farm.latitude, farm.longitude)
    # Auto-persist current observation
    current_data = data.get("current", {})
    if current_data:
        persist_current_weather(farm, current_data, db)
    return {"farm_id": farm_id, "source": "open-meteo", "data": data}


@router.get("/historical/{farm_id}")
async def get_historical_weather(
    farm_id: int,
    start: str = Query(..., description="Start date YYYYMMDD"),
    end: str = Query(..., description="End date YYYYMMDD"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch historical climate data from NASA POWER."""
    farm = _get_farm_or_404(db, farm_id, user.id)
    data = await weather_service.get_historical_nasa_power(
        farm.latitude, farm.longitude, start, end
    )
    return {"farm_id": farm_id, "source": "nasa-power", "data": data}


@router.get("/records/{farm_id}", response_model=list[WeatherRecordResponse])
def get_stored_weather(
    farm_id: int,
    days_back: int = Query(default=7, ge=1, le=365),
    limit: int = Query(default=100, ge=1, le=1000),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get stored weather records for a farm, with optional time-range filter."""
    _get_farm_or_404(db, farm_id, user.id)
    since = datetime.datetime.utcnow() - datetime.timedelta(days=days_back)
    return (
        db.query(WeatherRecord)
        .filter(WeatherRecord.farm_id == farm_id, WeatherRecord.timestamp >= since)
        .order_by(WeatherRecord.timestamp.desc())
        .limit(limit)
        .all()
    )


async def _compute_monthly_summaries(lat: float, lon: float) -> list[dict]:
    """Query NASA POWER for the past 12 months and compute per-month summaries."""
    today = datetime.date.today()
    results = []
    for i in range(12):
        # Walk backwards month by month
        month_offset = i + 1
        year = today.year
        month = today.month - month_offset
        while month <= 0:
            month += 12
            year -= 1
        start = f"{year}{month:02}01"
        # End of month: use 28th to avoid edge cases
        end = f"{year}{month:02}28"
        try:
            data = await weather_service.get_historical_nasa_power(lat, lon, start, end)
            params = data.get("properties", {}).get("parameter", {})
            t2m = params.get("T2M", {})
            rh = params.get("RH2M", {})
            precip = params.get("PRECTOTCORR", {})

            def _safe_mean(d: dict) -> float | None:
                vals = [float(v) for v in d.values() if float(v) != -999.0]
                return round(sum(vals) / len(vals), 2) if vals else None

            def _safe_sum(d: dict) -> float | None:
                vals = [float(v) for v in d.values() if float(v) != -999.0]
                return round(sum(vals), 1) if vals else None

            results.append({
                "month": f"{year}-{month:02}",
                "mean_temp_c": _safe_mean(t2m),
                "mean_humidity_pct": _safe_mean(rh),
                "total_precip_mm": _safe_sum(precip),
            })
        except Exception:
            results.append({
                "month": f"{year}-{month:02}",
                "mean_temp_c": None,
                "mean_humidity_pct": None,
                "total_precip_mm": None,
            })
    results.reverse()
    return results


@router.get("/climate/{farm_id}")
async def get_climate_summary(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return current anomaly, 12-month monthly summaries, and anomaly history."""
    farm = _get_farm_or_404(db, farm_id, user.id)
    # Current conditions for anomaly computation
    current = await weather_service.get_current_weather_open_meteo(farm.latitude, farm.longitude)
    cur = current.get("current", {})
    anomaly = await weather_service.get_climate_anomaly(
        farm.latitude, farm.longitude,
        current_temp=cur.get("temperature_2m"),
        current_humidity=cur.get("relative_humidity_2m"),
    )
    # 12-month monthly summaries from NASA POWER
    monthly = await _compute_monthly_summaries(farm.latitude, farm.longitude)
    # Persisted anomaly history
    snapshots = (
        db.query(ClimateSnapshot)
        .filter(ClimateSnapshot.farm_id == farm_id)
        .order_by(ClimateSnapshot.created_at.desc())
        .limit(24)
        .all()
    )
    return {
        "farm_id": farm_id,
        "current_anomaly": anomaly,
        "monthly_summaries": monthly,
        "anomaly_history": [ClimateSnapshotResponse.model_validate(s) for s in snapshots],
    }
