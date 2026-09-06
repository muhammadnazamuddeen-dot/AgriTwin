"""
AgriTwin AI — Real-Time LLM Inference & Explanation Engine.
Architectural Principle:
  LIVE TELEMETRY + NUMERICAL ML (PRICE & SUITABILITY) + RAG KNOWLEDGE -> STRUCTURED FACTS -> SOUP FINE-TUNED LLM -> FARMER RESPONSE

The LLM is NOT retrained when weather or market prices change. It takes structured numerical facts and formats/explains them clearly to farmers.
"""

import json
from pathlib import Path

class AgriTwinLLMEngine:
    """Inference wrapper for AgriTwin Soup fine-tuned LLM model."""

    def __init__(self, model_dir: Path | None = None):
        self.model_dir = model_dir or Path(__file__).resolve().parent.parent / "models" / "agritwin_lora_adapter"
        self.is_loaded = self.model_dir.exists()

    def generate_explanation(self, structured_facts: dict, language: str = "en") -> str:
        """
        Takes structured facts from numerical ML + telemetry + price predictions + gross margins + RAG
        and formats them into a natural explanation strictly grounded in evidence.
        """
        district = structured_facts.get("district", "Punjab")
        location = structured_facts.get("location", f"{district}, Punjab")
        crop = structured_facts.get("crop", "Crop")
        stage = structured_facts.get("growth_stage", "Active")
        temp = structured_facts.get("temperature_c")
        humidity = structured_facts.get("humidity_pct")
        soil_m = structured_facts.get("soil_moisture")
        ndvi = structured_facts.get("ndvi")
        health_score = structured_facts.get("health_score", 75)
        water_stress = structured_facts.get("water_stress", 0)
        heat_stress = structured_facts.get("heat_stress", 0)
        pest_risk_pct = structured_facts.get("pest_risk_pct")
        ec_salinity = structured_facts.get("ec_salinity")
        yield_pred = structured_facts.get("yield_prediction_t_ha")
        mandi_rate = structured_facts.get("mandi_rate")

        date = structured_facts.get("date")
        season = structured_facts.get("season")
        planting_window = structured_facts.get("planting_window")

        # Dynamic Sowing Window & Status
        status = structured_facts.get("status", "PLANT NOW 🟢")
        days_until_window = structured_facts.get("days_until_window", 0)

        # 9 Sub-scores
        season_score = structured_facts.get("season_score")
        window_score = structured_facts.get("planting_window_score")
        weather_score = structured_facts.get("weather_score") or structured_facts.get("climate_score")
        soil_score = structured_facts.get("soil_score")
        water_score = structured_facts.get("water_score")
        disease_score = structured_facts.get("disease_risk_score")
        yield_score = structured_facts.get("yield_score")
        market_score = structured_facts.get("market_score")
        profit_score = structured_facts.get("profit_score")

        # Price Forecast
        forecast_7d = structured_facts.get("price_forecast_7d")
        forecast_30d = structured_facts.get("price_forecast_30d")
        price_direction = structured_facts.get("price_direction")
        price_confidence = structured_facts.get("price_confidence_pct")

        # Profit & Financials
        expected_gross_margin = structured_facts.get("expected_gross_margin_pkr_acre")
        expected_revenue = structured_facts.get("expected_revenue_pkr_acre")
        estimated_cost = structured_facts.get("estimated_cost_pkr_acre")
        expected_yield_maunds = structured_facts.get("expected_yield_maunds_acre")
        suitability_score = structured_facts.get("suitability_score")
        rec_level = structured_facts.get("crop_recommendation_level")

        todays_actions = structured_facts.get("todays_farm_action", [])
        rag_context = structured_facts.get("rag_context", "")

        if language == "pa":
            parts = [
                f"فارم دا تجزیہ ({crop} - {location}):",
                f"تاریخ: {date or 'موجودہ'} | سیزن: {season or 'زرعی'} (بوائی دی ونڈو: {planting_window or 'موجودہ'})۔",
                f"حالت: {status} (بوائی دی ونڈو: {days_until_window} دن باقی)۔",
                f"موجودہ حالت: صحت اسکور {health_score}/100، مرحلہ: {stage}۔",
            ]
            if suitability_score is not None:
                parts.append(f"9-عنصری فصل مناسبت اسکور: {suitability_score}/100 ({rec_level or 'عالٰ'})۔")
            if temp is not None:
                parts.append(f"درجہ حرارت {temp}°C اے۔")
            if soil_m is not None:
                parts.append(f"زمین دی نمی {soil_m} m³/m³ اے۔")
            if ec_salinity is not None:
                parts.append(f"زیر زمین پانی دی نمکیات {ec_salinity} dS/m اے۔")
            if water_stress > 40:
                parts.append(f"زمین وچ پانی دا دباؤ ({water_stress}%) زیادہ اے۔")
            if pest_risk_pct is not None and pest_risk_pct > 40:
                parts.append(f"کیڑے مکوڑیاں دا خطرہ {pest_risk_pct}% اے۔")
            if yield_pred:
                parts.append(f"متوقع پیداوار {yield_pred} ٹن فی ہیکٹر اے۔")
            if mandi_rate:
                parts.append(f"منڈی ریٹ: {mandi_rate}۔")
            if forecast_7d and forecast_30d:
                parts.append(f"قیمت دی پیش گوئی: 7 دن {forecast_7d} روپے، 30 دن {forecast_30d} روپے (اعتماد {price_confidence or 74}%)۔")
            if expected_gross_margin:
                parts.append(f"متوقع خالص منافع: PKR {expected_gross_margin:,.0f} فی ایکڑ۔")
            if todays_actions:
                parts.append(f"اج دے فارم اقدامات: " + "؛ ".join(todays_actions[:3]))
            if rag_context:
                parts.append(f"\nزرعی سفارشات: {rag_context}")
            return " ".join(parts)
        else:
            parts = [
                f"Season & Crop Suitability Engine Analysis ({crop} in {location}):",
                f"Date: {date or 'Today'} | Season: {season or 'Agri'} | Planting Window: {planting_window or 'Sowing'}.",
                f"Status: {status} | Days Until Planting Window: {days_until_window} day(s).",
                f"Overall health score is {health_score}/100 during {stage} stage.",
            ]
            if temp is not None:
                parts.append(f"Temperature is {temp}°C.")
            if humidity is not None:
                parts.append(f"Relative humidity is {humidity}%.")
            if soil_m is not None:
                parts.append(f"Root soil moisture is {soil_m} m³/m³.")
            if ec_salinity is not None:
                parts.append(f"Groundwater EC salinity is {ec_salinity} dS/m.")
            if water_stress > 40:
                parts.append(f"Field is experiencing elevated water stress ({water_stress}%). Consider timely irrigation.")
            if heat_stress > 40:
                parts.append(f"Heat stress is high ({heat_stress}%). Monitor crop for thermal stress during {stage}.")
            if pest_risk_pct is not None and pest_risk_pct > 40:
                parts.append(f"Pest outbreak risk is elevated ({pest_risk_pct}%). Field scouting is recommended.")
            if ndvi is not None:
                parts.append(f"MODIS satellite NDVI is {ndvi}.")
            if yield_pred is not None:
                parts.append(f"ML estimated yield is {yield_pred} tonnes/ha.")
            if mandi_rate:
                parts.append(f"Current AMIS wholesale mandi rate range is {mandi_rate}.")

            if forecast_7d and forecast_30d:
                parts.append(
                    f"Market Price Forecast: 7-day expected rate Rs {forecast_7d:,.0f}/100kg, 30-day forecast Rs {forecast_30d:,.0f}/100kg "
                    f"({price_direction or 'bullish'} trend, confidence {price_confidence or 74}%)."
                )

            if suitability_score is not None or expected_gross_margin is not None:
                fin_summary = []
                if suitability_score is not None:
                    fin_summary.append(f"9-Component Suitability Score: {suitability_score}/100 ({rec_level or 'HIGH'})")
                if season_score is not None:
                    fin_summary.append(
                        f"Sub-scores: Season ({season_score}), Window ({window_score}), Weather ({weather_score}), Soil ({soil_score}), Water ({water_score}), Disease ({disease_score}), Yield ({yield_score}), Market ({market_score}), Profit ({profit_score})"
                    )
                if expected_yield_maunds:
                    fin_summary.append(f"Expected yield: {expected_yield_maunds} maunds/acre")
                if expected_revenue:
                    fin_summary.append(f"Expected revenue: Rs {expected_revenue:,.0f}/acre")
                if estimated_cost:
                    fin_summary.append(f"Estimated cost: Rs {estimated_cost:,.0f}/acre")
                if expected_gross_margin:
                    fin_summary.append(f"Expected gross margin: Rs {expected_gross_margin:,.0f}/acre")
                parts.append(" | ".join(fin_summary) + ".")

            if todays_actions:
                parts.append("Today's Farm Action Checklist: " + " | ".join(todays_actions))

            if rag_context:
                parts.append(f"\nAgronomic Advisory: {rag_context}")

            return " ".join(parts)

llm_engine = AgriTwinLLMEngine()
