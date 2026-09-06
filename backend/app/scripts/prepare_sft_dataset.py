"""
AgriTwin AI — SFT Dataset Generator for LLM Fine-Tuning & Competition Submission.
Generates multi-turn agricultural instruction pairs covering:
  1. Precision Agronomy & NDVI Satellite Diagnostics
  2. Weather Telemetry & Climate Anomaly Analysis
  3. Directorate General Pest Warning Advisories (Sept 2026)
  4. Warabandi Rotational Canal Water Distribution
  5. Punjab AMIS Mandi Price Intelligence
  6. Bilingual English and Punjabi (Shahmukhi) responses.
"""

import json
import os
from pathlib import Path

# SFT Instruction Examples Generator
def generate_sft_pairs():
    pairs = [
        {
            "system": "You are AgriTwin AI, the expert Punjab Precision Agriculture & AI Diagnostic Copilot. Provide evidence-grounded, actionable advice for farmers in English and Punjabi.",
            "instruction": "My cotton crop in Multan is showing whitefly and pink bollworm activity. What is the recommended treatment plan according to official Punjab advisories?",
            "response": "Based on the Directorate General of Pest Warning & Quality Control of Pesticides (Punjab Agriculture Dept) September 2026 alert:\n1. Whitefly Control: Conduct targeted spray cycles with recommended insecticides at minimum 6-day intervals.\n2. Pink Bollworm: Maintain 6 to 7-day spray intervals. Aim to complete 3 spray cycles by September 20 to protect bolls before opening.\n3. Water Drainage: Ensure zero stagnant monsoon rainwater in fields (standing water causes root damage within 48 hours).\n\nپنجاب محکمہ زراعت الرٹ (ستمبر 2026):\n1. سفید مکھی لئی 6 دن دے وقفے نال سپرے کرو۔\n2. گلابی سنڈی لئی 6-7 دن دا وقفہ رکھو تے 20 ستمبر توں پہلے 3 سپرے مکمل کرو۔"
        },
        {
            "system": "You are AgriTwin AI, the expert Punjab Precision Agriculture & AI Diagnostic Copilot.",
            "instruction": "What are the latest September 2026 Mandi rates for Wheat, Rice, and Cotton in Punjab?",
            "response": "According to the Punjab Agriculture Market Information Service (AMIS) September 2026 wholesale mandi rates:\n- Wheat: PKR 2,950 – 4,775 per 40 kg (Average: PKR 3,850)\n- Basmati Rice: PKR 4,400 – 13,800 per 40 kg (Average: PKR 9,100)\n- Seed Cotton (Phutti): PKR 8,000 – 9,350 per 40 kg (Average: PKR 8,675)\n- Sugarcane: PKR 2,600 – 3,220 per 40 kg (Average: PKR 2,910)\n- Maize: PKR 2,390 – 4,600 per 40 kg (Average: PKR 3,495)"
        },
        {
            "system": "You are AgriTwin AI, the expert Punjab Precision Agriculture & AI Diagnostic Copilot.",
            "instruction": "Explain how the Warabandi canal water irrigation system works in Punjab.",
            "response": "Warabandi is an equitable, rotational canal water distribution system regulated by the Punjab Irrigation Department and IRSA (Indus River System Authority):\n1. Fixed Turn Allocation: Each farm receives a weekly allocated time slot (Wari) proportional to field acreage.\n2. Watercourse Losses: Conveyance losses are accounted for through head-to-tail timing adjustments.\n3. Modern Efficiency: The CM Water Efficient Agriculture Program provides 60% subsidies on laser land leveling and watercourse lining to reduce conveyance loss."
        },
        {
            "system": "You are AgriTwin AI, the expert Punjab Precision Agriculture & AI Diagnostic Copilot.",
            "instruction": "How do MODIS satellite NDVI values indicate crop health in Faisalabad?",
            "response": "MODIS Terra 250m 16-day composite NDVI measures canopy biomass and chlorophyll activity:\n- NDVI > 0.70: Dense, healthy vegetative canopy (Optimal Condition).\n- NDVI 0.45 – 0.65: Moderate canopy development or early growth stage.\n- NDVI < 0.40: Potential moisture stress, pest damage, or delayed sowing.\nAgriTwin AI cross-references MODIS NDVI with Open-Meteo root soil moisture (0-7cm) to differentiate drought stress from nutrient deficiency."
        },
        {
            "system": "You are AgriTwin AI, the expert Punjab Precision Agriculture & AI Diagnostic Copilot.",
            "instruction": "What is the recommended sowing window and GDD requirement for Rabi Wheat in Punjab?",
            "response": "For Rabi Wheat in Punjab:\n- Optimal Sowing Window: November 1 to November 20 (late sowing beyond Dec 15 reduces yield by 15-20 kg/acre per day).\n- Seed Rate: 45-50 kg/acre for timely sowing; 55-60 kg/acre for late sowing.\n- Growth Stages: CRI (20-25 DAS), Tillering (40-45 DAS), Booting (75-80 DAS), Flowering (90-95 DAS), Grain Filling (110-125 DAS).\n- Critical Irrigations: Crown Root Initiation (CRI) and Flowering are non-negotiable for max yield."
        }
    ]

    # Expand dataset variations for robust LLM fine-tuning
    expanded = []
    crops = [
        ("Wheat", "گندم (کنک)", "Rabi", "Nov 1 - Nov 20", "29.6 Million Tonnes"),
        ("Rice (Basmati)", "دھان (باسمتی چاول)", "Kharif", "June 1 - July 15", "10.0 Million Tonnes"),
        ("Cotton", "کپاس (پھٹی)", "Kharif", "April 15 - June 15", "7.1 Million Bales"),
        ("Sugarcane", "کماد (گنا)", "Annual", "Feb - March / Sept - Oct", "89.5 Million Tonnes"),
        ("Maize", "مکئی (چھلی)", "Spring/Kharif", "Feb - March / July - Aug", "8.8 Million Tonnes"),
    ]

    for crop_en, crop_ur, season, sowing, prod in crops:
        expanded.append({
            "messages": [
                {"role": "system", "content": "You are AgriTwin AI, the Punjab Agriculture & Precision Diagnostic Copilot."},
                {"role": "user", "content": f"Provide comprehensive agronomic guidelines for {crop_en} ({crop_ur}) in Punjab."},
                {"role": "assistant", "content": f"Here are the official agronomic specs for {crop_en} ({crop_ur}) in Punjab:\n- Season: {season}\n- Optimal Sowing: {sowing}\n- National Output (2026): {prod}\n- Soil Moisture Target: 0.20-0.35 m³/m³\n- Key Pest Risks: See DG Pest Warning alerts.\n- Bilingual Note: {crop_ur} لئی باقاعدہ وادی تے پانی دا معائینہ ضروری اے۔"}
            ]
        })

    for p in pairs:
        expanded.append({
            "messages": [
                {"role": "system", "content": p["system"]},
                {"role": "user", "content": p["instruction"]},
                {"role": "assistant", "content": p["response"]}
            ]
        })

    return expanded

def main():
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir.parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    sft_file = data_dir / "agritwin_sft_dataset.jsonl"

    data = generate_sft_pairs()
    with open(sft_file, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"=== AgriTwin AI SFT Dataset Generated ===")
    print(f"Total Fine-Tuning Samples: {len(data)}")
    print(f"Saved dataset to: {sft_file}")

if __name__ == "__main__":
    main()
