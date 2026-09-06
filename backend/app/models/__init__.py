"""SQLAlchemy ORM models for AgriTwin AI."""

import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="farmer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    farms = relationship("Farm", back_populates="owner", cascade="all, delete-orphan")


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    # GeoJSON polygon stored as text for SQLite; use Geometry(POLYGON) with PostGIS
    geometry_geojson = Column(Text, nullable=True)
    area_acres = Column(Float, nullable=True)
    district = Column(String(100), nullable=True)
    province = Column(String(100), default="Punjab")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    # Warabandi (Canal Water Turn) & Tubewell Configuration
    canal_name = Column(String(120), nullable=True, default="Lower Bari Doab Canal")
    canal_turn_day = Column(String(20), nullable=True, default="Thursday")
    canal_turn_time = Column(String(10), nullable=True, default="02:00")
    canal_turn_duration_hours = Column(Float, default=4.0)
    tubewell_power_source = Column(String(30), default="diesel")
    tubewell_hourly_cost_pkr = Column(Float, default=1400.0)
    created_at = Column(DateTime, default=func.now())

    owner = relationship("User", back_populates="farms")
    crops = relationship("Crop", back_populates="farm", cascade="all, delete-orphan")
    weather_records = relationship("WeatherRecord", back_populates="farm", cascade="all, delete-orphan")
    satellite_observations = relationship(
        "SatelliteObservation", back_populates="farm", cascade="all, delete-orphan"
    )
    soil_observations = relationship("SoilObservation", back_populates="farm", cascade="all, delete-orphan")
    soil_profile = relationship("SoilProfile", back_populates="farm", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="farm", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="farm", cascade="all, delete-orphan")
    score_snapshots = relationship(
        "HealthScoreSnapshot", back_populates="farm", cascade="all, delete-orphan"
    )
    climate_snapshots = relationship(
        "ClimateSnapshot", back_populates="farm", cascade="all, delete-orphan"
    )


class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    crop_name = Column(String(100), nullable=False)
    variety = Column(String(100), nullable=True)
    sowing_date = Column(DateTime, nullable=True)
    expected_harvest_date = Column(DateTime, nullable=True)
    growth_stage = Column(String(50), nullable=True)
    season = Column(String(20), nullable=True)  # Rabi / Kharif
    # Crop profile metadata (Phase 3)
    irrigation = Column(String(50), nullable=True)       # canal / tubewell / drip / sprinkler / rainfed
    soil_type = Column(String(50), nullable=True)        # loam / clay / sandy / silt / clay-loam
    farming_method = Column(String(50), nullable=True)   # conventional / organic / precision / zero-tillage
    previous_crop = Column(String(100), nullable=True)   # free-text crop name

    farm = relationship("Farm", back_populates="crops")


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    temperature_c = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    rainfall_mm = Column(Float, nullable=True)
    wind_speed_kmh = Column(Float, nullable=True)
    et0_mm = Column(Float, nullable=True)
    cloud_cover_pct = Column(Float, nullable=True)
    source = Column(String(50), default="open-meteo")

    farm = relationship("Farm", back_populates="weather_records")


class ClimateSnapshot(Base):
    """Persisted climate anomaly snapshot — one per baseline_period per farm."""
    __tablename__ = "climate_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    baseline_period = Column(String(20), nullable=False)  # e.g. "2025-09"
    historical_mean_temp_c = Column(Float, nullable=True)
    temp_anomaly_c = Column(Float, nullable=True)
    historical_mean_humidity_pct = Column(Float, nullable=True)
    humidity_anomaly_pct = Column(Float, nullable=True)
    historical_total_precip_mm = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())

    farm = relationship("Farm", back_populates="climate_snapshots")


class SatelliteObservation(Base):
    __tablename__ = "satellite_observations"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    ndvi = Column(Float, nullable=True)
    evi = Column(Float, nullable=True)
    cloud_cover_pct = Column(Float, nullable=True)
    source = Column(String(50), default="sentinel-2")
    image_url = Column(Text, nullable=True)

    farm = relationship("Farm", back_populates="satellite_observations")


class SoilProfile(Base):
    """Static soil properties from SoilGrids — one per farm, rarely changes."""
    __tablename__ = "soil_profiles"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, unique=True)
    ph_topsoil = Column(Float, nullable=True)               # 0-30 cm
    organic_carbon_g_per_kg = Column(Float, nullable=True)  # 0-30 cm
    clay_pct = Column(Float, nullable=True)                  # 0-30 cm
    sand_pct = Column(Float, nullable=True)                  # 0-30 cm
    silt_pct = Column(Float, nullable=True)                  # 0-30 cm
    bulk_density_kg_dm3 = Column(Float, nullable=True)      # 0-30 cm
    source = Column(String(50), default="soilgrids")
    fetched_at = Column(DateTime, default=func.now())

    farm = relationship("Farm", back_populates="soil_profile")


