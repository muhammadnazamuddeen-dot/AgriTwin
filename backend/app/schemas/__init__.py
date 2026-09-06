"""Pydantic schemas for request/response validation."""

import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── User ──────────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    name: str = Field(..., max_length=120)
    email: str
    phone: str | None = None
    role: str = "farmer"
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    role: str
    is_active: bool
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=6)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Farm ──────────────────────────────────────────────────────────────────────
class FarmCreate(BaseModel):
    name: str = Field(..., max_length=200)
    geometry_geojson: str | None = None
    area_acres: float | None = None
    district: str | None = None
    province: str = "Punjab"
    latitude: float | None = None
    longitude: float | None = None
    canal_name: str | None = "Lower Bari Doab Canal"
    canal_turn_day: str | None = "Thursday"
    canal_turn_time: str | None = "02:00"
    canal_turn_duration_hours: float | None = 4.0
    tubewell_power_source: str | None = "diesel"
    tubewell_hourly_cost_pkr: float | None = 1400.0


class FarmResponse(BaseModel):
    id: int
    name: str
    geometry_geojson: str | None
    area_acres: float | None
    district: str | None
    province: str
    latitude: float | None
    longitude: float | None
    canal_name: str | None
    canal_turn_day: str | None
    canal_turn_time: str | None
    canal_turn_duration_hours: float | None
    tubewell_power_source: str | None
    tubewell_hourly_cost_pkr: float | None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class FarmUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    geometry_geojson: str | None = None
    area_acres: float | None = None
    district: str | None = None
    province: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    canal_name: str | None = None
    canal_turn_day: str | None = None
    canal_turn_time: str | None = None
    canal_turn_duration_hours: float | None = None
    tubewell_power_source: str | None = None
    tubewell_hourly_cost_pkr: float | None = None


class WarabandiConfigUpdate(BaseModel):
    canal_name: str | None = None
    canal_turn_day: str | None = None
    canal_turn_time: str | None = None
    canal_turn_duration_hours: float | None = None
    tubewell_power_source: str | None = None
    tubewell_hourly_cost_pkr: float | None = None


class WarabandiAdviceResponse(BaseModel):
    farm_id: int
    farm_name: str
    canal_name: str
    canal_turn_day: str
    canal_turn_time: str
    canal_turn_duration_hours: float
    hours_until_turn: float
    days_until_turn: int
    next_turn_formatted: str
    next_turn_formatted_ur: str
    water_demand_inches: float
    water_demand_m3: float
    current_soil_moisture_pct: float
    upcoming_rain_48h_mm: float
    hold_tubewell_recommended: bool
    potential_savings_pkr: float
    tubewell_power_source: str
    action_en: str
    action_ur: str
    reasoning_en: str
    reasoning_ur: str


class SoilPhysicsResponse(BaseModel):
    farm_id: int
    clay_pct: float
    sand_pct: float
    silt_pct: float
    organic_matter_pct: float
    field_capacity_m3m3: float
    wilting_point_m3m3: float
    saturation_m3m3: float
    available_water_capacity_mm_m: float
    available_water_capacity_in_ft: float
    ksat_mm_hr: float
    usda_texture: str
    punjabi_texture: str
    data_source: str


class CropPhenologyGDDResponse(BaseModel):
    farm_id: int
    crop_name: str
    stage_name: str
    stage_name_ur: str
    accumulated_gdd: float
    stage_target_gdd: float
    stage_progress_pct: float
    total_crop_gdd: float
    crop_progress_pct: float
    current_kc: float
    heat_stress_alert: bool
    heat_stress_message_en: str
    heat_stress_message_ur: str


# ── Crop ──────────────────────────────────────────────────────────────────────
class CropCreate(BaseModel):
    crop_name: str
    variety: str | None = None
    sowing_date: datetime.datetime | None = None
    expected_harvest_date: datetime.datetime | None = None
    growth_stage: str | None = None
    season: str | None = None
    irrigation: str | None = None
    soil_type: str | None = None
    farming_method: str | None = None
    previous_crop: str | None = None


class CropUpdate(BaseModel):
    crop_name: str | None = None
    variety: str | None = None
    sowing_date: datetime.datetime | None = None
    expected_harvest_date: datetime.datetime | None = None
    growth_stage: str | None = None
    season: str | None = None
    irrigation: str | None = None
    soil_type: str | None = None
    farming_method: str | None = None
    previous_crop: str | None = None


class CropResponse(BaseModel):
    id: int
    farm_id: int
    crop_name: str
    variety: str | None
    sowing_date: datetime.datetime | None
    expected_harvest_date: datetime.datetime | None
    growth_stage: str | None
    season: str | None
    irrigation: str | None
    soil_type: str | None
    farming_method: str | None
    previous_crop: str | None

    model_config = {"from_attributes": True}


