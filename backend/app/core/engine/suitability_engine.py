"""Crop Suitability Engine — AgriTwin AI (9-Factor Architecture)

Evaluates farm-level land suitability across 9 Core Factors:
1. Season Score (20%)
2. Planting Window Score (15%)
3. Weather (Climate) Score (15%)
4. Soil Score (15%)
5. Water Score (10%)
6. Disease Risk Score (5%)
7. Expected Yield Score (5%)
8. Market Price Score (5%)
9. Expected Profit Score (10%)

Total = 100%
"""

import datetime
import json
from pathlib import Path
from typing import Any
from app.core.engine.crop_knowledge import CROP_KNOWLEDGE_BASE, get_crop_info

# Baseline crop agronomic & economic profile benchmarks (Punjab 2026)
CROP_ECONOMIC_PROFILES = {
    "Wheat": {
        "expected_yield_maunds_acre": 42.0,
        "cost_per_maund_pkr": 2000.0,
        "base_price_pkr_maund": 3850.0,
    },
    "Rice (Basmati)": {
        "expected_yield_maunds_acre": 38.0,
        "cost_per_maund_pkr": 4200.0,
        "base_price_pkr_maund": 9100.0,
    },
    "Rice (Coarse)": {
        "expected_yield_maunds_acre": 50.0,
        "cost_per_maund_pkr": 2100.0,
        "base_price_pkr_maund": 3500.0,
    },
    "Cotton": {
        "expected_yield_maunds_acre": 25.0,
        "cost_per_maund_pkr": 6200.0,
        "base_price_pkr_maund": 8675.0,
    },
    "Sugarcane": {
        "expected_yield_maunds_acre": 750.0,
        "cost_per_maund_pkr": 1800.0,
        "base_price_pkr_maund": 2910.0,
    },
    "Maize": {
        "expected_yield_maunds_acre": 55.0,
        "cost_per_maund_pkr": 2200.0,
        "base_price_pkr_maund": 3495.0,
    },
    "Potato": {
        "expected_yield_maunds_acre": 250.0,
        "cost_per_maund_pkr": 1400.0,
        "base_price_pkr_maund": 2650.0,
    },
    "Canola / Mustard": {
        "expected_yield_maunds_acre": 22.0,
        "cost_per_maund_pkr": 3800.0,
        "base_price_pkr_maund": 6650.0,
    },
    "Gram (Chickpea)": {
        "expected_yield_maunds_acre": 18.0,
        "cost_per_maund_pkr": 5000.0,
        "base_price_pkr_maund": 9350.0,
    },
    "Sunflower": {
        "expected_yield_maunds_acre": 20.0,
        "cost_per_maund_pkr": 4500.0,
        "base_price_pkr_maund": 7350.0,
    },
    "Mango": {
        "expected_yield_maunds_acre": 120.0,
        "cost_per_maund_pkr": 3200.0,
        "base_price_pkr_maund": 7000.0,
    },
    "Citrus (Kinnow)": {
        "expected_yield_maunds_acre": 150.0,
        "cost_per_maund_pkr": 2500.0,
        "base_price_pkr_maund": 5000.0,
    },
    "Barley": {
        "expected_yield_maunds_acre": 30.0,
        "cost_per_maund_pkr": 2000.0,
        "base_price_pkr_maund": 3000.0,
    },
    "Lentil": {
        "expected_yield_maunds_acre": 15.0,
        "cost_per_maund_pkr": 4800.0,
        "base_price_pkr_maund": 8500.0,
    },
    "Peas": {
        "expected_yield_maunds_acre": 40.0,
        "cost_per_maund_pkr": 3000.0,
        "base_price_pkr_maund": 4500.0,
    },
}


