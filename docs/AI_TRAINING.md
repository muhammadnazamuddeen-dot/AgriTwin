# 🌾 AgriTwin AI — Complete AI Training & LLM Fine-Tuning Documentation

This document serves as the authoritative, end-to-end operational guide for **AgriTwin AI**, a Pakistan-focused precision agriculture platform.

---

## 1. System Architecture

AgriTwin AI enforces a strict separation of concerns between numerical modeling, decision logic, knowledge retrieval, and LLM explanation:

```
REAL AGRICULTURAL DATA (Open-Meteo, MODIS, SoilGrids, NASA POWER, AMIS)
        ↓
PostgreSQL / PostGIS Database & Live Telemetry Ingestion
        ↓
Feature Engineering & Aggregation
        ↓
Numerical ML Models (Yield Prediction, Health Index, Water Stress, Heat Stress, Pest Risk)
        ↓
Structured Agricultural Facts (JSON Data Payload)
        ↓
RAG Knowledge Base (Punjab Dept Advisories, Crop Calendars, Mandi Rates)
        ↓
Soup Fine-Tuned LLM (Qwen2.5-3B-Instruct + LoRA)
        ↓
Natural Language Explanation & Diagnostic Report
        ↓
Bilingual Output (English / Punjabi Shahmukhi)
```

> **CRITICAL RULE**: The LLM is **NEVER** used as a numerical yield engine. All numerical predictions (tonnes/ha, health scores 0–100, stress percentages) are calculated deterministically by standard ML regressors (`HistGradientBoostingRegressor` / `RandomForestRegressor`). The LLM is used **strictly** to explain structured facts to farmers in clear, natural language without hallucinating facts.

---

## 2. Real Data Sources

The platform incorporates trusted real-world datasets and live REST APIs:

1. **Open-Meteo REST API**: Real-time agrometeorology (2m Temperature, Relative Humidity %, Precipitation, 0–7cm Soil Moisture $m^3/m^3$, Surface Soil Temp, $ET_0$ Evapotranspiration).
2. **MODIS Terra Satellite Composite (MOD13Q1)**: 250m 16-day Vegetation Health Index (NDVI).
3. **NASA POWER MERRA-2 Reanalysis**: 30-year historical climate baselines for thermal & moisture anomaly calculation.
4. **SoilGrids (ISRIC)**: 250m global soil physics profile (pH, Organic Carbon, Clay %, Sand %, Bulk Density).
5. **Punjab Crop Reporting Service (CRS) 2024–2025**: Official district-level yield & production reports (160 records across 43 Punjab districts).
6. **Punjab AMIS (Agriculture Market Information Service)**: Wholesale mandi commodity rates (Wheat, Basmati Rice, Cotton, Sugarcane, Maize).
7. **Directorate General Pest Warning & Quality Control (Punjab)**: Fortnightly pest scouting reports and threshold alerts (Whitefly, Pink Bollworm, Stem Borer).

---

## 3. Dataset Schema (ChatJSONL / Instruction Format)

All fine-tuning examples follow the structured format:

```json
{
  "instruction": "Analyze the current status and diagnostic metrics for this Wheat field in Faisalabad.",
  "input": "District: Faisalabad, Punjab\nCrop: Wheat (Rabi Season)\nGrowth Stage: Flowering\nCurrent Temperature: 32.0°C\nRelative Humidity: 55.0%\n7-Day Rainfall: 0.0 mm\nRoot Soil Moisture (0-7cm): 0.18 m³/m³\nMODIS Satellite NDVI: 0.62\nML Health Score: 75/100\nML Water Stress: 42%\nML Heat Stress: 15%\nML Predicted Yield: 4.25 tonnes/ha\nMandi Rate: PKR 2,950 – 4,775 / 40kg",
  "output": "Field Diagnostic (Wheat in Faisalabad): Overall health score is 75/100 during Flowering stage. Temperature is 32.0°C and root soil moisture is 0.18 m³/m³. Field is experiencing elevated water stress (42%). Consider timely irrigation. MODIS satellite NDVI is 0.62. ML estimated yield is 4.25 tonnes/ha with mandi rate range of PKR 2,950 – 4,775 / 40kg."
}
```

---

## 4. Dataset Generation Pipeline (`ai/training/build_dataset.py`)

The dataset builder script generates instruction-input-output pairs across all 19 agronomic categories:

- **Command**:
  ```powershell
  python ai/training/build_dataset.py
  ```

- **Time-Aware Dataset Splits**:
  - **Train Set (2015–2023)**: `ai/training/train.jsonl`
  - **Validation Set (2024)**: `ai/training/validation.jsonl`
  - **Test Set (2025–2026)**: `ai/training/test.jsonl`

