"""AgriCore — the central decision engine for AgriTwin AI.

Combines weather, satellite, soil, and crop data into a unified farm
health score and generates AI-powered recommendations.
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

from app.core.engine.crop_knowledge import get_crop_info

load_dotenv()


# ── Data structures ───────────────────────────────────────────────────────────
@dataclass
class FarmContext:
    """Aggregated data context for a single farm."""

    farm_id: int
    crop_name: str | None = None
    growth_stage: str | None = None
    sowing_date: str | None = None

    # Crop profile (Phase 3)
    irrigation: str | None = None
    soil_type: str | None = None
    farming_method: str | None = None
    previous_crop: str | None = None

    # Weather
    temperature_c: float | None = None
    humidity_pct: float | None = None
    rainfall_mm: float | None = None
    rain_probability_pct: float | None = None
    wind_speed_kmh: float | None = None
    et0_mm: float | None = None

    # Satellite
    ndvi: float | None = None
    ndvi_change: float | None = None

    # Soil
    soil_moisture_m3m3: float | None = None
    soil_temperature_c: float | None = None

    # Soil profile (SoilGrids)
    ph_topsoil: float | None = None
    organic_carbon_g_per_kg: float | None = None
    soil_moisture_7_28cm: float | None = None
    soil_moisture_28_100cm: float | None = None

    # Climate anomaly (from NASA POWER historical baseline)
    temp_anomaly_c: float | None = None
    humidity_anomaly_pct: float | None = None
    historical_mean_temp_c: float | None = None

    # Warabandi Canal & Tubewell context
    canal_name: str | None = None
    canal_turn_day: str | None = None
    canal_turn_time: str | None = None
    canal_turn_duration_hours: float | None = None
    tubewell_power_source: str | None = None
    tubewell_hourly_cost_pkr: float | None = None

    # Engine Summaries
    pest_risks_summary: str | None = None
    crop_suitability_summary: str | None = None

    # Alerts
    regional_pest_alert: bool = False

    # Extra
    extra: dict = field(default_factory=dict)



@dataclass
class FarmHealthScore:
    overall: int = 0
    vegetation: int = 0
    water: int = 0
    weather: int = 0
    pest_risk: int = 0
    climate: int = 0
    soil: int = 0


@dataclass
class Recommendation:
    text: str
    reasoning: str
    confidence: float
    risk_level: str  # low / moderate / high / critical
    data_summary: dict
    text_ur: str | None = None
    reasoning_ur: str | None = None


# ── Scoring engine ────────────────────────────────────────────────────────────
def compute_health_score(ctx: FarmContext) -> FarmHealthScore:
    """Compute a 0–100 health score for each dimension."""
    score = FarmHealthScore()

    # ── Vegetation (NDVI-based) ───────────────────────────────────────────────
    if ctx.ndvi is not None:
        crop_info = get_crop_info(ctx.crop_name) if ctx.crop_name else None
        low, high = (crop_info["ndvi_healthy_range"] if crop_info else (0.4, 0.85))
        if ctx.ndvi >= low:
            score.vegetation = min(100, int(ctx.ndvi / high * 100))
        else:
            score.vegetation = max(0, int(ctx.ndvi / low * 60))
        if ctx.ndvi_change is not None and ctx.ndvi_change < -0.05:
            score.vegetation = max(0, score.vegetation - 15)
    else:
        score.vegetation = 50

    # ── Water (soil moisture + ET0 + rainfall) ────────────────────────────────
    water_score = 70
    if ctx.soil_moisture_m3m3 is not None:
        if ctx.soil_moisture_m3m3 < 0.15:
            water_score -= 35
        elif ctx.soil_moisture_m3m3 < 0.25:
            water_score -= 15
        elif ctx.soil_moisture_m3m3 > 0.45:
            water_score -= 20

    if ctx.rainfall_mm is not None and ctx.rainfall_mm > 20:
        water_score = min(100, water_score + 15)

    if ctx.et0_mm is not None and ctx.et0_mm > 6.0:
        water_score = max(0, water_score - 15)

    score.water = max(0, min(100, water_score))

    # ── Weather (temperature + humidity + wind extremes) ──────────────────────
    weather_score = 80
    if ctx.temperature_c is not None:
        if ctx.temperature_c > 42:
            weather_score -= 40
        elif ctx.temperature_c > 38:
            weather_score -= 20
        elif ctx.temperature_c < 4:
            weather_score -= 30

    if ctx.wind_speed_kmh is not None and ctx.wind_speed_kmh > 45:
        weather_score -= 25

    if ctx.humidity_pct is not None and ctx.humidity_pct > 85:
        weather_score -= 10

    score.weather = max(0, min(100, weather_score))

    # ── Pest Risk (temp + humidity interaction) ───────────────────────────────
    pest_score = 80
    if ctx.temperature_c and ctx.humidity_pct:
        if 26 <= ctx.temperature_c <= 35 and ctx.humidity_pct > 65:
            pest_score -= 35
        elif 22 <= ctx.temperature_c <= 38 and ctx.humidity_pct > 55:
            pest_score -= 20

    if ctx.regional_pest_alert:
        pest_score -= 25

    score.pest_risk = max(0, min(100, pest_score))

    # ── Climate Anomaly (departure from historical baseline) ───────────────────
    climate_score = 80
    if ctx.temp_anomaly_c is not None:
        anomaly = abs(ctx.temp_anomaly_c)
        if anomaly >= 5.0:
            climate_score -= 45
        elif anomaly >= 3.0:
            climate_score -= 25
        elif anomaly >= 1.5:
            climate_score -= 10

    if ctx.humidity_anomaly_pct is not None:
        h_anomaly = abs(ctx.humidity_anomaly_pct)
        if h_anomaly >= 25.0:
            climate_score -= 25
        elif h_anomaly >= 15.0:
            climate_score -= 10

    score.climate = max(0, min(100, climate_score))

    # ── Soil Health (pH, organic carbon, moisture consistency) ───────────────
    soil_score = 70
    if ctx.ph_topsoil is not None:
        if ctx.ph_topsoil < 5.5 or ctx.ph_topsoil > 8.5:
            soil_score -= 25
        elif ctx.ph_topsoil < 6.0 or ctx.ph_topsoil > 8.0:
            soil_score -= 10

    if ctx.organic_carbon_g_per_kg is not None:
        if ctx.organic_carbon_g_per_kg < 4:
            soil_score -= 20
        elif ctx.organic_carbon_g_per_kg < 8:
            soil_score -= 10

    layers = [ctx.soil_moisture_m3m3, ctx.soil_moisture_7_28cm, ctx.soil_moisture_28_100cm]
    present = [v for v in layers if v is not None]
    if len(present) >= 2:
        spread = max(present) - min(present)
        if spread > 0.20:
            soil_score -= 10

    score.soil = max(0, min(100, soil_score))

    # ── Overall composite (weighted average) ──────────────────────────────────
    weights = {
        "vegetation": 0.22,
        "water": 0.20,
        "weather": 0.18,
        "pest_risk": 0.12,
        "climate": 0.13,
        "soil": 0.15,
    }
    score.overall = int(
        score.vegetation * weights["vegetation"]
        + score.water * weights["water"]
        + score.weather * weights["weather"]
        + score.pest_risk * weights["pest_risk"]
        + score.climate * weights["climate"]
        + score.soil * weights["soil"]
    )
    return score


# ── AI Recommendation Engine (Gemini) ─────────────────────────────────────────
async def generate_recommendation(
    ctx: FarmContext,
    health: FarmHealthScore,
    grounding: str | None = None,
    question: str | None = None,
) -> Recommendation:
    """Generate agronomic recommendations via Gemini (bilingual English + Punjabi-flavored Urdu), or fallback to rule-based."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return _rule_based_recommendation(ctx, health, question=question)

    try:
        from google import genai
        from google.genai import types as genai_types
    except ImportError:
        return _rule_based_recommendation(ctx, health, question=question)

    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    grounding_block = ""
    if grounding:
        grounding_block = (
            "Grounding Data (this farm's own recorded history, recent alerts, "
            "previous advice, and a locally-trained ML forecast — use it to make "
            "the advice specific and authentic; cite concrete numbers when relevant):\n"
            f"{grounding}\n\n"
        )

    question_block = ""
    if question:
        question_block = f"\nFARMER'S SPECIFIC QUESTION / INQUIRY:\n\"{question}\"\nPlease ensure your answer directly addresses this question using the telemetry data above.\n"

    prompt = f"""You are AgriTwin AI, an expert precision agronomy advisor for farmers in Punjab, Pakistan.
Analyze the following farm telemetry and provide concise, actionable recommendations in BOTH English AND simple, friendly Punjabi / Urdu (using colloquial Punjab farming terminology understandable by local farmers, e.g. آبپاشی/پانی, کھاد/یوریا, سنڈی/تیلہ, گندم/دھان/کپاس/کماد).

Farm Context:
- Crop: {ctx.crop_name or 'Unknown'}
- Growth Stage: {ctx.growth_stage or 'Unknown'}
- Irrigation: {ctx.irrigation or 'Unknown'}
- Soil Type: {ctx.soil_type or 'Unknown'}
- Farming Method: {ctx.farming_method or 'Unknown'}
- Previous Crop: {ctx.previous_crop or 'Unknown'}
- Temperature: {ctx.temperature_c}°C
- Humidity: {ctx.humidity_pct}%
- Rainfall (recent): {ctx.rainfall_mm} mm
- Rain Probability (next 48h): {ctx.rain_probability_pct}%
- Soil Moisture: {ctx.soil_moisture_m3m3} m³/m³
- Soil Temp: {ctx.soil_temperature_c}°C
- Soil pH (topsoil): {ctx.ph_topsoil if ctx.ph_topsoil is not None else 'N/A'}
- Soil Organic Carbon: {ctx.organic_carbon_g_per_kg if ctx.organic_carbon_g_per_kg is not None else 'N/A'} g/kg
- Canal Water Turn: {ctx.canal_name or 'N/A'} ({ctx.canal_turn_day or 'N/A'} {ctx.canal_turn_time or 'N/A'}, {ctx.canal_turn_duration_hours or 'N/A'} hrs)
- Tubewell Power / Cost: {ctx.tubewell_power_source or 'N/A'} (PKR {ctx.tubewell_hourly_cost_pkr or 'N/A'}/hr)
- NDVI: {ctx.ndvi} (change: {ctx.ndvi_change})
- ET0: {ctx.et0_mm} mm
- Wind: {ctx.wind_speed_kmh} km/h
- Regional Pest Alert: {ctx.regional_pest_alert}
- Temperature Anomaly vs. Historical Baseline: {ctx.temp_anomaly_c if ctx.temp_anomaly_c is not None else 'N/A'}°C
- Historical Mean Temperature (same month last year, NASA POWER): {ctx.historical_mean_temp_c if ctx.historical_mean_temp_c is not None else 'N/A'}°C
- Humidity Anomaly vs. Historical: {ctx.humidity_anomaly_pct if ctx.humidity_anomaly_pct is not None else 'N/A'}%
{f"- Pest Risk Summary: {ctx.pest_risks_summary}" if ctx.pest_risks_summary else ""}

{grounding_block}{question_block}Farm Health Score: {health.overall}/100
- Vegetation: {health.vegetation}
- Water: {health.water}
- Weather: {health.weather}
- Pest Risk: {health.pest_risk}
- Climate: {health.climate}
- Soil: {health.soil}

Respond in this exact JSON format:
{{
  "recommendation": "<concise actionable recommendation in English>",
  "reasoning": "<concise explanation why based on telemetry in English>",
  "recommendation_ur": "<آسان اور عام فہم اردو / پنجابی زرعی زبان میں کسان کے لیے ٹھوس عملی مشورہ>",
  "reasoning_ur": "<موسم، نمی اور فصل کے مطابق آسان اردو میں وجہ>",
  "confidence": <0.0 to 1.0>,
  "risk_level": "<low|moderate|high|critical>"
}}
"""
    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3,
            ),
        )
    except Exception:
        return _rule_based_recommendation(ctx, health, question=question)

    try:
        result = json.loads(response.text)
    except (json.JSONDecodeError, TypeError):
        result = {
            "recommendation": response.text,
            "reasoning": "AI response could not be parsed as JSON.",
            "recommendation_ur": response.text,
            "reasoning_ur": "اے آئی جواب مکمل طور پر موصول نہیں ہوا۔",
            "confidence": 0.5,
            "risk_level": "moderate",
        }

    return Recommendation(
        text=result.get("recommendation", ""),
        reasoning=result.get("reasoning", ""),
        text_ur=result.get("recommendation_ur") or None,
        reasoning_ur=result.get("reasoning_ur") or None,
        confidence=result.get("confidence", 0.5),
        risk_level=result.get("risk_level", "moderate"),
        data_summary=_build_data_summary(ctx, health),
    )