# ── Weather ───────────────────────────────────────────────────────────────────
class WeatherRecordResponse(BaseModel):
    id: int
    farm_id: int
    timestamp: datetime.datetime
    temperature_c: float | None
    humidity_pct: float | None
    rainfall_mm: float | None
    wind_speed_kmh: float | None
    et0_mm: float | None
    cloud_cover_pct: float | None
    source: str

    model_config = {"from_attributes": True}


# ── Climate ────────────────────────────────────────────────────────────────
class ClimateSnapshotResponse(BaseModel):
    id: int
    farm_id: int
    baseline_period: str
    historical_mean_temp_c: float | None
    temp_anomaly_c: float | None
    historical_mean_humidity_pct: float | None
    humidity_anomaly_pct: float | None
    historical_total_precip_mm: float | None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


# ── Satellite ─────────────────────────────────────────────────────────────────
class SatelliteObservationResponse(BaseModel):
    id: int
    farm_id: int
    date: datetime.datetime
    ndvi: float | None
    evi: float | None
    cloud_cover_pct: float | None
    source: str
    image_url: str | None

    model_config = {"from_attributes": True}


# ── Soil ──────────────────────────────────────────────────────────────────────
class SoilProfileResponse(BaseModel):
    id: int
    farm_id: int
    ph_topsoil: float | None
    organic_carbon_g_per_kg: float | None
    clay_pct: float | None
    sand_pct: float | None
    silt_pct: float | None
    bulk_density_kg_dm3: float | None
    source: str
    fetched_at: datetime.datetime

    model_config = {"from_attributes": True}


class SoilObservationResponse(BaseModel):
    id: int
    farm_id: int
    date: datetime.datetime
    soil_moisture_m3m3: float | None
    soil_temperature_c: float | None
    soil_moisture_7_28cm: float | None
    soil_moisture_28_100cm: float | None
    depth_cm: int | None
    source: str

    model_config = {"from_attributes": True}


# ── Recommendation ────────────────────────────────────────────────────────────
class RecommendationResponse(BaseModel):
    id: int
    farm_id: int
    recommendation_text: str
    reason: str | None
    confidence: float | None
    risk_level: str | None
    category: str | None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


# ── Farm Health ───────────────────────────────────────────────────────────────
class FarmHealthScore(BaseModel):
    overall: int
    vegetation: int
    water: int
    weather: int
    pest_risk: int
    climate: int
    soil: int = 0


# ── AI Recommendation ────────────────────────────────────────────────────────
class AIRecommendationRequest(BaseModel):
    farm_id: int
    question: str | None = None


class AIRecommendationResponse(BaseModel):
    recommendation: str
    reasoning: str
    recommendation_ur: str | None = None
    reasoning_ur: str | None = None
    confidence: float
    risk_level: str
    data_summary: dict



# ── Crop Suitability ──────────────────────────────────────────────────────────
class CropSuitabilityItem(BaseModel):
    crop_id: str | None = None
    crop_name: str
    suitability_score: int
    category: str
    status: str = "PLANT NOW 🟢"
    status_code: str | None = None
    days_until_window: int = 0
    days_remaining_in_window: int = 0
    days_since_window: int = 0
    season_score: int
    planting_window_score: int = 80
    soil_score: int
    climate_score: int
    weather_score: int | None = None
    water_score: int
    disease_risk_score: int = 85
    yield_score: int = 80
    market_score: int = 80
    profit_score: int = 80
    expected_yield_maunds_acre: float | None = None
    expected_price_pkr_maund: float | None = None
    expected_revenue_pkr_acre: float | None = None
    estimated_cost_pkr_acre: float | None = None
    expected_gross_margin_pkr_acre: float | None = None
    price_confidence_pct: float | None = None
    recommendation_level: str | None = None
    limiting_factors: list[str] = []
    recommendations: list[str] = []
    timeline: list[dict[str, Any]] = []
    todays_farm_action: list[str] = []


class CropSuitabilityResponse(BaseModel):
    farm_id: int
    evaluated_at: datetime.datetime
    target_crop: str | None = None
    ranked_crops: list[CropSuitabilityItem]


# ── Pest & Disease Risk ───────────────────────────────────────────────────────
class PestRiskItem(BaseModel):
    pest_or_disease_name: str
    category: str  # "Pest" or "Disease"
    risk_level: str  # "High", "Medium", "Low"
    risk_score: int  # 0-100
    trigger_conditions: list[str]
    organic_control: str
    chemical_control: str
    preventative_measures: list[str]


class PestRiskResponse(BaseModel):
    farm_id: int
    evaluated_at: datetime.datetime
    crop_name: str
    growth_stage: str | None = None
    overall_pest_risk: str
    risks: list[PestRiskItem]


