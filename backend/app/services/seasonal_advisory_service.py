"""
AgriTwin AI — Real-Time Seasonal & Temporal Advisory Engine.
Generates dynamic agronomic recommendations based on calendar month, active agricultural season 
(Kharif vs Rabi), phenological growth stage, and live weather telemetry.
"""

import datetime
from typing import Any

# Monthly Crop Advisory Rules Sourced from Punjab Agriculture Department Guidelines
MONTHLY_CROP_ADVISORIES = {
    # ── SEPTEMBER ────────────────────────────────────────────────────────────────
    9: {
        "season_name": "Late Kharif / Pre-Rabi Transition",
        "Wheat": {
            "focus": "Pre-sowing Land Preparation & Variety Selection",
            "advisory_en": "Prepare fields with laser land leveling. Procure certified seed (Akbar-19, Dilkash-20, Ghazi-19). Prepare land solarization and plan sowing between Oct 15 and Nov 20.",
            "advisory_pa": "گندم دی کاشت لئی لیزر لیولنگ کراؤ۔ تصدیق شدہ بیج (اکبر-19، دلکش-20) حاصل کرو تے 15 اکتوبر توں 20 نومبر دے درمیان کاشت دی منصوبہ بندی کرو۔"
        },
        "Cotton": {
            "focus": "Boll Opening & Pest Sanitation",
            "advisory_en": "Directorate Pest Warning Alert: Monitor Whitefly & Pink Bollworm. Avoid excess nitrogen. Maintain 6-7 day spray intervals. Stop irrigation when 60% bolls are open.",
            "advisory_pa": "کپاس لئی وائٹ فلائی تے گلابی سنڈی دا جائزہ لؤ۔ نائٹروجن دا زیادہ استعمال نہ کرو۔ 60% ٹینڈے کھلن تے پانی بند کر دیو۔"
        },
        "Rice (Basmati)": {
            "focus": "Panicle Initiation & Water Management",
            "advisory_en": "Keep 2-3 cm standing water during grain filling. Stop irrigation 10-14 days before harvest. Inspect for Stem Borer and Brown Plant Hopper.",
            "advisory_pa": "باسمتی چاول لئی دانے بنن وقت 2-3 سینٹی میٹر پانی قائم رکھو۔ کٹائی توں 10-14 دن پہلے پانی بند کر دیو۔"
        },
        "Sugarcane": {
            "focus": "Autumn Sowing & Crop Maturation",
            "advisory_en": "September is prime window for Autumn Sugarcane sowing. Intercrop with Lentil or Gram for additional profit.",
            "advisory_pa": "ستمبر ستمبر دی کماد دی کاشت لئی بہترین وقت اے۔ نال مسور یا چنا شامل کر کے اضافی منافع کماؤ۔"
        },
        "Maize": {
            "focus": "Kharif Grain Filling & Armyworm Protection",
            "advisory_en": "Ensure non-stress irrigation during silking and grain filling. Apply recommended insecticide if Fall Armyworm exceeds 5% threshold.",
            "advisory_pa": "مئی-چھلی وچ دانے بھرن وقت پانی دا دباؤ نہ آن دیو۔ فال آرمی ورم توں بچاؤ لئی باقاعدہ معائنہ کرو۔"
        },
        "Citrus (Kinnow)": {
            "focus": "Fruit Enlargement & Color Break Preparation",
            "advisory_en": "Maintain consistent soil moisture to prevent fruit splitting. Install methyl eugenol fruit fly traps across orchard boundaries.",
            "advisory_pa": "کنو دے باغ وچ پھل پھٹن توں بچان لئی باقاعدہ آبپاشی کرو تے فرٹ فلائی ٹریپ لگاؤ۔"
        }
    },

    # ── OCTOBER ──────────────────────────────────────────────────────────────────
    10: {
        "season_name": "Rabi Sowing Season Kickoff",
        "Wheat": {
            "focus": "Optimal Early Sowing Window",
            "advisory_en": "Begin wheat sowing for optimal yield potential. Treat seed with recommended fungicide (Dithane or Topas) before sowing. Apply DAP basal dose at sowing.",
            "advisory_pa": "گندم دی بروقت کاشت شروع کرو۔ بیج نوں زہر آلود کر کے بیجو تے بیجدے وقت ڈی اے پی دی پوری خوراک دیو۔"
        },
        "Rice (Basmati)": {
            "focus": "Harvesting & Moisture Management",
            "advisory_en": "Harvest when grain moisture reaches 20-22%. Avoid crop residue burning; incorporate paddy straw into soil with rotavator to preserve soil organic carbon.",
            "advisory_pa": "دھان دی کٹائی 20-22% نمی تے کرو۔ پرالی نوں آگ نہ لاؤ بلکہ روٹاویٹر نال زمین وچ ملاؤ۔"
        },
        "Cotton": {
            "focus": "First & Second Picking",
            "advisory_en": "Perform clean picking after dew dries in the morning. Store seed cotton in dry, ventilated stores to prevent moisture staining.",
            "advisory_pa": "شبنم خشک ہون توں بعد صاف چنائی کرو۔ پھٹی نوں خشک تے ہوادار جگہ تے رکھو۔"
        }
    },

    # ── NOVEMBER ─────────────────────────────────────────────────────────────────
    11: {
        "season_name": "Peak Rabi Sowing",
        "Wheat": {
            "focus": "Main Sowing & First Irrigation (CRI Stage)",
            "advisory_en": "Complete wheat sowing before Nov 20. Apply Crown Root Initiation (CRI) first irrigation at 20-25 days after sowing with 1 bag Urea.",
            "advisory_pa": "20 نومبر توں پہلے گندم دی کاشت مکمل کرو۔ 20-25 دن بعد کور دی پہلی آبپاشی تے یوریا دی بوری دیو۔"
        }
    },

    # ── DECEMBER ─────────────────────────────────────────────────────────────────
    12: {
        "season_name": "Rabi Mid-Season & Frost Protection",
        "Wheat": {
            "focus": "Tillering & Weed Control",
            "advisory_en": "Apply broadleaf and narrow-leaf herbicides 45 days after sowing when weeds are in 2-3 leaf stage. Ensure moist soil during herbicide spray.",
            "advisory_pa": "گندم وچ جڑی بوٹیاں دی تلفی لئی تر حالت وچ باقاعدہ سپرے کرو۔"
        }
    },

    # ── DEFAULT / OTHER MONTHS ────────────────────────────────────────────────────
    "default": {
        "season_name": "Active Agriculture Season",
        "general_en": "Maintain balanced fertilizer application, monitor weather forecasts, and ensure soil moisture retention.",
        "general_pa": "زمین دی نمی تے باقاعدہ گوڈی تے کھاد دا توازن برقرار رکھو۔"
    }
}


