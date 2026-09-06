# AgriTwin AI — Automated Testing & Quality Assurance Guide

## Overview

AgriTwin AI maintains a rigorous test suite using `pytest` for the backend Python API and engines, and `jest` / `vitest` for the frontend Next.js application.

---

## 1. Running Backend Test Suite

To run all automated backend unit and integration tests:

```bash
# Execute full pytest suite
python -m pytest

# Run with detailed verbose output
python -m pytest -v

# Run specific test modules
python -m pytest backend/tests/test_final_api_checklist.py -v
python -m pytest backend/tests/test_decoupled_recommendation_and_prices.py -v
python -m pytest backend/tests/test_warabandi.py -v
```

---

## 2. Test Suite Structure

| Test File | Focus Area | Test Count | Result |
|---|---|---|---|
| `test_final_api_checklist.py` | 11 Versioned Required API Endpoints | 11 | 🟢 100% Passed |
| `test_decoupled_recommendation_and_prices.py` | Crop ID Standard & Decoupled Engines | 12 | 🟢 100% Passed |
| `test_agricore_and_crops.py` | Health Scoring & Crop Knowledge | 3 | 🟢 100% Passed |
| `test_ai_advisory.py` | RAG Advisory & LLM Explanation | 3 | 🟢 100% Passed |
| `test_farms_crud.py` | Farm Management CRUD & Geofencing | 1 | 🟢 100% Passed |
| `test_health_auth.py` | Auth, Cookies, Roles & Health Checks | 3 | 🟢 100% Passed |
| `test_intelligence_history.py` | Historical Telemetry & Analytics | 3 | 🟢 100% Passed |
| `test_pest_engine.py` | Pest Risk Engine & Thresholds | 5 | 🟢 100% Passed |
| `test_price_and_suitability_market.py` | Price Prediction & Mandi Rates | 8 | 🟢 100% Passed |
| `test_satellite_engine.py` | MODIS/Sentinel NDVI Imagery | 5 | 🟢 100% Passed |
| `test_soil_and_gdd.py` | Saxton-Rawls Soil & GDD Phenology | 6 | 🟢 100% Passed |
| `test_suitability_engine.py` | 9-Factor Suitability & Windows | 15 | 🟢 100% Passed |
| `test_warabandi.py` | Canal Turns & Tubewell Savings | 4 | 🟢 100% Passed |
| **Total Test Suite** | **Comprehensive System Testing** | **79** | **🟢 100% Passed** |

---

## 3. Key Edge Cases Verified

1. **Boundary Coordinate Values:** Coordinates outside Pakistan default gracefully to fallback agro-ecological zones.
2. **Missing Input Data:** Decoupled suitability scoring functions without requiring soil, weather, or price parameters.
3. **Leap Years & Year-Crossing Windows:** Wheat sowing windows spanning November -> January calculate `days_until_window` and `days_remaining_in_window` correctly.
4. **Empty Database Seeding:** Application automatically seeds initial demo users and farms on first startup.