def _rule_based_recommendation(
    ctx: FarmContext,
    health: FarmHealthScore,
    question: str | None = None,
) -> Recommendation:
    """Intelligent rule-based fallback with authentic Punjab farmer Urdu translations."""
    alerts = []
    alerts_ur = []

    # If farmer asked a specific question, handle keywords first
    q_lower = (question or "").lower()
    if q_lower:
        if any(w in q_lower for w in ["water", "irrigate", "irrigation", "پانی", "آبپاشی"]):
            if (ctx.soil_moisture_m3m3 or 0.3) < 0.22:
                alerts.append(
                    f"Irrigation Recommended: Soil moisture is low ({ctx.soil_moisture_m3m3 or 0.18:.2f} m³/m³). "
                    f"Utilize your canal turn ({ctx.canal_name or 'Canal'} on {ctx.canal_turn_day or 'scheduled day'} at {ctx.canal_turn_time or '02:00'}) "
                    f"or run tubewell."
                )
                alerts_ur.append(
                    f"آبپاشی دی سفارش: زمین وچ نمی کم اے۔ اپنی نہری واری ({ctx.canal_name or 'نہرا'} {ctx.canal_turn_day or 'مقررہ دن'}) استعمال کرو یا ٹیوب ویل چلاؤ۔"
                )
            else:
                alerts.append(
                    f"Delay Irrigation: Adequate soil moisture ({ctx.soil_moisture_m3m3 or 0.30:.2f} m³/m³). "
                    "Save tubewell diesel fuel for next week."
                )
                alerts_ur.append(
                    f"پانی فی الحال نہ لاؤ: زمین وچ پہلے توں مناسب نمی موجود اے۔ ٹیوب ویل دا ڈیزل بچاؤ۔"
                )
        elif any(w in q_lower for w in ["rust", "disease", "pest", "کیڑا", "تیلہ", "سنڈی", "بیماری"]):
            alerts.append(
                f"Pest/Disease Assessment for {ctx.crop_name or 'Crop'}: "
                f"{ctx.pest_risks_summary or 'Monitor foliage regularly for aphids or fungal spots.'}"
            )
            alerts_ur.append(
                f"{ctx.crop_name or 'فصل'} دی بیماری الرٹ: پتیاں دا باقاعدگی نال معائنہ کرو۔ نيم تیل یا تجویز کردہ دوائی دا سپرے کرو۔"
            )
        elif any(w in q_lower for w in ["fertilizer", "urea", "n", "کھاد", "یوریا"]):
            alerts.append(
                f"Fertilizer Advisory: Crop is at {ctx.growth_stage or 'vegetative'} stage. "
                "Apply split dose of Urea/DAP before scheduled canal turn."
            )
            alerts_ur.append(
                f"کھاد دی سفارش: فصل اس وقت {ctx.growth_stage or 'نشوونما'} دے مرحلے وچ اے۔ پانی توں پہلے یوریا دی قسط پاؤ۔"
            )

    if health.water < 50 and not alerts:
        alerts.append(
            "Water stress detected: soil moisture is low and no significant rainfall expected. "
            "Consider irrigation within the next 24–48 hours."
        )
        alerts_ur.append(
            "زمین وچ نمی دی کمی ہے تے بارش دا امکان نہیں۔ اگلے 24 توں 48 گھنٹیاں دے اندر فصل نوں پانی (آبپاشی) لاؤ۔"
        )
    if health.weather < 50 and not alerts:
        alerts.append(
            "Weather alert: extreme temperature or wind conditions detected. "
            "Monitor crops closely and consider protective measures."
        )
        alerts_ur.append(
            "موسمی الرٹ: تیز ہوا یا غیر معمولی گرمی دی وجہ توں فصل تے دباؤ اے۔ کھیت دی مسلسل نگرانی رکھو۔"
        )
    if health.pest_risk < 50 and not alerts:
        alerts.append(
            "Pest risk elevated: warm and humid conditions favor pest development. "
            "Consider scouting your fields and consulting local pest advisory services."
        )
        alerts_ur.append(
            "کیڑیاں (تیلہ / سنڈی) دا خطرہ: گرم تے نم موسم کیڑیاں لئی سازگار ہے۔ فورا اپنے کھیتاں دا معائنہ کرو۔"
        )
    if health.vegetation < 50 and not alerts:
        alerts.append(
            "Vegetation stress: NDVI indicates declining crop health. "
            "Investigate possible causes such as water stress, nutrient deficiency, or disease."
        )
        alerts_ur.append(
            "فصل دی ہریالی وچ کمی: سیٹلائٹ امیجری توں پودیاں دی صحت کمزور نظر آ رہی اے۔ کھاد تے پانی دی صورتحال چیک کرو۔"
        )

    if not alerts:
        alerts.append(
            "Your farm is in good condition. Continue current practices and monitor regularly."
        )
        alerts_ur.append(
            "ماشاءاللہ تہاڈی فصل دی مجموعی حالت بہترین ہے۔ موجودہ نگہداشت جاری رکھو۔"
        )

    risk = "critical" if health.overall < 30 else "high" if health.overall < 50 else "moderate" if health.overall < 70 else "low"
    confidence = 0.6 if health.overall < 50 else 0.75

    return Recommendation(
        text=" | ".join(alerts),
        reasoning=(
            f"Based on health score {health.overall}/100, live Open-Meteo observations, "
            f"MODIS NDVI, Warabandi canal turn schedule, and Punjab microclimate pathogen rules."
        ),
        text_ur=" | ".join(alerts_ur),
        reasoning_ur=f"صحت اسکور {health.overall}/100، اوپن میٹیو لائیو ڈیٹا، سیٹلائٹ این ڈی وی آئی، واربندی شیڈول تے زرعی ریکارڈ دی بنیاد پر۔",
        confidence=confidence,
        risk_level=risk,
        data_summary=_build_data_summary(ctx, health),
    )



def _build_data_summary(ctx: FarmContext, health: FarmHealthScore) -> dict:
    return {
        "farm_id": ctx.farm_id,
        "crop": ctx.crop_name,
        "growth_stage": ctx.growth_stage,
        "irrigation": ctx.irrigation,
        "soil_type": ctx.soil_type,
        "farming_method": ctx.farming_method,
        "previous_crop": ctx.previous_crop,
        "temperature_c": ctx.temperature_c,
        "humidity_pct": ctx.humidity_pct,
        "rainfall_mm": ctx.rainfall_mm,
        "soil_moisture_m3m3": ctx.soil_moisture_m3m3,
        "soil_temperature_c": ctx.soil_temperature_c,
        "ph_topsoil": ctx.ph_topsoil,
        "organic_carbon_g_per_kg": ctx.organic_carbon_g_per_kg,
        "ndvi": ctx.ndvi,
        "ndvi_change": ctx.ndvi_change,
        "et0_mm": ctx.et0_mm,
        "regional_pest_alert": ctx.regional_pest_alert,
        "temp_anomaly_c": ctx.temp_anomaly_c,
        "historical_mean_temp_c": ctx.historical_mean_temp_c,
        "health_score": health.overall,
    }