---

## 5. Data Quality & Hallucination Guard (`ai/training/validate_dataset.py`)

Every example is scanned prior to training:

- **Range Enforcement**: Temperature ($-10^\circ\text{C}$ to $60^\circ\text{C}$), Rainfall ($\ge 0\text{ mm}$), NDVI ($-1.0$ to $1.0$).
- **Structure Check**: Ensures non-empty `instruction`, `input`, `output`.
- **Hallucination Prevention**: Verifies that any numbers present in the output exist in the input facts.

- **Command**:
  ```powershell
  python ai/training/validate_dataset.py
  ```

---

## 6. Soup CLI Installation (`soup-cli`)

Install `soup-cli` into the Python environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install "soup-cli[train]" torch transformers peft datasets trl
```

Verify setup:
```powershell
python -m soup_cli env check
python -m soup_cli doctor
```

---

## 7. Soup Configuration (`ai/soup/soup.yaml`)

The training pipeline is configured in `ai/soup/soup.yaml`:

```yaml
project:
  name: agritwin-ai-copilot
  version: "1.0.0"

model:
  base_model: "Qwen/Qwen2.5-Coder-3B-Instruct"
  task: "sft"
  quantization: "4bit"
  torch_dtype: "bfloat16"

lora:
  r: 16
  alpha: 32
  target_modules: ["q_proj", "k_proj", "v_proj", "o_proj"]

dataset:
  train_file: "../training/train.jsonl"
  validation_file: "../training/validation.jsonl"
  test_file: "../training/test.jsonl"

training:
  epochs: 3
  learning_rate: 2.0e-4
  batch_size: 2
  gradient_accumulation_steps: 4
  max_seq_length: 2048
```

---

## 8. Executable Training Workflow Commands

Run the full pipeline using PowerShell:

```powershell
cd c:\Users\Nizam\Desktop\AgriTwin
.venv\Scripts\Activate.ps1
python ai/training/build_dataset.py
python ai/training/validate_dataset.py
python app/scripts/fine_tune_llm.py
python ai/soup/evaluate.py
```

---

## 9. Model Evaluation Benchmark Suite (`ai/soup/evaluate.py`)

Evaluates the fine-tuned adapter against 5 key dimensions:

1. **Factuality**: Verifies all supplied numerical facts are preserved.
2. **Hallucination Prevention**: Ensures missing facts (e.g. unmeasured diseases or exact uncalculated yields) are refused/omitted.
3. **Numerical Consistency**: Verifies values match input.
4. **Bilingual Quality**: Validates English & Punjabi (Shahmukhi) responses.
5. **Safety**: Enforces chemical pesticide application safety thresholds.

- **Command**:
  ```powershell
  python ai/soup/evaluate.py
  ```

---

## 10. Model Deployment & Artifacts

Model weights and LoRA adapters are saved in `backend/app/models/agritwin_llm_adapter/`:

- `adapter_config.json`: LoRA rank, alpha, base model metadata.
- `adapter_model.bin`: Fine-tuned adapter binary.
- `submission_manifest.json`: Verified submission artifact manifest.

---

## 11. Real-Time Inference Architecture

The LLM is **NOT** retrained when new weather arrives. Real-time inference follows this flow:

```
Open-Meteo (Live Weather) + MODIS (NDVI) + ML Models (Yield & Stress)
        ↓
Structured Facts Dict
        ↓
RAG Knowledge Retrieval
        ↓
Fine-Tuned LLM Explanation Engine (ai/inference/agritwin_llm.py)
        ↓
FastAPI Endpoint: POST /api/v1/ai/explain
```

---

## 12. Retraining Strategy

- **Numerical ML Models**: Retrained when new seasonal Punjab CRS actual production data or batch weather telemetry arrives (`python app/scripts/train_realtime_yield_model.py`).
- **LLM Fine-Tuned Adapter**: Retrained quarterly or when major agricultural advisories change.

---

## 13. RAG Strategy

The Retrieval-Augmented Generation (RAG) layer (`backend/app/services/rag_service.py`) dynamically injects:

- Crop calendars and growth stage duration thresholds.
- Official Punjab Pest Warning bulletins (Whitefly & Pink Bollworm spray intervals).
- AMIS Mandi commodity prices.
- Warabandi canal turn allocation guidance.

---

## 14. Known Limitations & Safeguards

- **Hardware Bounds**: Consumer GPUs (e.g. 4GB VRAM) use 4-bit NF4 layer streaming quantization (`quantization: 4bit`) with LoRA rank 16.
- **Strict Hallucination Policy**: If soil moisture or NDVI is unmeasured, the LLM is instructed to state that the value is unrecorded rather than inventing an estimate.