class SoilObservation(Base):
    __tablename__ = "soil_observations"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    soil_moisture_m3m3 = Column(Float, nullable=True)       # 0-7 cm
    soil_temperature_c = Column(Float, nullable=True)       # 0-7 cm
    soil_moisture_7_28cm = Column(Float, nullable=True)
    soil_moisture_28_100cm = Column(Float, nullable=True)
    depth_cm = Column(Integer, nullable=True)
    source = Column(String(50), default="open-meteo")

    farm = relationship("Farm", back_populates="soil_observations")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    recommendation_text = Column(Text, nullable=False)
    reason = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)  # low / moderate / high / critical
    category = Column(String(50), nullable=True)  # irrigation, pest, weather, crop
    created_at = Column(DateTime, default=func.now())

    farm = relationship("Farm", back_populates="recommendations")


class HealthScoreSnapshot(Base):
    """Point-in-time health score — persisted per intelligence call for trend charts."""

    __tablename__ = "health_score_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    overall = Column(Integer, nullable=False)
    vegetation = Column(Integer, nullable=True)
    water = Column(Integer, nullable=True)
    weather = Column(Integer, nullable=True)
    pest_risk = Column(Integer, nullable=True)
    climate = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())

    farm = relationship("Farm", back_populates="score_snapshots")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    severity = Column(String(20), nullable=False)  # info / warning / critical
    category = Column(String(50), nullable=False)  # irrigation / heat / vegetation / pest / rain / wind
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)  # JSON-encoded list
    recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

    farm = relationship("Farm", back_populates="alerts")


class CropPrice(Base):
    """Daily market committee prices from AMIS Punjab & PAR REST API."""

    __tablename__ = "crop_prices"

    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String(100), nullable=False, index=True)
    variety = Column(String(100), nullable=True)
    district = Column(String(100), nullable=False, index=True)
    market = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    min_price_pkr_100kg = Column(Float, nullable=True)
    max_price_pkr_100kg = Column(Float, nullable=True)
    average_price_pkr_100kg = Column(Float, nullable=False)
    unit = Column(String(30), default="100 kg")
    source = Column(String(100), default="AMIS Punjab / PAR")
    created_at = Column(DateTime, default=func.now())


class CropMarketPrice(Base):
    """Real-time & historical wholesale market prices per crop_id across mandis."""

    __tablename__ = "crop_market_prices"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(String(50), nullable=False, index=True)
    crop_name = Column(String(100), nullable=False, index=True)
    variety = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True, default="Punjab")
    district = Column(String(100), nullable=False, index=True)
    market = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    min_price_pkr_40kg = Column(Float, nullable=True)
    max_price_pkr_40kg = Column(Float, nullable=True)
    average_price_pkr_40kg = Column(Float, nullable=False)
    min_price_pkr_100kg = Column(Float, nullable=True)
    max_price_pkr_100kg = Column(Float, nullable=True)
    average_price_pkr_100kg = Column(Float, nullable=True)
    unit = Column(String(30), default="40 kg")
    source = Column(String(100), default="AMIS Pakistan / PAR")
    created_at = Column(DateTime, default=func.now())


class CropPricePrediction(Base):
    """ML commodity price predictions per crop_id for 7d, 14d, and 30d horizons."""

    __tablename__ = "crop_price_predictions"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(String(50), nullable=False, index=True)
    crop_name = Column(String(100), nullable=False, index=True)
    province = Column(String(100), nullable=True, default="Punjab")
    district = Column(String(100), nullable=False, index=True)
    market = Column(String(100), nullable=True)
    prediction_date = Column(DateTime, nullable=False, default=func.now())
    current_price_pkr_100kg = Column(Float, nullable=False)
    current_price_pkr_40kg = Column(Float, nullable=True)
    forecast_7d_pkr_100kg = Column(Float, nullable=False)
    forecast_14d_pkr_100kg = Column(Float, nullable=False)
    forecast_30d_pkr_100kg = Column(Float, nullable=False)
    forecast_7d_pkr_40kg = Column(Float, nullable=True)
    forecast_14d_pkr_40kg = Column(Float, nullable=True)
    forecast_30d_pkr_40kg = Column(Float, nullable=True)
    price_change_7d_pct = Column(Float, nullable=True)
    price_change_30d_pct = Column(Float, nullable=True)
    trend_direction = Column(String(20), nullable=True)
    confidence = Column(Float, nullable=True)
    confidence_pct = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())