def load_crop_calendar() -> list[dict[str, Any]]:
    """Load crop calendar database from JSON file."""
    calendar_file = Path(__file__).resolve().parent.parent.parent / "data" / "crop_calendar.json"
    if calendar_file.exists():
        try:
            with open(calendar_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


CROP_CALENDAR = load_crop_calendar()


def get_crop_calendar_entry(crop_name: str) -> dict[str, Any] | None:
    """Retrieve crop calendar details for a crop by name."""
    cn_lower = str(crop_name).strip().lower()
    for entry in CROP_CALENDAR:
        c_entry_lower = entry.get("crop", "").strip().lower()
        if c_entry_lower in cn_lower or cn_lower in c_entry_lower:
            return entry
    return None


def calculate_soil_suitability(
    crop_name: str,
    ph: float | None = None,
    organic_carbon_g_kg: float | None = None,
    clay_pct: float | None = None,
    sand_pct: float | None = None,
    silt_pct: float | None = None,
) -> tuple[int, list[str], list[str]]:
    """
    Calculate soil suitability score (0-100), limiting factors, and management recommendations.
    """
    score = 100
    limits: list[str] = []
    recs: list[str] = []

    # 1. pH evaluation
    calendar_entry = get_crop_calendar_entry(crop_name)
    ph_min = calendar_entry.get("soil_ph_min", 6.0) if calendar_entry else 6.0
    ph_max = calendar_entry.get("soil_ph_max", 8.0) if calendar_entry else 8.0

    if ph is not None:
        if ph < ph_min:
            score -= 30
            limits.append(f"Soil pH ({ph:.1f}) is below optimal minimum ({ph_min:.1f}) for {crop_name}")
            recs.append("Apply agricultural lime (calcium carbonate) to raise soil pH")
        elif ph > ph_max:
            score -= 30
            limits.append(f"High soil alkalinity/salinity risk (pH {ph:.1f} exceeds optimal maximum {ph_max:.1f} for {crop_name})")
            recs.append("Apply agricultural gypsum (CaSO4) and leaching irrigation to mitigate alkalinity")
        elif ph > 7.8 and ph_max <= 7.8:
            score -= 10
            limits.append(f"Slightly alkaline soil (pH {ph:.1f})")
            recs.append("Use ammonium-based nitrogen fertilizers to gradually buffer soil pH")

    # 2. Organic Carbon
    if organic_carbon_g_kg is not None:
        if organic_carbon_g_kg < 4.0:
            score -= 25
            limits.append(f"Very low organic carbon content ({organic_carbon_g_kg:.1f} g/kg)")
            recs.append("Incorporate 5-10 tonnes/acre of well-rotted farmyard manure (FYM) or green manure")
        elif organic_carbon_g_kg < 7.0:
            score -= 10
            limits.append(f"Moderate organic carbon content ({organic_carbon_g_kg:.1f} g/kg)")
            recs.append("Practice minimum tillage and crop residue retention to build soil organic matter")

    # 3. Soil Texture & Water Capacity suitability
    c_lower = crop_name.lower()
    if clay_pct is not None and sand_pct is not None:
        if "rice" in c_lower or "basmati" in c_lower:
            if clay_pct < 20:
                score -= 30
                limits.append(f"Soil has low clay content ({clay_pct:.0f}%), risking excessive water percolation")
                recs.append("Ensure thorough puddling (hardpan creation) before rice transplanting")
        elif "cotton" in c_lower:
            if clay_pct > 50:
                score -= 25
                limits.append(f"Heavy clay soil ({clay_pct:.0f}%) may cause waterlogging and root restriction")
                recs.append("Improve field drainage and plant on raised beds/ridges")
            elif sand_pct > 70:
                score -= 20
                limits.append(f"High sand content ({sand_pct:.0f}%) reduces nutrient and water retention")
                recs.append("Apply split fertilizer applications and frequent light irrigations")
        elif "wheat" in c_lower or "maize" in c_lower:
            if sand_pct > 75:
                score -= 20
                limits.append(f"Excessively sandy soil ({sand_pct:.0f}%) limits moisture holding capacity")
                recs.append("Use organic mulching and frequent light irrigation schedules")

    return max(0, min(100, round(score))), limits, recs


def calculate_climate_suitability(
    crop_info: dict,
    temp_c: float | None = None,
    humidity_pct: float | None = None,
) -> tuple[int, list[str], list[str]]:
    """
    Calculate climate/weather suitability score (0-100) against temperature and humidity bounds.
    """
    score = 100
    limits: list[str] = []
    recs: list[str] = []

    opt_temp = crop_info.get("optimal_temperature_c", {})
    t_min = opt_temp.get("min", 10)
    t_max = opt_temp.get("max", 35)
    t_crit = opt_temp.get("critical_high", 40)

    if temp_c is not None:
        if temp_c > t_crit:
            score -= 40
            limits.append(f"Extreme heat stress risk: current temp {temp_c:.1f}°C exceeds critical threshold ({t_crit}°C)")
            recs.append("Apply micro-irrigation/sprinklers during peak afternoon heat to suppress canopy temperature")
        elif temp_c > t_max:
            score -= 20
            limits.append(f"Temperature ({temp_c:.1f}°C) is above optimal range ({t_min}-{t_max}°C)")
            recs.append("Ensure adequate soil moisture to prevent heat-induced transpiration stress")
        elif temp_c < t_min:
            score -= 30
            limits.append(f"Cold temperature ({temp_c:.1f}°C) is below minimum growth threshold ({t_min}°C)")
            recs.append("Delay planting until temperature warms or protect seedling beds")

    if humidity_pct is not None and humidity_pct > 85 and temp_c and temp_c > 28:
        score -= 15
        limits.append("High humidity and temperature create elevated fungal pest/blight risk")
        recs.append("Monitor closely for fungal pathogens (e.g. Rust/Blast) and apply preventative bio-fungicides")

    return max(0, min(100, round(score))), limits, recs


def calculate_water_suitability(
    crop_info: dict,
    canal_name: str | None = None,
    canal_turn_hours: float | None = None,
    tubewell_power: str | None = None,
    rainfall_mm: float | None = None,
) -> tuple[int, list[str], list[str]]:
    """
    Calculate water asset & availability suitability score (0-100).
    """
    score = 100
    limits: list[str] = []
    recs: list[str] = []

    water_req = crop_info.get("water_requirement_mm", 500)
    has_canal = bool(canal_name and (canal_turn_hours or 0) > 0)
    has_tubewell = bool(tubewell_power and tubewell_power.lower() != "none")

    if water_req >= 1000:
        if not has_canal and not has_tubewell:
            score -= 60
            limits.append(f"High crop water requirement ({water_req}mm) without secure canal or tubewell access")
            recs.append("Switch to lower water-demand crops (e.g. Maize, Pulses) or install tubewell/drip system")
        elif not has_canal and has_tubewell:
            score -= 20
            limits.append(f"Reliance purely on tubewell irrigation increases operational energy costs for {water_req}mm requirement")
            recs.append("Adopt Alternate Wetting and Drying (AWD) irrigation technique to save up to 30% water")
        elif has_canal and (canal_turn_hours or 0) < 3.0:
            score -= 15
            limits.append(f"Canal turn duration ({canal_turn_hours} hrs) may be insufficient for high demand ({water_req}mm)")
            recs.append("Supplement canal water with solar-powered tubewell pumping during critical growth stages")
    elif water_req >= 600:
        if not has_canal and not has_tubewell:
            score -= 40
            limits.append(f"Moderate water requirement ({water_req}mm) lacks reliable irrigation sources")
            recs.append("Secure tubewell access or rain-harvesting storage before sowing")
    else:
        if not has_canal and not has_tubewell and (rainfall_mm or 0) < 200:
            score -= 25
            limits.append("Low rainfall zone with limited irrigation assets")
            recs.append("Utilize moisture conservation techniques like zero-tillage and straw mulching")

    return max(0, min(100, round(score))), limits, recs


def calculate_season_suitability(
    crop_info: dict,
    month: int | None = None,
    ref_date: datetime.date | None = None,
) -> tuple[int, list[str], list[str]]:
    """
    Evaluate seasonal sowing window suitability based on current month (1-12) or ref_date.
    """
    if month is None:
        if ref_date:
            month = ref_date.month
        else:
            month = datetime.date.today().month
    else:
        try:
            month = max(1, min(12, int(month)))
        except (ValueError, TypeError):
            month = datetime.date.today().month

    crop_name = crop_info.get("crop", "")
    score = 100
    limits: list[str] = []
    recs: list[str] = []

    calendar_entry = get_crop_calendar_entry(crop_name)
    if calendar_entry and "planting_window" in calendar_entry:
        p_win = calendar_entry["planting_window"]
        season_name = calendar_entry.get("season", "Season")
        try:
            start_m = int(p_win["start"].split("-")[0])
            end_m = int(p_win["end"].split("-")[0])

            sowing_months = set()
            m_curr = start_m
            while True:
                sowing_months.add(m_curr)
                if m_curr == end_m:
                    break
                m_curr = (m_curr % 12) + 1

            shoulder_months = set()
            for sm in sowing_months:
                shoulder_months.add(((sm - 2) % 12) + 1)
                shoulder_months.add((sm % 12) + 1)
            shoulder_months -= sowing_months

            if month in sowing_months:
                score = 100
            elif month in shoulder_months:
                score = 70
                limits.append(f"Month {month} is marginal/shoulder for {crop_name} {season_name} sowing window")
                recs.append(f"Select appropriate short-duration variety suited for early/late {season_name} sowing")
            else:
                score = 25
                limits.append(f"Month {month} is completely outside the {crop_name} {season_name} sowing window")
                recs.append(f"Do not sow {crop_name} now; wait for its recommended {season_name} planting window")
            return max(0, min(100, round(score))), limits, recs
        except Exception:
            pass

    cn_lower = crop_name.lower()
    if "wheat" in cn_lower:
        if month in [10, 11, 12, 1]:
            score = 100
        elif month in [9, 2]:
            score = 70
            limits.append(f"Month {month} is marginal for Wheat sowing window (Oct 15 - Dec 15)")
            recs.append("Use short-duration or heat-tolerant Wheat varieties (e.g. Akbar-19)")
        else:
            score = 25
            limits.append(f"Month {month} is completely outside the Wheat Rabi sowing window")
            recs.append("Do not sow Wheat now; prepare land for Kharif crops instead")
    elif "rice" in cn_lower:
        if month in [5, 6, 7]:
            score = 100
        elif month in [4, 8]:
            score = 65
            limits.append(f"Month {month} is off-peak for Rice nursery/transplanting")
            recs.append("Ensure nursery preparation timing aligns with recommended transplanting window")
        else:
            score = 20
            limits.append(f"Month {month} is outside the Kharif Rice season")
            recs.append("Consider Rabi crops like Wheat or Canola for the current season")
    elif "cotton" in cn_lower:
        if month in [4, 5, 6]:
            score = 100
        elif month in [3, 7]:
            score = 70
            limits.append(f"Month {month} is early/late for Cotton sowing (Optimal: Apr 15 - Jun 30)")
            recs.append("Select early-maturing Bt Cotton hybrids to avoid end-of-season bollworm stress")
        else:
            score = 25
            limits.append(f"Month {month} is outside Cotton sowing window")
            recs.append("Wait for April spring/Kharif window or plant an in-season crop")
    elif "sugarcane" in cn_lower:
        if month in [2, 3, 9, 10]:
            score = 100
        elif month in [1, 4, 8]:
            score = 75
            limits.append(f"Month {month} is secondary sowing window for Sugarcane")
            recs.append("Ensure sufficient soil warmth and seed cane treatment before planting")
        else:
            score = 45
            limits.append(f"Month {month} is off-season for Sugarcane planting")
    elif "maize" in cn_lower:
        if month in [2, 3, 7, 8]:
            score = 100
        elif month in [1, 4, 6, 9]:
            score = 70
            limits.append(f"Month {month} is on the shoulder of Maize sowing windows")
        else:
            score = 35
            limits.append(f"Month {month} is outside peak Maize sowing windows")
    else:
        score = 80

    return max(0, min(100, round(score))), limits, recs


class PlantingWindowResult(tuple):
    """Result tuple that unpacks as (score, days_until_window, status) for backward compatibility,
    while exposing days_remaining_in_window and days_since_window as attributes."""
    def __new__(cls, score: int, days_until: int, status: str, days_remaining: int = 0, days_since: int = 0):
        obj = super().__new__(cls, (score, days_until, status))
        obj.score = score
        obj.days_until_window = days_until
        obj.status = status
        obj.days_remaining_in_window = days_remaining
        obj.days_since_window = days_since
        return obj


def calculate_planting_window_status(
    crop_name: str,
    ref_date: datetime.date | None = None,
    province: str | None = "Punjab",
) -> PlantingWindowResult:
    """
    Calculates planting window score (100, 80, 60, 50, 20, 0), days_until_window,
    days_remaining_in_window, days_since_window, and status:
    PLANT NOW 🟢, PREPARE NOW 🟡, WAIT 🔵, LATE SOWING 🟡, NOT RECOMMENDED 🔴
    Supports Pakistani agricultural zones (Punjab, Sindh, KPK, Balochistan, AJK/GB).
    """
    from app.core.engine.crop_knowledge import get_crop_id, REGION_PLANTING_WINDOWS, AGRICULTURAL_ZONES, normalize_province

    if ref_date is None:
        ref_date = datetime.date.today()

    crop_id = get_crop_id(crop_name)
    prov = normalize_province(province)

    calendar_entry = get_crop_calendar_entry(crop_name)
    is_known_crop = any(
        entry["crop"].lower() in crop_name.lower() or crop_name.lower() in entry["crop"].lower()
        for entry in CROP_KNOWLEDGE_BASE
    )

    if is_known_crop and crop_id in REGION_PLANTING_WINDOWS and prov in REGION_PLANTING_WINDOWS[crop_id]:
        win = REGION_PLANTING_WINDOWS[crop_id][prov]
        start_str = win.get("start", "10-15")
        end_str = win.get("end", "12-15")
    elif calendar_entry and "planting_window" in calendar_entry:
        window = calendar_entry["planting_window"]
        start_str = window.get("start", "10-15")
        end_str = window.get("end", "12-15")
    elif crop_id in REGION_PLANTING_WINDOWS and prov in REGION_PLANTING_WINDOWS[crop_id]:
        win = REGION_PLANTING_WINDOWS[crop_id][prov]
        start_str = win.get("start", "10-15")
        end_str = win.get("end", "12-15")
    else:
        start_str, end_str = "10-15", "12-15"

    try:
        start_m, start_d = map(int, start_str.split("-"))
        end_m, end_d = map(int, end_str.split("-"))
    except Exception:
        start_m, start_d, end_m, end_d = 10, 15, 12, 15

    ref_year = ref_date.year
    candidate_windows = []
    for y_offset in (-1, 0, 1, 2):
        w_start = datetime.date(ref_year + y_offset, start_m, start_d)
        if start_m <= end_m:
            w_end = datetime.date(ref_year + y_offset, end_m, end_d)
        else:
            w_end = datetime.date(ref_year + y_offset + 1, end_m, end_d)
        candidate_windows.append((w_start, w_end))

    for w_start, w_end in candidate_windows:
        if w_start <= ref_date <= w_end:
            days_rem = (w_end - ref_date).days
            return PlantingWindowResult(100, 0, "PLANT NOW 🟢", days_remaining=days_rem, days_since=0)

    future_starts = [ws for ws, we in candidate_windows if ws > ref_date]
    past_ends = [we for ws, we in candidate_windows if we < ref_date]

    next_w_start = min(future_starts) if future_starts else datetime.date(ref_year + 1, start_m, start_d)
    prev_w_end = max(past_ends) if past_ends else datetime.date(ref_year - 1, end_m, end_d)

    days_until_window = (next_w_start - ref_date).days
    days_past = (ref_date - prev_w_end).days

    if days_past <= 15:
        planting_window_score = 60
        status = "LATE SOWING 🟡"
        days_rem = 0
        days_since = days_past
    elif days_past <= 30:
        planting_window_score = 40
        status = "LATE SOWING 🟡"
        days_rem = 0
        days_since = days_past
    else:
        days_since = days_past
        days_rem = 0
        if days_until_window <= 30:
            planting_window_score = 80
            status = "PREPARE NOW 🟡"
        elif days_until_window <= 60:
            planting_window_score = 50
            status = "WAIT 🔵"
        elif days_until_window <= 90:
            planting_window_score = 20
            status = "WAIT 🔵"
        else:
            planting_window_score = 0
            status = "NOT RECOMMENDED 🔴"

    return PlantingWindowResult(planting_window_score, days_until_window, status, days_remaining=days_rem, days_since=days_since)


def calculate_market_suitability(
    crop_name: str,
    price_forecast_data: dict | None = None,
) -> tuple[int, list[str], list[str]]:
    """
    Evaluate Market Score (0-100) based on price trend direction and expected price appreciation.
    """
    limits: list[str] = []
    recs: list[str] = []

    if not price_forecast_data:
        return 78, limits, recs

    direction = price_forecast_data.get("direction", "stable").lower()
    change_30d_pct = price_forecast_data.get("price_change_30d_pct", 0.0)

    if direction == "bullish" or change_30d_pct > 3.0:
        score = 88
        recs.append(f"Market trend is positive ({change_30d_pct:+.1f}% 30-day forecast). Harvest timing is favorable.")
    elif direction == "bearish" or change_30d_pct < -3.0:
        score = 65
        limits.append(f"Market prices expected to soften ({change_30d_pct:+.1f}% 30-day forecast)")
        recs.append("Plan post-harvest warehouse storage or contract forward selling to mitigate price decline")
    else:
        score = 78
        recs.append("Market prices are stable with steady wholesale demand in Punjab mandis")

    return score, limits, recs


def calculate_profit_suitability(
    expected_gross_margin_pkr_acre: float,
) -> tuple[int, list[str], list[str]]:
    """
    Evaluate Profit Score (0-100) based on expected gross margin per acre.
    """
    limits: list[str] = []
    recs: list[str] = []

    if expected_gross_margin_pkr_acre >= 150000:
        score = 92
        recs.append(f"High profit potential: expected gross margin PKR {expected_gross_margin_pkr_acre:,.0f} / acre")
    elif expected_gross_margin_pkr_acre >= 100000:
        score = 84
        recs.append(f"Strong financial returns: expected gross margin PKR {expected_gross_margin_pkr_acre:,.0f} / acre")
    elif expected_gross_margin_pkr_acre >= 50000:
        score = 75
        recs.append(f"Moderate gross margin: PKR {expected_gross_margin_pkr_acre:,.0f} / acre")
    else:
        score = 60
        limits.append(f"Low expected gross margin (PKR {expected_gross_margin_pkr_acre:,.0f} / acre)")
        recs.append("Optimize input efficiency (seed, fertilizer) to improve profit margins")

    return score, limits, recs


def calculate_disease_risk_suitability(
    crop_name: str,
    temp_c: float | None = None,
    humidity_pct: float | None = None,
) -> tuple[int, list[str], list[str]]:
    """
    Evaluate Disease Risk Score (0-100) based on microclimate pest/pathogen pressure.
    """
    score = 90
    limits: list[str] = []
    recs: list[str] = []

    if temp_c is not None and humidity_pct is not None:
        if humidity_pct > 80 and 22 <= temp_c <= 32:
            score -= 25
            limits.append("Elevated risk of fungal blight and pest outbreaks due to high humidity and warm temperatures")
            recs.append("Implement proactive crop monitoring and bio-fungicide sprays")
        elif humidity_pct > 70:
            score -= 10
            limits.append("Moderate humidity levels present slight pest pressure risk")

    return max(0, min(100, score)), limits, recs


def calculate_yield_suitability(
    crop_name: str,
    soil_score: int,
    climate_score: int,
    water_score: int,
) -> tuple[int, list[str], list[str]]:
    """
    Evaluate Expected Yield Score (0-100) based on agronomic land suitability.
    """
    avg_score = (soil_score + climate_score + water_score) / 3.0
    if avg_score >= 85:
        score = 95
    elif avg_score >= 70:
        score = 85
    elif avg_score >= 50:
        score = 65
    else:
        score = 45

    return score, [], []


def generate_crop_timeline(crop_name: str, ref_date: datetime.date) -> list[dict[str, Any]]:
    """
    Generates a structured crop lifecycle timeline.
    """
    cn_lower = crop_name.lower()
    if "wheat" in cn_lower or "barley" in cn_lower:
        return [
            {"stage": "Pre-Sowing & Land Prep", "days": "Oct 15 - Nov 10", "description": "Deep plowing, FYM application, and Rauni irrigation."},
            {"stage": "Optimal Sowing Window", "days": "Nov 01 - Nov 25", "description": "Certified seed sowing with seed drill & DAP application."},
            {"stage": "Crown Root Initiation (CRI)", "days": "Day 20 - 25", "description": "First critical irrigation + first split urea application."},
            {"stage": "Tillering & Flowering", "days": "Day 45 - 85", "description": "Second irrigation + weed control + rust monitoring."},
            {"stage": "Grain Filling & Maturity", "days": "Day 90 - 130", "description": "Final light irrigation + combined harvesting."},
        ]
    elif "rice" in cn_lower:
        return [
            {"stage": "Nursery Preparation", "days": "May 20 - Jun 15", "description": "Seed soaking, seedbed sowing, and moisture maintenance."},
            {"stage": "Field Puddling & Transplanting", "days": "Jun 15 - Jul 20", "description": "Land puddling, 25-day seedling transplanting, zinc sulphate."},
            {"stage": "Tillering & Panicle Initiation", "days": "Jul 25 - Sep 15", "description": "AWD irrigation cycle, nitrogen top-dressing."},
            {"stage": "Heading & Grain Maturity", "days": "Sep 15 - Oct 30", "description": "Water draining 15 days before harvest, combined harvesting."},
        ]
    elif "cotton" in cn_lower:
        return [
            {"stage": "Land Preparation", "days": "Apr 01 - Apr 30", "description": "Ridge formation, pre-sowing irrigation."},
            {"stage": "Sowing & Germination", "days": "Apr 15 - Jun 15", "description": "Delinted seed sowing, seedling thinning."},
            {"stage": "Square & Boll Formation", "days": "Jun 15 - Aug 31", "description": "Pest scouting (Whitefly, Pink Bollworm), split N application."},
            {"stage": "Boll Opening & Picking", "days": "Sep 01 - Dec 15", "description": "Manual cotton picking in clean dry weather."},
        ]
    elif "potato" in cn_lower:
        return [
            {"stage": "Land Preparation & Ridging", "days": "Sep 15 - Oct 10", "description": "Soil tilling, organic manure incorporation, ridge making."},
            {"stage": "Tuber Sowing", "days": "Oct 01 - Oct 31", "description": "Planting disease-free seed tubers on ridges."},
            {"stage": "Tuber Initiation & Earthing-up", "days": "Day 30 - 50", "description": "Earthing up ridges, nitrogen application, irrigation."},
            {"stage": "Tuber Bulking & Harvest", "days": "Dec 15 - Feb 28", "description": "Late blight scouting, haulm cutting, mechanical digging."},
        ]
    elif "canola" in cn_lower or "mustard" in cn_lower:
        return [
            {"stage": "Land Preparation", "days": "Sep 15 - Oct 01", "description": "Fine seedbed preparation, basal phosphorus fertilizer."},
            {"stage": "Sowing & Rosette Stage", "days": "Oct 01 - Nov 15", "description": "Line sowing, seedling thinning, early irrigation."},
            {"stage": "Flowering & Podging", "days": "Dec 01 - Jan 31", "description": "Aphid scouting, nitrogen top-dressing during flowering."},
            {"stage": "Pod Filling & Harvesting", "days": "Feb 15 - Mar 31", "description": "Timely harvesting when 75% pods turn golden brown."},
        ]
    elif "gram" in cn_lower or "chickpea" in cn_lower or "lentil" in cn_lower or "peas" in cn_lower:
        return [
            {"stage": "Land Preparation", "days": "Sep 20 - Oct 10", "description": "Moisture conservation plowing, basal DAP application."},
            {"stage": "Sowing & Germination", "days": "Oct 01 - Nov 15", "description": "Rhizobium inoculant treated seed sowing."},
            {"stage": "Vegetative & Flowering", "days": "Nov 20 - Jan 31", "description": "Weed management, pod borer pest scouting."},
            {"stage": "Pod Development & Harvest", "days": "Feb 15 - Apr 30", "description": "Threshing and storage at <10% seed moisture."},
        ]
    else:
        return [
            {"stage": "Land Preparation", "days": "Pre-sowing", "description": "Soil leveling and basal fertilizer application."},
            {"stage": "Sowing / Planting", "days": "Day 0 - 15", "description": "Planting at recommended depth and row spacing."},
            {"stage": "Vegetative Growth", "days": "Day 15 - 60", "description": "Irrigation, weed control, and pest scouting."},
            {"stage": "Harvesting", "days": "Maturity", "description": "Timely harvesting and mandi transport."},
        ]


def generate_todays_farm_actions(
    crop_name: str,
    status: str,
    days_until_window: int,
    limiting_factors: list[str],
) -> list[str]:
    """
    Generates actionable farm checklist items for today based on crop status.
    """
    cn_lower = crop_name.lower()

    if "PLANT" in status:
        actions = [
            f"Begin sowing {crop_name} immediately in the optimal planting window.",
            "Treat certified seeds with recommended fungicide/insecticide prior to sowing.",
            "Ensure field moisture (Rauni) is adequate for uniform seed germination.",
            "Apply 1 bag DAP / acre as basal dose during final seedbed preparation.",
        ]
    elif "PREPARE" in status:
        actions = [
            f"Prepare field for upcoming {crop_name} sowing window ({days_until_window} days remaining).",
            "Perform deep plowing and land leveling to ensure even water distribution.",
            "Procure certified high-yielding seed varieties and basal fertilizers.",
            "Verify canal turn (Warabandi) timing for pre-sowing irrigation.",
        ]
    elif "WAIT" in status:
        actions = [
            f"{crop_name} sowing window opens in {days_until_window} days. Hold sowing.",
            "Complete harvesting and residue management of the current standing crop.",
            "Conduct soil sampling for pH, organic matter, and NPK nutrient testing.",
        ]
    else:
        actions = [
            f"{crop_name} is currently off-season or unsuitable for sowing today.",
            "Review alternative in-season crop options for current month.",
            "Maintain soil cover or plan green manure crop to preserve field health.",
        ]

    if limiting_factors:
        actions.append(f"Remediate key limitation: {limiting_factors[0]}")

    return actions[:4]


def evaluate_crop_suitability(
    crop_name: str,
    farm_data: dict[str, Any],
    soil_data: dict[str, Any] | None = None,
    weather_data: dict[str, Any] | None = None,
    month: int | None = None,
    price_forecast_data: dict | None = None,
    ref_date: datetime.date | None = None,
) -> dict[str, Any]:
    """
    Evaluates complete crop suitability across 9 factors and computes expected gross margin / acre,
    dynamic planting window, days_until_window, status, timeline, and todays_farm_action.
    """
    crop_info = get_crop_info(crop_name)
    if not crop_info:
        crop_info = {
            "crop": crop_name,
            "optimal_temperature_c": {"min": 15, "max": 32, "critical_high": 38},
            "water_requirement_mm": 500,
        }

    # Reference Date handling
    if ref_date is None:
        if month is not None:
            try:
                curr_year = datetime.date.today().year
                ref_date = datetime.date(curr_year, max(1, min(12, int(month))), 15)
            except Exception:
                ref_date = datetime.date.today()
        else:
            ref_date = datetime.date.today()

    matched_crop_key = "Wheat"
    if crop_name and str(crop_name).strip():
        cn_lower = str(crop_name).strip().lower()
        for k in CROP_ECONOMIC_PROFILES.keys():
            if k.lower() in cn_lower or cn_lower in k.lower():
                matched_crop_key = k
                break

    econ = CROP_ECONOMIC_PROFILES[matched_crop_key]

    soil_data = soil_data or {}
    weather_data = weather_data or {}

    # Soil parameters
    ph = soil_data.get("ph_topsoil")
    soc = soil_data.get("organic_carbon_g_per_kg")
    clay = soil_data.get("clay_pct")
    sand = soil_data.get("sand_pct")
    silt = soil_data.get("silt_pct")

    # Climate parameters
    current_weather = weather_data.get("current", {})
    temp_c = current_weather.get("temperature_2m") or current_weather.get("temperature_c")
    humidity_pct = current_weather.get("relative_humidity_2m") or current_weather.get("humidity_pct")
    precip_mm = current_weather.get("precipitation") or current_weather.get("rainfall_mm")

    # Water parameters
    canal_name = farm_data.get("canal_name")
    canal_turn_hrs = farm_data.get("canal_turn_duration_hours")
    tubewell_power = farm_data.get("tubewell_power_source")

    # Price & Profit calculations
    yield_maunds = econ["expected_yield_maunds_acre"]
    cost_per_maund = econ["cost_per_maund_pkr"]
    estimated_cost_acre = round(yield_maunds * cost_per_maund, 2)

    if price_forecast_data and "forecast_30d_maund" in price_forecast_data:
        expected_price_maund = price_forecast_data["forecast_30d_maund"]
        confidence_pct = price_forecast_data.get("confidence_pct", 74.0)
    elif price_forecast_data and "current_price_maund" in price_forecast_data:
        expected_price_maund = price_forecast_data["current_price_maund"]
        confidence_pct = price_forecast_data.get("confidence_pct", 74.0)
    else:
        expected_price_maund = econ["base_price_pkr_maund"]
        confidence_pct = 74.0

    expected_revenue_acre = round(yield_maunds * expected_price_maund, 2)
    expected_gross_margin_acre = round(expected_revenue_acre - estimated_cost_acre, 2)

    # Evaluate 9 Sub-scores
    soil_score, soil_limits, soil_recs = calculate_soil_suitability(
        crop_name=crop_name, ph=ph, organic_carbon_g_kg=soc, clay_pct=clay, sand_pct=sand, silt_pct=silt
    )
    climate_score, climate_limits, climate_recs = calculate_climate_suitability(
        crop_info=crop_info, temp_c=temp_c, humidity_pct=humidity_pct
    )
    water_score, water_limits, water_recs = calculate_water_suitability(
        crop_info=crop_info,
        canal_name=canal_name,
        canal_turn_hours=canal_turn_hrs,
        tubewell_power=tubewell_power,
        rainfall_mm=precip_mm,
    )
    season_score, season_limits, season_recs = calculate_season_suitability(
        crop_info=crop_info, month=month, ref_date=ref_date
    )
    from app.core.engine.crop_knowledge import normalize_province
    province_raw = farm_data.get("province") or farm_data.get("Province")
    district_raw = farm_data.get("district") or farm_data.get("District")
    province = normalize_province(province_raw, district_raw)

    pw_res = calculate_planting_window_status(
        crop_name=crop_name, ref_date=ref_date, province=province
    )
    planting_window_score = pw_res.score
    days_until_window = pw_res.days_until_window
    days_remaining_in_window = pw_res.days_remaining_in_window
    days_since_window = pw_res.days_since_window
    status = pw_res.status

    market_score, market_limits, market_recs = calculate_market_suitability(
        crop_name=crop_name, price_forecast_data=price_forecast_data
    )
    profit_score, profit_limits, profit_recs = calculate_profit_suitability(
        expected_gross_margin_pkr_acre=expected_gross_margin_acre
    )
    disease_risk_score, disease_limits, disease_recs = calculate_disease_risk_suitability(
        crop_name=crop_name, temp_c=temp_c, humidity_pct=humidity_pct
    )
    yield_score, yield_limits, yield_recs = calculate_yield_suitability(
        crop_name=crop_name, soil_score=soil_score, climate_score=climate_score, water_score=water_score
    )

    # Decoupled Agronomic vs 9-Factor Combined Scoring
    if price_forecast_data is None:
        # Pure Agronomic Suitability Score (decoupled from market prices):
        # Season: 20%, Planting Window: 20%, Weather: 20%, Soil: 20%, Water: 10%, Disease Risk: 5%, Yield: 5%
        overall_score = round(
            0.20 * season_score
            + 0.20 * planting_window_score
            + 0.20 * climate_score
            + 0.20 * soil_score
            + 0.10 * water_score
            + 0.05 * disease_risk_score
            + 0.05 * yield_score
        )
    else:
        # 9-Factor Overall Weighted Crop Suitability Score:
        # Season: 20%, Planting Window: 15%, Weather: 15%, Soil: 15%, Water: 10%, Disease Risk: 5%, Yield: 5%, Market: 5%, Profit: 10%
        overall_score = round(
            0.20 * season_score
            + 0.15 * planting_window_score
            + 0.15 * climate_score
            + 0.15 * soil_score
            + 0.10 * water_score
            + 0.05 * disease_risk_score
            + 0.05 * yield_score
            + 0.05 * market_score
            + 0.10 * profit_score
        )
    overall_score = max(0, min(100, overall_score))

    # Determine final recommendation status
    if overall_score >= 85:
        category = "Highly Suitable"
        recommendation_level = "HIGH"
    elif overall_score >= 70:
        category = "Suitable"
        recommendation_level = "RECOMMENDED"
    elif overall_score >= 50:
        category = "Moderately Suitable"
        recommendation_level = "MODERATE"
    else:
        category = "Unsuitable"
        recommendation_level = "LOW"
        status = "NOT RECOMMENDED 🔴"

    if "NOT RECOMMENDED" in status or "NOT_RECOMMENDED" in status:
        status_code = "NOT_RECOMMENDED"
    elif "PLANT" in status:
        status_code = "PLANT"
    elif "PREPARE" in status:
        status_code = "PREPARE"
    elif "WAIT" in status:
        status_code = "WAIT"
    elif "LATE" in status:
        status_code = "LATE"
    else:
        status_code = "NOT_RECOMMENDED"

    all_limits = soil_limits + climate_limits + water_limits + season_limits + market_limits + profit_limits + disease_limits
    all_recs = soil_recs + climate_recs + water_recs + season_recs + market_recs + profit_recs + disease_recs

    unique_recs = list(dict.fromkeys(all_recs))
    unique_limits = list(dict.fromkeys(all_limits))

    timeline = generate_crop_timeline(crop_info["crop"], ref_date)
    todays_farm_action = generate_todays_farm_actions(crop_info["crop"], status, days_until_window, unique_limits)

    from app.core.engine.crop_knowledge import get_crop_id
    crop_id = get_crop_id(crop_info.get("crop_id") or crop_name)

    return {
        "crop_id": crop_id,
        "crop_name": crop_info["crop"],
        "suitability_score": overall_score,
        "category": category,
        "recommendation_level": recommendation_level,
        "status": status,
        "status_code": status_code,
        "days_until_window": days_until_window,
        "days_remaining_in_window": days_remaining_in_window,
        "days_since_window": days_since_window,
        "season_score": season_score,
        "planting_window_score": planting_window_score,
        "soil_score": soil_score,
        "climate_score": climate_score,
        "weather_score": climate_score,  # Alias for climate_score
        "water_score": water_score,
        "disease_risk_score": disease_risk_score,
        "yield_score": yield_score,
        "market_score": market_score,
        "profit_score": profit_score,
        "expected_yield_maunds_acre": yield_maunds,
        "expected_price_pkr_maund": expected_price_maund,
        "expected_revenue_pkr_acre": expected_revenue_acre,
        "estimated_cost_pkr_acre": estimated_cost_acre,
        "expected_gross_margin_pkr_acre": expected_gross_margin_acre,
        "price_confidence_pct": confidence_pct,
        "limiting_factors": unique_limits,
        "recommendations": unique_recs,
        "timeline": timeline,
        "todays_farm_action": todays_farm_action,
    }


def evaluate_all_crops(
    farm_data: dict[str, Any],
    soil_data: dict[str, Any] | None = None,
    weather_data: dict[str, Any] | None = None,
    month: int | None = None,
    price_forecasts: dict[str, dict] | None = None,
    ref_date: datetime.date | None = None,
) -> list[dict[str, Any]]:
    """
    Evaluates 9-factor suitability & profit expected margins for all crops in knowledge base.
    """
    results = []
    price_forecasts = price_forecasts or {}
    for entry in CROP_KNOWLEDGE_BASE:
        crop_name = entry["crop"]
        p_forecast = price_forecasts.get(crop_name)
        res = evaluate_crop_suitability(
            crop_name=crop_name,
            farm_data=farm_data,
            soil_data=soil_data,
            weather_data=weather_data,
            month=month,
            price_forecast_data=p_forecast,
            ref_date=ref_date,
        )
        results.append(res)

    results.sort(key=lambda x: x["suitability_score"], reverse=True)
    return results
