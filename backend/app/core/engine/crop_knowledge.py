AGRICULTURAL_ZONES = ["Punjab", "Sindh", "KPK", "Balochistan", "AJK/GB"]

CROP_ID_MAP = {
    "WHEAT_001": "Wheat",
    "RICE_001": "Rice (Basmati)",
    "RICE_COARSE_001": "Rice (Coarse)",
    "COTTON_001": "Cotton",
    "MAIZE_001": "Maize",
    "SUGARCANE_001": "Sugarcane",
    "POTATO_001": "Potato",
    "CHICKPEA_001": "Gram (Chickpea)",
    "CANOLA_001": "Canola / Mustard",
    "SUNFLOWER_001": "Sunflower",
    "BARLEY_001": "Barley",
    "LENTIL_001": "Lentil",
    "PEAS_001": "Peas",
}

REGION_PLANTING_WINDOWS = {
    "WHEAT_001": {
        "Punjab": {"start": "10-25", "end": "12-15"},
        "Sindh": {"start": "10-20", "end": "12-05"},
        "KPK": {"start": "10-15", "end": "11-30"},
        "Balochistan": {"start": "10-01", "end": "11-30"},
        "AJK/GB": {"start": "09-25", "end": "11-15"},
    },
    "RICE_001": {
        "Punjab": {"start": "06-01", "end": "07-15"},
        "Sindh": {"start": "05-15", "end": "06-30"},
        "KPK": {"start": "05-20", "end": "06-30"},
        "Balochistan": {"start": "05-10", "end": "06-20"},
        "AJK/GB": {"start": "05-15", "end": "06-25"},
    },
    "RICE_COARSE_001": {
        "Punjab": {"start": "05-20", "end": "07-10"},
        "Sindh": {"start": "05-01", "end": "06-20"},
        "KPK": {"start": "05-15", "end": "06-25"},
        "Balochistan": {"start": "05-01", "end": "06-15"},
        "AJK/GB": {"start": "05-10", "end": "06-20"},
    },
    "COTTON_001": {
        "Punjab": {"start": "04-15", "end": "06-30"},
        "Sindh": {"start": "04-01", "end": "05-31"},
        "KPK": {"start": "04-20", "end": "06-15"},
        "Balochistan": {"start": "04-10", "end": "05-31"},
        "AJK/GB": {"start": "04-25", "end": "06-10"},
    },
    "MAIZE_001": {
        "Punjab": {"start": "02-01", "end": "03-31"},
        "Sindh": {"start": "01-15", "end": "03-15"},
        "KPK": {"start": "03-01", "end": "04-30"},
        "Balochistan": {"start": "03-01", "end": "04-30"},
        "AJK/GB": {"start": "03-15", "end": "05-15"},
    },
    "SUGARCANE_001": {
        "Punjab": {"start": "02-01", "end": "03-31"},
        "Sindh": {"start": "01-15", "end": "03-15"},
        "KPK": {"start": "02-15", "end": "04-15"},
        "Balochistan": {"start": "02-01", "end": "03-31"},
        "AJK/GB": {"start": "03-01", "end": "04-15"},
    },
    "POTATO_001": {
        "Punjab": {"start": "10-01", "end": "10-31"},
        "Sindh": {"start": "10-15", "end": "11-15"},
        "KPK": {"start": "03-01", "end": "04-15"},
        "Balochistan": {"start": "03-01", "end": "04-15"},
        "AJK/GB": {"start": "03-15", "end": "05-01"},
    },
    "CHICKPEA_001": {
        "Punjab": {"start": "10-01", "end": "11-15"},
        "Sindh": {"start": "10-15", "end": "11-30"},
        "KPK": {"start": "09-25", "end": "11-10"},
        "Balochistan": {"start": "09-15", "end": "11-01"},
        "AJK/GB": {"start": "09-15", "end": "10-31"},
    },
    "CANOLA_001": {
        "Punjab": {"start": "10-01", "end": "11-15"},
        "Sindh": {"start": "10-15", "end": "11-30"},
        "KPK": {"start": "09-25", "end": "11-10"},
        "Balochistan": {"start": "09-20", "end": "11-05"},
        "AJK/GB": {"start": "09-15", "end": "10-31"},
    },
    "SUNFLOWER_001": {
        "Punjab": {"start": "01-15", "end": "03-01"},
        "Sindh": {"start": "01-01", "end": "02-15"},
        "KPK": {"start": "02-01", "end": "03-15"},
        "Balochistan": {"start": "02-01", "end": "03-15"},
        "AJK/GB": {"start": "02-15", "end": "03-31"},
    },
    "BARLEY_001": {
        "Punjab": {"start": "10-15", "end": "12-01"},
        "Sindh": {"start": "10-20", "end": "12-05"},
        "KPK": {"start": "10-01", "end": "11-20"},
        "Balochistan": {"start": "09-25", "end": "11-15"},
        "AJK/GB": {"start": "09-15", "end": "11-05"},
    },
    "LENTIL_001": {
        "Punjab": {"start": "10-15", "end": "11-30"},
        "Sindh": {"start": "10-20", "end": "12-05"},
        "KPK": {"start": "10-01", "end": "11-20"},
        "Balochistan": {"start": "09-25", "end": "11-15"},
        "AJK/GB": {"start": "09-15", "end": "11-05"},
    },
    "PEAS_001": {
        "Punjab": {"start": "10-01", "end": "11-15"},
        "Sindh": {"start": "10-15", "end": "11-30"},
        "KPK": {"start": "09-20", "end": "11-05"},
        "Balochistan": {"start": "09-15", "end": "10-31"},
        "AJK/GB": {"start": "09-10", "end": "10-25"},
    },
}

