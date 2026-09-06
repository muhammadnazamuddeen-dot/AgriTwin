"""Pest & Disease Risk Engine — AgriTwin AI

Predictive risk model evaluating localized pest and pathogen threats for Punjab crops
based on thermal microclimate, relative humidity, canopy wetness, growth stage, and crop history.
"""

from typing import Any


PEST_DISEASE_KNOWLEDGE_BASE: list[dict[str, Any]] = [
    # ── WHEAT ─────────────────────────────────────────────────────────────────
    {
        "crop": "Wheat",
        "name": "Yellow / Stripe Rust",
        "category": "Disease",
        "stages": ["Tillering", "Jointing", "Booting", "Flowering"],
        "temp_min": 8.0,
        "temp_max": 22.0,
        "humidity_min": 70.0,
        "rainfall_required": False,
        "organic_control": "Apply Neem seed kernel extract (NSKE 5%) and grow rust-resistant Punjab cultivars (Akbar-19, Dilkash-20, Subhani-21).",
        "chemical_control": "Foliar spray of Propiconazole 25% EC @ 200 ml/acre or Tebuconazole 250 EC @ 200 ml/acre.",
        "preventative_measures": [
            "Avoid over-application of nitrogenous fertilizers",
            "Maintain optimal seed rate to prevent excessive humidity inside canopy",
            "Monitor lower leaf surfaces during cool, foggy morning periods",
        ],
    },
    {
        "crop": "Wheat",
        "name": "Wheat Aphid",
        "category": "Pest",
        "stages": ["Booting", "Flowering", "Grain Filling"],
        "temp_min": 16.0,
        "temp_max": 28.0,
        "humidity_min": 40.0,
        "rainfall_required": False,
        "organic_control": "Install 20 yellow sticky traps per acre and encourage bio-predators (Chrysoperla carnea / Ladybird beetles).",
        "chemical_control": "Spray Imidacloprid 200 SL @ 60 ml/acre or Acetamiprid 20% SP @ 60 g/acre if population exceeds Economic Threshold Level (ETL: 5-8 aphids/earhead).",
        "preventative_measures": [
            "Conserve natural predator populations by avoiding broad-spectrum chemical sprays early in the season",
            "Balance NPK fertilization to avoid succulent foliage",
        ],
    },
    {
        "crop": "Wheat",
        "name": "Armyworm",
        "category": "Pest",
        "stages": ["Jointing", "Booting", "Grain Filling"],
        "temp_min": 18.0,
        "temp_max": 32.0,
        "humidity_min": 60.0,
        "rainfall_required": False,
        "organic_control": "Spray Bacillus thuringiensis (Bt) @ 400 g/acre or apply neem oil concentrate.",
        "chemical_control": "Spray Emamectin benzoate 1.9 EC @ 200 ml/acre or Lufenuron 50 EC @ 100 ml/acre in evening hours.",
        "preventative_measures": [
            "Deep summer plowing to expose overwintering pupae",
            "Keep field borders clean of weed hosts",
        ],
    },
    # ── RICE ──────────────────────────────────────────────────────────────────
    {
        "crop": "Rice (Basmati)",
        "name": "Rice Blast",
        "category": "Disease",
        "stages": ["Nursery", "Tillering", "Panicle Initiation", "Flowering"],
        "temp_min": 18.0,
        "temp_max": 28.0,
        "humidity_min": 80.0,
        "rainfall_required": True,
        "organic_control": "Treat seeds with Trichoderma viride (4g/kg seed) and apply pseudomonas fluorescens spray.",
        "chemical_control": "Spray Tricyclazole 75 WP @ 120 g/acre or Isoprothiolane 40 EC @ 250 ml/acre.",
        "preventative_measures": [
            "Avoid excessive nitrogen application",
            "Avoid standing water drying out completely during susceptible flowering stage",
            "Use certified disease-free seeds",
        ],
    },
    {
        "crop": "Rice (Basmati)",
        "name": "Rice Stem Borer",
        "category": "Pest",
        "stages": ["Tillering", "Panicle Initiation", "Flowering"],
        "temp_min": 24.0,
        "temp_max": 36.0,
        "humidity_min": 60.0,
        "rainfall_required": False,
        "organic_control": "Install 8 light traps/acre or release Trichogramma japonicum parasitoids @ 50,000 eggs/acre.",
        "chemical_control": "Apply Cartap hydrochloride 4% GR @ 9 kg/acre or Chlorantraniliprole 0.4% GR @ 4 kg/acre in standing water.",
        "preventative_measures": [
            "Clip seedling tip leaves before transplanting to remove egg masses",
            "Maintain 2-3 inches of standing water during peak tillering",
        ],
    },
    {
        "crop": "Rice (Basmati)",
        "name": "Bacterial Leaf Blight (BLB)",
        "category": "Disease",
        "stages": ["Tillering", "Panicle Initiation", "Flowering", "Grain Filling"],
        "temp_min": 25.0,
        "temp_max": 34.0,
        "humidity_min": 80.0,
        "rainfall_required": True,
        "organic_control": "Foliar spray of fresh cow dung slurry extract (20%) or copper hydroxide.",
        "chemical_control": "Spray Copper oxychloride 50 WP (250g/acre) mixed with Streptocycline (6g/acre).",
        "preventative_measures": [
            "Ensure good field drainage after heavy monsoon rainstorms",
            "Avoid deep flooding that submerges leaf tips",
        ],
    },
    # ── COTTON ────────────────────────────────────────────────────────────────
    {
        "crop": "Cotton",
        "name": "Cotton Whitefly & CLCV Vector",
        "category": "Pest",
        "stages": ["Seedling", "Squaring", "Flowering", "Boll Formation"],
        "temp_min": 28.0,
        "temp_max": 42.0,
        "humidity_min": 45.0,
        "rainfall_required": False,
        "organic_control": "Install 25 yellow sticky cards/acre and spray Neem seed kernel extract (NSKE 5%).",
        "chemical_control": "Foliar spray of Pyriproxyfen 10.8 EC @ 500 ml/acre or Spirotetramat 240 SC @ 125 ml/acre.",
        "preventative_measures": [
            "Sow CLCV-tolerant Bt Cotton hybrids",
            "Eliminate weed hosts like Solanum nigrum (Mako) along field edges",
            "Avoid early chemical sprays that kill natural predatory mites",
        ],
    },
    {
        "crop": "Cotton",
        "name": "Pink Bollworm",
        "category": "Pest",
        "stages": ["Flowering", "Boll Formation", "Boll Opening"],
        "temp_min": 22.0,
        "temp_max": 38.0,
        "humidity_min": 50.0,
        "rainfall_required": False,
        "organic_control": "Install PB-Rope / Pheromone mating disruption dispensers (10 traps/acre).",
        "chemical_control": "Spray Triazophos 40 EC @ 800 ml/acre or Gamma-Cyhalothrin 60 g/L @ 100 ml/acre at initial rosette flower stage.",
        "preventative_measures": [
            "Shred and plow under crop residue immediately post-harvest",
            "Avoid keeping cotton sticks in fields as overwintering refuge",
        ],
    },
    {
        "crop": "Cotton",
        "name": "Cotton Jassid",
        "category": "Pest",
        "stages": ["Seedling", "Squaring", "Flowering"],
        "temp_min": 24.0,
        "temp_max": 35.0,
        "humidity_min": 65.0,
        "rainfall_required": False,
        "organic_control": "Spray neem oil 10,000 ppm @ 3 ml/L water.",
        "chemical_control": "Spray Flonicamid 50 WG @ 60 g/acre or Thiamethoxam 25 WG @ 24 g/acre when hopper burn symptoms appear.",
        "preventative_measures": [
            "Ensure recommended spacing between rows for adequate sunlight penetration",
            "Avoid excess nitrogen fertilization",
        ],
    },
    # ── SUGARCANE ─────────────────────────────────────────────────────────────
    {
        "crop": "Sugarcane",
        "name": "Sugarcane Top Borer",
        "category": "Pest",
        "stages": ["Tillering", "Grand Growth"],
        "temp_min": 28.0,
        "temp_max": 40.0,
        "humidity_min": 50.0,
        "rainfall_required": False,
        "organic_control": "Release Trichogramma chilonis parasites @ 20,000/acre at 10-day intervals.",
        "chemical_control": "Apply Carbofuran 3G @ 12 kg/acre or Chlorantraniliprole 18.5 SC @ 150 ml/acre in whorls.",
        "preventative_measures": [
            "Collect and destroy egg masses manually during early stage",
            "Remove shoot borer dead hearts",
        ],
    },
    {
        "crop": "Sugarcane",
        "name": "Red Rot",
        "category": "Disease",
        "stages": ["Grand Growth", "Maturation"],
        "temp_min": 26.0,
        "temp_max": 36.0,
        "humidity_min": 80.0,
        "rainfall_required": True,
        "organic_control": "Hot water seed sett treatment at 52°C for 30 min and plant Red Rot resistant cultivars (CPF-249).",
        "chemical_control": "Dip seed setts in Carbendazim 50 WP (2g/L water) before planting.",
        "preventative_measures": [
            "Ensure proper field drainage; do not allow stagnant irrigation water",
            "Rotate crop with legumes or paddy rice after sugarcane harvest",
        ],
    },
    # ── MAIZE ─────────────────────────────────────────────────────────────────
    {
        "crop": "Maize",
        "name": "Fall Armyworm (FAW)",
        "category": "Pest",
        "stages": ["Germination", "Vegetative", "Tasseling", "Silking"],
        "temp_min": 20.0,
        "temp_max": 35.0,
        "humidity_min": 50.0,
        "rainfall_required": False,
        "organic_control": "Apply dry sand + wood ash mixture (1:1 ratio) directly into central plant whorls or spray Bt toxins.",
        "chemical_control": "Foliar whorl application of Emamectin benzoate 5% WDG @ 75 g/acre or Spinetoram 11.7 SC @ 80 ml/acre.",
        "preventative_measures": [
            "Clean inter-cultivation to destroy weeds",
            "Sow synchronously with surrounding farms to prevent pest population concentration",
        ],
    },
    {
        "crop": "Maize",
        "name": "Maydis Leaf Blight",
        "category": "Disease",
        "stages": ["Vegetative", "Tasseling", "Grain Filling"],
        "temp_min": 20.0,
        "temp_max": 30.0,
        "humidity_min": 75.0,
        "rainfall_required": True,
        "organic_control": "Foliar spray of Bio-fungicide Trichoderma harzianum and practice crop rotation.",
        "chemical_control": "Foliar spray of Mancozeb 75 WP @ 500 g/acre or Azoxystrobin 23% SC @ 200 ml/acre.",
        "preventative_measures": [
            "Destroy infected crop debris after harvest",
            "Use certified hybrid seeds with leaf blight tolerance",
        ],
    },
]


