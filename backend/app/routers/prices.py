"""AgriTwin AI Router — /api/v1/prices Endpoints.
Crop Price Intelligence Engine — tracks current and predicted prices independently by crop_id.
"""

import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.market_price_service import market_price_service
from app.services.price_prediction_engine import price_prediction_engine
from app.core.engine import crop_knowledge

router = APIRouter(prefix="/prices", tags=["crop_prices"])


@router.get("/{crop_id}")
async def get_crop_prices_by_id(
    crop_id: str,
    district: str | None = Query(None, description="Optional Punjab / Pakistan district filter"),
    province: str | None = Query("Punjab", description="Province"),
    db: Session = Depends(get_db),
):
    """
    Fetch current & historical wholesale market rates for a specific crop_id (e.g. WHEAT_001).
    Decoupled endpoint for market price tracking. Persists to `crop_market_prices` DB table.
    """
    standard_crop_name = crop_knowledge.get_crop_name(crop_id)
    canonical_crop_id = crop_knowledge.get_crop_id(crop_id)

    # Fetch live price feed
    live_prices_res = await market_price_service.fetch_live_commodity_prices(district=district, db=db)
    
    # Filter for target crop
    crop_prices_matching = [
        p for p in live_prices_res.get("prices", [])
        if p.get("crop_id") == canonical_crop_id or p.get("crop", "").lower() == standard_crop_name.lower()
    ]

    market_analysis = market_price_service.analyze_crop_market(crop_name=standard_crop_name)

    return {
        "crop_id": canonical_crop_id,
        "crop_name": standard_crop_name,
        "district": district or "Punjab All Mandis",
        "province": province or "Punjab",
        "currency": "PKR",
        "unit_maund": "40 kg (maund)",
        "unit_100kg": "100 kg",
        "current_market_rates": crop_prices_matching[0] if crop_prices_matching else {
            "crop_id": canonical_crop_id,
            "crop": standard_crop_name,
            "avg_pkr_40kg": market_analysis.get("average_mandi_rate_pkr", 3850),
            "avg_pkr_100kg": round(market_analysis.get("average_mandi_rate_pkr", 3850) * 2.5, 2),
        },
        "market_analysis": market_analysis,
        "data_source": live_prices_res.get("data_source"),
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@router.get("/{crop_id}/history")
async def get_crop_price_history(
    crop_id: str,
    district: str | None = Query(None, description="Optional Punjab district filter"),
    days_back: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Fetch historical price trend points & records for a crop_id."""
    standard_crop_name = crop_knowledge.get_crop_name(crop_id)
    canonical_crop_id = crop_knowledge.get_crop_id(crop_id)
    market_analysis = market_price_service.analyze_crop_market(crop_name=standard_crop_name)

    from app.models import CropMarketPrice
    history_records = (
        db.query(CropMarketPrice)
        .filter(CropMarketPrice.crop_id == canonical_crop_id)
        .order_by(CropMarketPrice.date.desc())
        .limit(days_back)
        .all()
    )

    return {
        "crop_id": canonical_crop_id,
        "crop_name": standard_crop_name,
        "district": district or "Punjab All Mandis",
        "current_avg_pkr_40kg": market_analysis.get("average_mandi_rate_pkr"),
        "trend_7d_pct": market_analysis.get("trend_7d_pct"),
        "trend_30d_pct": market_analysis.get("trend_30d_pct"),
        "trend_90d_pct": market_analysis.get("trend_90d_pct"),
        "trend_yoy_pct": market_analysis.get("trend_yoy_pct"),
        "history_count": len(history_records),
        "history": [
            {
                "date": r.date.isoformat() if hasattr(r.date, "isoformat") else str(r.date),
                "avg_price_pkr_40kg": r.average_price_pkr_40kg,
                "avg_price_pkr_100kg": r.average_price_pkr_100kg,
                "district": r.district,
                "market": r.market,
            }
            for r in history_records
        ],
    }


@router.get("/{crop_id}/forecast")
def get_crop_price_forecast_by_id(
    crop_id: str,
    district: str | None = Query("Gujrat", description="District name"),
    market: str | None = Query(None, description="Local mandi name"),
    current_price: float | None = Query(None, description="Current price per 100kg (optional)"),
    temp_c: float = Query(28.0, description="Temperature °C"),
    humidity_pct: float = Query(55.0, description="Humidity %"),
    db: Session = Depends(get_db),
):
    """
    Computes ML price predictions (7d, 14d, 30d) by crop_id (e.g. WHEAT_001).
    Decoupled price prediction endpoint using GradientBoosting architecture.
    Persists forecast to `crop_price_predictions` DB table.
    """
    standard_crop_name = crop_knowledge.get_crop_name(crop_id)
    canonical_crop_id = crop_knowledge.get_crop_id(crop_id)

    forecast_res = price_prediction_engine.forecast_price(
        crop_name=standard_crop_name,
        district=district or "Gujrat",
        market=market or f"{district or 'Gujrat'} Mandi",
        current_price_100kg=current_price,
        temperature_c=temp_c,
        humidity_pct=humidity_pct,
        db=db,
    )

    forecast_res["crop_id"] = canonical_crop_id
    forecast_res["crop_name"] = standard_crop_name

    return forecast_res