def get_crop_id(crop_name_or_id: str) -> str:
    """Resolve permanent crop_id from crop name or ID."""
    if not crop_name_or_id:
        return "WHEAT_001"
    clean = str(crop_name_or_id).strip()
    if clean.upper() in CROP_ID_MAP:
        return clean.upper()
    cn_lower = clean.lower()
    if "coarse" in cn_lower:
        return "RICE_COARSE_001"
    elif "basmati" in cn_lower:
        return "RICE_001"
    elif "rice" in cn_lower:
        return "RICE_001"
    elif "wheat" in cn_lower:
        return "WHEAT_001"
    elif "cotton" in cn_lower:
        return "COTTON_001"
    elif "maize" in cn_lower:
        return "MAIZE_001"
    elif "sugarcane" in cn_lower:
        return "SUGARCANE_001"
    elif "potato" in cn_lower:
        return "POTATO_001"
    elif "chickpea" in cn_lower or "gram" in cn_lower:
        return "CHICKPEA_001"
    elif "canola" in cn_lower or "mustard" in cn_lower:
        return "CANOLA_001"
    elif "sunflower" in cn_lower:
        return "SUNFLOWER_001"
    elif "barley" in cn_lower:
        return "BARLEY_001"
    elif "lentil" in cn_lower:
        return "LENTIL_001"
    elif "peas" in cn_lower:
        return "PEAS_001"
    for cid, name in CROP_ID_MAP.items():
        if name.lower() in cn_lower or cn_lower in name.lower():
            return cid
    return "WHEAT_001"

def get_crop_name(crop_id_or_name: str) -> str:
    """Resolve standard crop name from permanent crop_id or name."""
    if not crop_id_or_name:
        return "Wheat"
    cid = get_crop_id(crop_id_or_name)
    return CROP_ID_MAP.get(cid, "Wheat")