class SeasonalAdvisoryEngine:
    """Generates real-time time-and-season agronomic advisories."""

    def get_seasonal_recommendation(
        self,
        crop_name: str,
        district: str | None = None,
        telemetry: dict[str, Any] | None = None,
        reference_date: datetime.date | None = None
    ) -> dict[str, str]:
        """
        Returns real-time seasonal recommendation formatted in both English and Punjabi.
        """
        ref_dt = reference_date or datetime.date.today()
        month = ref_dt.month
        month_name = ref_dt.strftime("%B")

        telemetry = telemetry or {}
        temp = telemetry.get("temperature_c", 28.0)
        humidity = telemetry.get("humidity_pct", 55.0)
        soil_m = telemetry.get("soil_moisture", 0.22)
        rain = telemetry.get("rainfall_7d_mm", 0.0)

        # Lookup monthly rules
        month_rules = MONTHLY_CROP_ADVISORIES.get(month, MONTHLY_CROP_ADVISORIES["default"])
        season_name = month_rules.get("season_name", "Active Season")

        crop_rule = month_rules.get(crop_name, {})
        base_en = crop_rule.get(
            "advisory_en",
            f"During {month_name} ({season_name}), maintain regular scouting for {crop_name} in {district or 'Punjab'}."
        )
        base_pa = crop_rule.get(
            "advisory_pa",
            f"{month_name} دے مہینے وچ {crop_name} دی باقاعدہ دیکھ بھال کرو۔"
        )

        # Real-time weather modifier alerts
        weather_alerts_en = []
        weather_alerts_pa = []

        if temp > 35.0:
            weather_alerts_en.append(f"High temperature ({temp}°C) detected. Apply light evening irrigation or potassium foliar spray to prevent thermal shock.")
            weather_alerts_pa.append(f"زیادہ درجہ حرارت ({temp}°C) دی وجہ توں شام نوں ہلکی آبپاشی کرو۔")

        if soil_m < 0.16:
            weather_alerts_en.append(f"Root soil moisture is low ({soil_m} m³/m³). Schedule urgent irrigation according to your canal Warabandi turn.")
            weather_alerts_pa.append(f"زمین دی نمی کم ({soil_m} m³/m³) اے۔ واری دے مطابق فوراً پانی دیو۔")

        if humidity > 72.0 and temp >= 22.0 and temp <= 32.0:
            weather_alerts_en.append(f"High humidity ({humidity}%) and warm weather create high fungal pest risk. Field scouting recommended.")
            weather_alerts_pa.append(f"نمی ({humidity}%) زیادہ ہون کی وجہ توں پپوندی تے کیڑیاں دا خطرہ اے۔")

        if rain > 20.0:
            weather_alerts_en.append(f"Recent rain ({rain} mm) recorded. Postpone planned irrigation and ensure field drainage.")
            weather_alerts_pa.append(f"بارش ({rain} mm) ہون کر کے آبپاشی ملتوی کرو تے فالتو پانی نکالو۔")

        full_en = f"[{month_name} Season Advisory - {season_name}]: {base_en}"
        if weather_alerts_en:
            full_en += " " + " ".join(weather_alerts_en)

        full_pa = f"[{month_name} موسمی سفارشات]: {base_pa}"
        if weather_alerts_pa:
            full_pa += " " + " ".join(weather_alerts_pa)

        return {
            "month": month_name,
            "season": season_name,
            "advisory_en": full_en,
            "advisory_pa": full_pa
        }


seasonal_advisory_engine = SeasonalAdvisoryEngine()
