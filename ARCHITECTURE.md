# AgriTwin AI — System Architecture & Technical Specifications

## Architecture Overview

AgriTwin AI is built as a multi-layered, decoupled precision agriculture platform designed specifically for Pakistani agro-ecological zones.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FRONTEND (Next.js 16)                            │
│           Farmer Mission Control | Officer Dashboard | Punjabi & English     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTPS / JSON / Cookies
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                            FASTAPI BACKEND GATEWAY                          │
│        /api/v1 (Auth, Weather, Soil, Crops, Prices, Opportunities, AI)      │
└─────────┬────────────────────────────┬────────────────────────────┬─────────┘
          │                            │                            │
┌─────────▼─────────────┐   ┌──────────▼────────────┐   ┌───────────▼─────────┐
│ DECOUPLED ENGINES     │   │ ML PREDICTION ENGINE  │   │ RAG & SOUP LLM      │
│ • Crop Suitability    │   │ • GradientBoosting    │   │ • Bilingual RAG     │
│ • Soil Physics        │   │ • 7d/14d/30d Forecast │   │ • Explanations      │
│ • Warabandi Pumping   │   │ • Baseline Eval       │   │ • Localized Advice  │
│ • GDD Phenology       │   └───────────────────────┘   └─────────────────────┘
└─────────┬─────────────┘
          │
┌─────────▼───────────────────────────────────────────────────────────────────┐
│                          PERSISTENCE & TELEMETRY LAYER                      │
│     SQLite / PostGIS Database | Open-Meteo API | ISRIC SoilGrids | AMIS Rates│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core System Layers

### 1. API & Routing Layer (`backend/app/routers/`)
- Built on FastAPI with async task support.
- Fully versioned routes under `/api/v1`.
- OpenAPI / Swagger documentation exposed at `/docs`.

### 2. Decoupled Agronomic & Hydraulic Engines (`data-engine/` & `backend/app/core/engine/`)
- **Crop Suitability Engine:** Evaluates 9 factors (Season, Planting Window, Weather, Soil, Water, Disease, Yield, Market, Profit). Supports pure agronomic scoring without market prices.
- **Soil Physics Engine:** Uses Saxton-Rawls pedotransfer equations for field capacity, wilting point, and AWC.
- **Warabandi Canal Optimizer:** Calculates exact canal turn countdowns and tubewell rain-hold savings in PKR.
- **GDD Phenology Engine:** Tracks thermal units using crop-specific base temperatures.

### 3. Machine Learning Engine (`backend/app/services/price_prediction_engine.py`)
- Multi-target `GradientBoostingRegressor` trained on historical price trends, weather telemetry, market supply/demand, and seasonality.
- Outputs 7-day, 14-day, and 30-day forecasts, confidence scores (%), and trend directions (`bullish`, `bearish`, `stable`).
- Includes model evaluation against naive baseline (last observed price).

### 4. Bilingual RAG & Soup LLM Layer (`ai/` & `backend/app/services/rag_service.py`)
- Domain-specific agricultural vector index for Pakistan crops.
- Fine-tuned Soup LLM model (`agritwin_llm.py`) producing structured diagnostic explanations in English, Urdu, and Shahmukhi Punjabi.

---

## Permanent Crop ID Key System

The platform standardizes all crop intelligence on 13 permanent immutable keys:

| Permanent Crop ID | Crop Name | Primary Season | Water Req (mm) |
|---|---|---|---|
| `WHEAT_001` | Wheat | Rabi | 450 |
| `RICE_001` | Rice (Basmati) | Kharif | 1200 |
| `RICE_COARSE_001` | Rice (Coarse) | Kharif | 1100 |
| `COTTON_001` | Cotton | Kharif | 700 |
| `MAIZE_001` | Maize | Kharif / Spring | 500 |
| `SUGARCANE_001` | Sugarcane | Kharif (Annual) | 1500 |
| `POTATO_001` | Potato | Rabi | 450 |
| `CHICKPEA_001` | Gram (Chickpea) | Rabi | 250 |
| `CANOLA_001` | Canola / Mustard | Rabi | 300 |
| `SUNFLOWER_001` | Sunflower | Zaid / Spring | 400 |
| `BARLEY_001` | Barley | Rabi | 250 |
| `LENTIL_001` | Lentil | Rabi | 250 |
| `PEAS_001` | Peas | Rabi | 300 |