def normalize_province(province_str: str | None = None, district_str: str | None = None) -> str:
    """Normalize province / agricultural zone name to one of 5 Pakistani zones: Punjab, Sindh, KPK, Balochistan, AJK/GB."""
    if province_str and str(province_str).strip():
        p_clean = str(province_str).strip().lower()
        if "sindh" in p_clean or "sind" in p_clean:
            return "Sindh"
        elif "khyber" in p_clean or "kpk" in p_clean or "pakhtunkhwa" in p_clean:
            return "KPK"
        elif "balochistan" in p_clean or "baluchistan" in p_clean:
            return "Balochistan"
        elif "ajk" in p_clean or "kashmir" in p_clean or "gilgit" in p_clean or "gb" in p_clean or "baltistan" in p_clean:
            return "AJK/GB"
        elif "punjab" in p_clean:
            return "Punjab"

    if district_str and str(district_str).strip():
        d_clean = str(district_str).strip().lower()
        sindh_districts = ["karachi", "hyderabad", "sukkur", "larkana", "mirpur khas", "nawabshah", "badin", "thatta", "dadu", "ghotki", "jacobabad", "sanghar", "khairpur", "tharparkar", "shikarpur", "tando"]
        kpk_districts = ["peshawar", "mardan", "swat", "abbottabad", "mansehra", "charsadda", "swabi", "dera ismail khan", "d.i. khan", "kohat", "nowshera", "bannu", "dir", "haripur", "chitral"]
        baloch_districts = ["quetta", "turbat", "khuzdar", "chaman", "gwadar", "sibi", "zhob", "loralai", "pishin", "jaffarabad", "nasirabad", "mastung", "nushki"]
        ajkgb_districts = ["muzaffarabad", "mirpur", "rawalakot", "gilgit", "skardu", "hunza", "diamer", "ghanche"]

        for d in sindh_districts:
            if d in d_clean:
                return "Sindh"
        for d in kpk_districts:
            if d in d_clean:
                return "KPK"
        for d in baloch_districts:
            if d in d_clean:
                return "Balochistan"
        for d in ajkgb_districts:
            if d in d_clean:
                return "AJK/GB"

    return "Punjab"