def evaluate_pest_disease_risks(
    crop_name: str,
    growth_stage: str | None = None,
    temp_c: float | None = None,
    humidity_pct: float | None = None,
    rainfall_mm: float | None = None,
    ndvi: float | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """
    Evaluates microclimate, canopy density (NDVI), and growth stage against Punjab pathogen rules.
    Returns overall pest risk category ('Low', 'Moderate', 'High', 'Critical') and list of risk items.
    """
    if not crop_name:
        crop_name = "Wheat"

    c_name_lower = crop_name.lower()
    evaluated_risks: list[dict[str, Any]] = []

    for entry in PEST_DISEASE_KNOWLEDGE_BASE:
        kb_crop = entry["crop"].lower()
        if kb_crop not in c_name_lower and c_name_lower not in kb_crop:
            continue

        risk_score = 30  # Baseline vulnerability
        triggers: list[str] = []

        # 1. Growth Stage match check
        stages = entry["stages"]
        stage_matched = False
        if growth_stage:
            for s in stages:
                if s.lower() in growth_stage.lower() or growth_stage.lower() in s.lower():
                    stage_matched = True
                    break
        else:
            stage_matched = True  # Assume susceptible stage if unknown

        if stage_matched:
            risk_score += 25
            triggers.append(f"Crop is currently in vulnerable growth stage ({growth_stage or 'susceptible stage'})")

        # 2. Temperature condition check
        if temp_c is not None:
            t_min = entry["temp_min"]
            t_max = entry["temp_max"]
            if t_min <= temp_c <= t_max:
                risk_score += 25
                triggers.append(f"Ambient temperature ({temp_c:.1f}°C) is in optimal range for pathogen ({t_min}–{t_max}°C)")
            elif abs(temp_c - t_min) <= 4.0 or abs(temp_c - t_max) <= 4.0:
                risk_score += 10

        # 3. Humidity condition check
        if humidity_pct is not None:
            h_min = entry["humidity_min"]
            if humidity_pct >= h_min:
                risk_score += 20
                triggers.append(f"Relative humidity ({humidity_pct:.0f}%) meets threshold (≥{h_min:.0f}%)")
            elif humidity_pct >= (h_min - 10):
                risk_score += 10

        # 4. Rainfall / Leaf wetness check
        if entry.get("rainfall_required") and rainfall_mm and rainfall_mm > 0.5:
            risk_score += 15
            triggers.append(f"Recent rainfall ({rainfall_mm:.1f}mm) provides leaf wetness required for pathogen germination")

        # 5. Canopy density (NDVI) check
        if ndvi and ndvi > 0.70:
            risk_score += 10
            triggers.append(f"High canopy density (NDVI {ndvi:.2f}) traps micro-humidity inside lower leaf canopy")

        # Cap score between 0 and 100
        final_score = max(0, min(100, round(risk_score)))

        if final_score >= 75:
            risk_level = "High"
        elif final_score >= 50:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        evaluated_risks.append(
            {
                "pest_or_disease_name": entry["name"],
                "category": entry["category"],
                "risk_level": risk_level,
                "risk_score": final_score,
                "trigger_conditions": triggers if triggers else ["Standard seasonal monitoring advised"],
                "organic_control": entry["organic_control"],
                "chemical_control": entry["chemical_control"],
                "preventative_measures": entry["preventative_measures"],
            }
        )

    # Sort risks descending by score
    evaluated_risks.sort(key=lambda x: x["risk_score"], reverse=True)

    # Determine overall risk category
    if any(r["risk_level"] == "High" for r in evaluated_risks):
        overall_level = "High Risk"
    elif any(r["risk_level"] == "Medium" for r in evaluated_risks):
        overall_level = "Moderate Risk"
    else:
        overall_level = "Low Risk"

    return overall_level, evaluated_risks