# Sourced from Punjab Agriculture Department (https://agripunjab.gov.pk) & AMIS Mandi Rates (Sept 2026)
CROP_KNOWLEDGE_BASE: list[dict] = [
    {
        "crop_id": "WHEAT_001",
        "crop": "Wheat",
        "province": "Punjab",
        "season": "Rabi",
        "sowing_window": "October 15 – December 15",
        "harvest_window": "April – May",
        "optimal_temperature_c": {"min": 10, "max": 25, "critical_high": 35},
        "water_requirement_mm": 450,
        "mandi_rate_pkr_per_40kg": {"min": 2950, "max": 4775, "avg": 3850},
        "national_production_2026": "29.6 Million Tonnes (+4.6% YoY)",
        "growth_stages": [
            {"stage": "Germination", "days_after_sowing": "0–10", "water_sensitivity": "moderate"},
            {"stage": "Tillering", "days_after_sowing": "20–45", "water_sensitivity": "high"},
            {"stage": "Jointing", "days_after_sowing": "55–70", "water_sensitivity": "high"},
            {"stage": "Booting", "days_after_sowing": "75–90", "water_sensitivity": "critical"},
            {"stage": "Flowering", "days_after_sowing": "95–110", "water_sensitivity": "critical"},
            {"stage": "Grain Filling", "days_after_sowing": "115–140", "water_sensitivity": "moderate"},
            {"stage": "Maturity", "days_after_sowing": "145–160", "water_sensitivity": "low"},
        ],
        "common_pests": ["Aphids", "Army worm", "Termites", "Rust"],
        "advisory_2026": "Government promoting high-yield certified seed varieties to stabilize market prices above cost baseline.",
        "ndvi_healthy_range": (0.5, 0.9),
    },
    {
        "crop_id": "RICE_001",
        "crop": "Rice (Basmati)",
        "province": "Punjab",
        "season": "Kharif",
        "sowing_window": "June 1 – July 15",
        "harvest_window": "October – November",
        "optimal_temperature_c": {"min": 20, "max": 35, "critical_high": 40},
        "water_requirement_mm": 1200,
        "mandi_rate_pkr_per_40kg": {"min": 4400, "max": 13800, "avg": 9100},
        "national_production_2026": "10.0 Million Tonnes (+2.8% YoY)",
        "growth_stages": [
            {"stage": "Nursery", "days_after_sowing": "0–30", "water_sensitivity": "high"},
            {"stage": "Transplanting", "days_after_sowing": "25–35", "water_sensitivity": "critical"},
            {"stage": "Tillering", "days_after_sowing": "35–60", "water_sensitivity": "high"},
            {"stage": "Panicle Initiation", "days_after_sowing": "60–80", "water_sensitivity": "critical"},
            {"stage": "Flowering", "days_after_sowing": "80–100", "water_sensitivity": "critical"},
            {"stage": "Grain Filling", "days_after_sowing": "100–130", "water_sensitivity": "high"},
            {"stage": "Maturity", "days_after_sowing": "130–150", "water_sensitivity": "low"},
        ],
        "common_pests": ["Stem borer", "Leaf folder", "Blast", "Bacterial leaf blight"],
        "advisory_2026": "High export profitability. Monitor for Stem Borer & Leaf Folder during humid monsoons.",
        "ndvi_healthy_range": (0.6, 0.9),
    },
    {
        "crop_id": "RICE_COARSE_001",
        "crop": "Rice (Coarse)",
        "province": "Punjab",
        "season": "Kharif",
        "sowing_window": "May 20 – July 10",
        "harvest_window": "October – November",
        "optimal_temperature_c": {"min": 20, "max": 36, "critical_high": 42},
        "water_requirement_mm": 1100,
        "mandi_rate_pkr_per_40kg": {"min": 2100, "max": 4200, "avg": 3500},
        "national_production_2026": "4.5 Million Tonnes",
        "growth_stages": [
            {"stage": "Nursery", "days_after_sowing": "0–25", "water_sensitivity": "high"},
            {"stage": "Transplanting", "days_after_sowing": "20–30", "water_sensitivity": "critical"},
            {"stage": "Tillering", "days_after_sowing": "30–55", "water_sensitivity": "high"},
            {"stage": "Panicle Initiation", "days_after_sowing": "55–75", "water_sensitivity": "critical"},
            {"stage": "Flowering", "days_after_sowing": "75–95", "water_sensitivity": "critical"},
            {"stage": "Grain Filling", "days_after_sowing": "95–115", "water_sensitivity": "high"},
            {"stage": "Maturity", "days_after_sowing": "115–130", "water_sensitivity": "low"},
        ],
        "common_pests": ["Stem borer", "Leaf folder", "Bacterial blight"],
        "advisory_2026": "High-yielding coarse varieties for local consumption and milling.",
        "ndvi_healthy_range": (0.6, 0.9),
    },
    {
        "crop_id": "COTTON_001",
        "crop": "Cotton",
        "province": "Punjab",
        "season": "Kharif",
        "sowing_window": "April 15 – June 30",
        "harvest_window": "September – December",
        "optimal_temperature_c": {"min": 21, "max": 35, "critical_high": 42},
        "water_requirement_mm": 700,
        "mandi_rate_pkr_per_40kg": {"min": 8000, "max": 9350, "avg": 8675},
        "national_production_2026": "7.1 Million Bales",
        "growth_stages": [
            {"stage": "Germination", "days_after_sowing": "0–10", "water_sensitivity": "moderate"},
            {"stage": "Seedling", "days_after_sowing": "10–30", "water_sensitivity": "moderate"},
            {"stage": "Squaring", "days_after_sowing": "40–60", "water_sensitivity": "high"},
            {"stage": "Flowering", "days_after_sowing": "60–100", "water_sensitivity": "critical"},
            {"stage": "Boll Formation", "days_after_sowing": "100–140", "water_sensitivity": "high"},
            {"stage": "Boll Opening", "days_after_sowing": "140–180", "water_sensitivity": "low"},
        ],
        "common_pests": ["Bollworm", "Whitefly", "Jassid", "Pink bollworm", "CLCV"],
        "advisory_2026": "Directorate General Pest Warning Alert (Sept 2026): Active Whitefly & Pink Bollworm. Maintain 6-day spray cycles for Whitefly and 6-7 day intervals for Pink Bollworm before Sept 20.",
        "ndvi_healthy_range": (0.5, 0.85),
    },
    {
        "crop_id": "SUGARCANE_001",
        "crop": "Sugarcane",
        "province": "Punjab",
        "season": "Kharif (annual)",
        "sowing_window": "February – March (spring) / September – October (autumn)",
        "harvest_window": "November – March (12–18 months)",
        "optimal_temperature_c": {"min": 20, "max": 35, "critical_high": 42},
        "water_requirement_mm": 1500,
        "mandi_rate_pkr_per_40kg": {"min": 2600, "max": 3220, "avg": 2910},
        "national_production_2026": "89.5 Million Tonnes (Record +6.2% YoY)",
        "growth_stages": [
            {"stage": "Germination", "days_after_sowing": "0–30", "water_sensitivity": "moderate"},
            {"stage": "Tillering", "days_after_sowing": "30–90", "water_sensitivity": "high"},
            {"stage": "Grand Growth", "days_after_sowing": "90–240", "water_sensitivity": "critical"},
            {"stage": "Maturation", "days_after_sowing": "240–360", "water_sensitivity": "low"},
        ],
        "common_pests": ["Top borer", "Early shoot borer", "Pyralid borer", "Red rot"],
        "advisory_2026": "Record crop yields in 2026. Ensure adequate irrigation during Grand Growth stage.",
        "ndvi_healthy_range": (0.6, 0.9),
    },
    {
        "crop_id": "MAIZE_001",
        "crop": "Maize",
        "province": "Punjab",
        "season": "Kharif / Spring",
        "sowing_window": "February – March (spring) / July – August (Kharif)",
        "harvest_window": "May – June (spring) / October – November (Kharif)",
        "optimal_temperature_c": {"min": 18, "max": 32, "critical_high": 38},
        "water_requirement_mm": 500,
        "mandi_rate_pkr_per_40kg": {"min": 2390, "max": 4600, "avg": 3495},
        "national_production_2026": "8.8 Million Tonnes",
        "growth_stages": [
            {"stage": "Germination", "days_after_sowing": "0–10", "water_sensitivity": "moderate"},
            {"stage": "Vegetative", "days_after_sowing": "15–50", "water_sensitivity": "high"},
            {"stage": "Tasseling", "days_after_sowing": "50–65", "water_sensitivity": "critical"},
            {"stage": "Silking", "days_after_sowing": "65–75", "water_sensitivity": "critical"},
            {"stage": "Grain Filling", "days_after_sowing": "75–110", "water_sensitivity": "high"},
            {"stage": "Maturity", "days_after_sowing": "110–130", "water_sensitivity": "low"},
        ],
        "common_pests": ["Fall armyworm", "Stem borer", "Leaf blight"],
        "advisory_2026": "Scout for Fall Armyworm during Vegetative and Tasseling stages.",
        "ndvi_healthy_range": (0.6, 0.9),
    },
    {
        "crop_id": "POTATO_001",
        "crop": "Potato",
        "province": "Punjab",
        "season": "Rabi",
        "sowing_window": "October 1 – October 31",
        "harvest_window": "January 15 – February 28",
        "optimal_temperature_c": {"min": 12, "max": 24, "critical_high": 30},
        "water_requirement_mm": 450,
        "mandi_rate_pkr_per_40kg": {"min": 2200, "max": 3100, "avg": 2650},
        "national_production_2026": "8.2 Million Tonnes",
        "growth_stages": [
            {"stage": "Sprouting / Emergence", "days_after_sowing": "0–15", "water_sensitivity": "moderate"},
            {"stage": "Vegetative Growth", "days_after_sowing": "15–35", "water_sensitivity": "high"},
            {"stage": "Tuber Initiation", "days_after_sowing": "35–55", "water_sensitivity": "critical"},
            {"stage": "Tuber Bulking", "days_after_sowing": "55–90", "water_sensitivity": "critical"},
            {"stage": "Maturation", "days_after_sowing": "90–110", "water_sensitivity": "low"},
        ],
        "common_pests": ["Late Blight", "Early Blight", "Aphids", "Potato Tuber Moth"],
        "advisory_2026": "High potential gross returns in central Punjab. Protect against Late Blight during foggy humid weather.",
        "ndvi_healthy_range": (0.55, 0.85),
    },
    {
        "crop_id": "CANOLA_001",
        "crop": "Canola / Mustard",
        "province": "Punjab",
        "season": "Rabi",
        "sowing_window": "October 1 – November 15",
        "harvest_window": "February 15 – March 31",
        "optimal_temperature_c": {"min": 10, "max": 25, "critical_high": 32},
        "water_requirement_mm": 300,
        "mandi_rate_pkr_per_40kg": {"min": 5800, "max": 7200, "avg": 6650},
        "national_production_2026": "1.4 Million Tonnes",
        "growth_stages": [
            {"stage": "Germination", "days_after_sowing": "0–10", "water_sensitivity": "moderate"},
            {"stage": "Rosette Stage", "days_after_sowing": "10–35", "water_sensitivity": "moderate"},
            {"stage": "Bolting & Flowering", "days_after_sowing": "35–70", "water_sensitivity": "critical"},
            {"stage": "Pod Development", "days_after_sowing": "70–100", "water_sensitivity": "high"},
            {"stage": "Maturity", "days_after_sowing": "100–120", "water_sensitivity": "low"},
        ],
        "common_pests": ["Mustard Aphid", "White Rust", "Powdery Mildew"],
        "advisory_2026": "Promoted by Govt for domestic oilseed self-sufficiency. Excellent drought tolerance.",
        "ndvi_healthy_range": (0.5, 0.85),
    },
    {
        "crop_id": "CHICKPEA_001",
        "crop": "Gram (Chickpea)",
        "province": "Punjab",
        "season": "Rabi",
        "sowing_window": "October 1 – November 15",
        "harvest_window": "March 15 – April 30",
        "optimal_temperature_c": {"min": 10, "max": 28, "critical_high": 35},
        "water_requirement_mm": 250,
        "mandi_rate_pkr_per_40kg": {"min": 8200, "max": 10500, "avg": 9350},
        "national_production_2026": "0.6 Million Tonnes",
        "growth_stages": [
            {"stage": "Germination", "days_after_sowing": "0–12", "water_sensitivity": "low"},
            {"stage": "Vegetative Branching", "days_after_sowing": "12–45", "water_sensitivity": "moderate"},
            {"stage": "Flowering & Podging", "days_after_sowing": "45–90", "water_sensitivity": "critical"},
            {"stage": "Pod Filling", "days_after_sowing": "90–115", "water_sensitivity": "high"},
            {"stage": "Maturity", "days_after_sowing": "115–130", "water_sensitivity": "low"},
        ],
        "common_pests": ["Pod Borer (Helicoverpa)", "Chickpea Wilt (Fusarium)", "Ascochyta Blight"],
        "advisory_2026": "Ideal for Thal desert and rainfed (Barani) zones. Low water consumption.",
        "ndvi_healthy_range": (0.45, 0.8),
    },
    {
        "crop_id": "SUNFLOWER_001",
        "crop": "Sunflower",
        "province": "Punjab",
        "season": "Zaid / Spring",
        "sowing_window": "January 15 – March 01",
        "harvest_window": "May 01 – June 15",
        "optimal_temperature_c": {"min": 18, "max": 32, "critical_high": 40},
        "water_requirement_mm": 400,
        "mandi_rate_pkr_per_40kg": {"min": 6500, "max": 8200, "avg": 7350},
        "national_production_2026": "0.8 Million Tonnes",
        "growth_stages": [
            {"stage": "Germination", "days_after_sowing": "0–10", "water_sensitivity": "moderate"},
            {"stage": "Vegetative", "days_after_sowing": "10–40", "water_sensitivity": "moderate"},
            {"stage": "Button Stage & Flowering", "days_after_sowing": "40–65", "water_sensitivity": "critical"},
            {"stage": "Seed Development", "days_after_sowing": "65–95", "water_sensitivity": "high"},
            {"stage": "Maturity", "days_after_sowing": "95–110", "water_sensitivity": "low"},
        ],
        "common_pests": ["Head Rot", "Cutworm", "Whitefly", "Jassid"],
        "advisory_2026": "Short duration cash crop between Rabi wheat and Kharif rice/cotton.",
        "ndvi_healthy_range": (0.5, 0.85),
    },
    {
        "crop_id": "BARLEY_001",
        "crop": "Barley",
        "province": "Punjab",
        "season": "Rabi",
        "sowing_window": "October 15 – December 01",
        "harvest_window": "March 15 – April 30",
        "optimal_temperature_c": {"min": 8, "max": 24, "critical_high": 32},
        "water_requirement_mm": 250,
        "mandi_rate_pkr_per_40kg": {"min": 2500, "max": 3500, "avg": 3000},
        "national_production_2026": "0.4 Million Tonnes",
        "growth_stages": [
            {"stage": "Germination", "days_after_sowing": "0–10", "water_sensitivity": "low"},
            {"stage": "Tillering", "days_after_sowing": "10–40", "water_sensitivity": "moderate"},
            {"stage": "Heading / Flowering", "days_after_sowing": "40–75", "water_sensitivity": "high"},
            {"stage": "Grain Filling", "days_after_sowing": "75–105", "water_sensitivity": "moderate"},
            {"stage": "Maturity", "days_after_sowing": "105–120", "water_sensitivity": "low"},
        ],
        "common_pests": ["Aphids", "Covered Smut", "Net Blotch"],
        "advisory_2026": "High tolerance to soil salinity and drought compared to wheat.",
        "ndvi_healthy_range": (0.45, 0.8),
    },
    {
        "crop_id": "LENTIL_001",
        "crop": "Lentil",
        "province": "Punjab",
        "season": "Rabi",
        "sowing_window": "October 15 – November 30",
        "harvest_window": "March 01 – April 15",
        "optimal_temperature_c": {"min": 10, "max": 25, "critical_high": 32},
        "water_requirement_mm": 250,
        "mandi_rate_pkr_per_40kg": {"min": 7500, "max": 9500, "avg": 8500},
        "national_production_2026": "0.3 Million Tonnes",
        "growth_stages": [
            {"stage": "Germination", "days_after_sowing": "0–10", "water_sensitivity": "low"},
            {"stage": "Vegetative", "days_after_sowing": "10–40", "water_sensitivity": "moderate"},
            {"stage": "Flowering & Pod Setting", "days_after_sowing": "40–75", "water_sensitivity": "critical"},
            {"stage": "Pod Filling", "days_after_sowing": "75–100", "water_sensitivity": "moderate"},
            {"stage": "Maturity", "days_after_sowing": "100–110", "water_sensitivity": "low"},
        ],
        "common_pests": ["Lentil Wilt", "Rust", "Aphids"],
        "advisory_2026": "Valuable pulse crop with strong nitrogen fixation benefits for soil health.",
        "ndvi_healthy_range": (0.45, 0.8),
    },
    {
        "crop_id": "PEAS_001",
        "crop": "Peas",
        "province": "Punjab",
        "season": "Rabi",
        "sowing_window": "October 01 – November 15",
        "harvest_window": "January 15 – March 15",
        "optimal_temperature_c": {"min": 10, "max": 22, "critical_high": 28},
        "water_requirement_mm": 300,
        "mandi_rate_pkr_per_40kg": {"min": 3800, "max": 5200, "avg": 4500},
        "national_production_2026": "0.5 Million Tonnes",
        "growth_stages": [
            {"stage": "Germination", "days_after_sowing": "0–10", "water_sensitivity": "moderate"},
            {"stage": "Vegetative", "days_after_sowing": "10–30", "water_sensitivity": "moderate"},
            {"stage": "Flowering & Pod Formation", "days_after_sowing": "30–60", "water_sensitivity": "critical"},
            {"stage": "Pod Filling / Green Picking", "days_after_sowing": "60–80", "water_sensitivity": "high"},
            {"stage": "Maturity", "days_after_sowing": "80–90", "water_sensitivity": "low"},
        ],
        "common_pests": ["Powdery Mildew", "Pea Aphid", "Pod Borer"],
        "advisory_2026": "High value vegetable crop with multiple pickings during winter season.",
        "ndvi_healthy_range": (0.5, 0.85),
    },
]


import datetime
import re


def get_crop_info(crop_name: str) -> dict | None:
    """Look up crop info by name or crop_id (case-insensitive)."""
    if not crop_name:
        return None
    cn_clean = str(crop_name).strip()
    for entry in CROP_KNOWLEDGE_BASE:
        if entry.get("crop_id", "").upper() == cn_clean.upper():
            return entry
        if entry["crop"].lower() == cn_clean.lower():
            return entry
    for entry in CROP_KNOWLEDGE_BASE:
        if cn_clean.lower() in entry["crop"].lower() or entry["crop"].lower() in cn_clean.lower():
            return entry
    return None


def list_crops() -> list[str]:
    """Return list of all known crop names."""
    return [entry["crop"] for entry in CROP_KNOWLEDGE_BASE]


def derive_growth_stage(
    crop_name: str,
    sowing_date: str | datetime.date | datetime.datetime | None,
    reference_date: datetime.date | None = None,
) -> dict:
    """
    Auto-derive crop growth stage dynamically from sowing date using Punjab Agricultural Knowledge tables.
    Returns stage name, days after sowing (DAS), water sensitivity, stage index, and full stages list.
    """
    if not sowing_date:
        return {
            "stage": "Vegetative",
            "days_after_sowing": None,
            "water_sensitivity": "moderate",
            "stage_index": 1,
            "stages": [],
            "is_harvested": False,
        }

    if isinstance(sowing_date, str):
        try:
            sowing_dt = datetime.date.fromisoformat(sowing_date.split("T")[0])
        except Exception:
            return {
                "stage": "Vegetative",
                "days_after_sowing": None,
                "water_sensitivity": "moderate",
                "stage_index": 1,
                "stages": [],
                "is_harvested": False,
            }
    elif isinstance(sowing_date, datetime.datetime):
        sowing_dt = sowing_date.date()
    elif isinstance(sowing_date, datetime.date):
        sowing_dt = sowing_date
    else:
        return {
            "stage": "Vegetative",
            "days_after_sowing": None,
            "water_sensitivity": "moderate",
            "stage_index": 1,
            "stages": [],
            "is_harvested": False,
        }

    ref_dt = reference_date or datetime.date.today()
    days_elapsed = (ref_dt - sowing_dt).days

    crop_info = get_crop_info(crop_name)
    if not crop_info or "growth_stages" not in crop_info:
        if days_elapsed < 14:
            stage_name = "Emergence / Germination"
            idx = 0
            sens = "moderate"
        elif days_elapsed < 50:
            stage_name = "Vegetative Growth"
            idx = 1
            sens = "high"
        elif days_elapsed < 85:
            stage_name = "Flowering / Reproduction"
            idx = 2
            sens = "critical"
        elif days_elapsed < 125:
            stage_name = "Grain / Fruit Filling"
            idx = 3
            sens = "high"
        elif days_elapsed <= 160:
            stage_name = "Maturity"
            idx = 4
            sens = "low"
        else:
            stage_name = "Post-Maturity / Harvested"
            idx = 5
            sens = "low"

        return {
            "stage": stage_name,
            "days_after_sowing": max(0, days_elapsed),
            "water_sensitivity": sens,
            "stage_index": idx,
            "stages": [],
            "is_harvested": days_elapsed > 160,
        }

    stages = crop_info["growth_stages"]

    if days_elapsed < 0:
        return {
            "stage": "Pre-sowing",
            "days_after_sowing": days_elapsed,
            "water_sensitivity": "low",
            "stage_index": 0,
            "stages": stages,
            "is_harvested": False,
        }

    parsed_stages = []
    for idx, s in enumerate(stages):
        das_str = s.get("days_after_sowing", "")
        nums = [int(n) for n in re.findall(r"\d+", das_str)]
        if len(nums) >= 2:
            min_d, max_d = nums[0], nums[1]
        elif len(nums) == 1:
            min_d, max_d = nums[0], nums[0] + 15
        else:
            min_d, max_d = 0, 999
        parsed_stages.append((idx, min_d, max_d, s))

    for idx, min_d, max_d, s in parsed_stages:
        if min_d <= days_elapsed <= max_d:
            return {
                "stage": s["stage"],
                "days_after_sowing": days_elapsed,
                "water_sensitivity": s.get("water_sensitivity", "moderate"),
                "stage_index": idx,
                "stages": stages,
                "is_harvested": False,
            }

    for i in range(len(parsed_stages) - 1):
        curr_max = parsed_stages[i][2]
        next_min = parsed_stages[i + 1][1]
        if curr_max < days_elapsed < next_min:
            s = parsed_stages[i + 1][3]
            return {
                "stage": s["stage"],
                "days_after_sowing": days_elapsed,
                "water_sensitivity": s.get("water_sensitivity", "moderate"),
                "stage_index": parsed_stages[i + 1][0],
                "stages": stages,
                "is_harvested": False,
            }

    last_idx, _, last_max, last_s = parsed_stages[-1]
    if days_elapsed > last_max:
        return {
            "stage": f"Post-{last_s['stage']} (Ready for Harvest)",
            "days_after_sowing": days_elapsed,
            "water_sensitivity": "low",
            "stage_index": last_idx,
            "stages": stages,
            "is_harvested": True,
        }

    first_s = parsed_stages[0][3]
    return {
        "stage": first_s["stage"],
        "days_after_sowing": days_elapsed,
        "water_sensitivity": first_s.get("water_sensitivity", "moderate"),
        "stage_index": 0,
        "stages": stages,
        "is_harvested": False,
    }
