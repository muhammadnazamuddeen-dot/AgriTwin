# AgriTwin AI — API Specification & Endpoint Documentation

**Version:** 1.0.0  
**Base URL:** `/api/v1`  
**Interactive Docs:** `http://localhost:8000/docs`  

---

## Endpoint Matrix

| Method | Endpoint | Description | Query / Body Params | Response Key |
|---|---|---|---|---|
| `GET` | `/health` | Core system health check | None | `{"status": "ok"}` |
| `GET` | `/ready` | System readiness check | None | `{"status": "ready"}` |
| `GET` | `/api/v1/health` | Prefixed health check | None | `{"status": "ok"}` |
| `GET` | `/api/v1/ready` | Prefixed readiness check | None | `{"status": "ready"}` |
| `GET` | `/api/v1/weather` | Live weather forecast & conditions | `farm_id`, `latitude`, `longitude`, `days` | `{"data": ...}` |
| `GET` | `/api/v1/soil` | Soil physics & pedotransfer hydraulics | `farm_id`, `latitude`, `longitude` | `{"soil_physics": ...}` |
| `GET` | `/api/v1/crops` | List all 13 supported crops | None | `{"crops": [...]}` |
| `GET` | `/api/v1/crops/recommendations` | Decoupled agronomic recommendations | `province`, `district`, `month`, `crop_id` | `{"ranked_crops": [...]}` |
| `GET` | `/api/v1/crops/{crop_id}` | Detailed crop profile & windows | `crop_id` (e.g. `WHEAT_001`) | `{"crop_id": "WHEAT_001", ...}` |
| `GET` | `/api/v1/prices/{crop_id}` | Current market rates & mandi info | `crop_id`, `district` | `{"current_market_rates": ...}` |
| `GET` | `/api/v1/prices/{crop_id}/history` | Historical price trends & series | `crop_id`, `district`, `days_back` | `{"history": [...]}` |
| `GET` | `/api/v1/prices/{crop_id}/forecast` | ML 7d, 14d, 30d price forecast | `crop_id`, `district`, `temp_c`, `humidity_pct` | `{"forecast_30d": ...}` |
| `GET` | `/api/v1/opportunities` | Composite market opportunity ranking | `province`, `district`, `month` | `{"opportunities": [...]}` |
| `GET` | `/api/v1/opportunities/{farm_id}`| Farm-specific market opportunity | `farm_id`, `month` | `{"opportunities": [...]}` |
| `POST` | `/api/v1/assistant` | Bilingual AI intelligence assistant | `{"farm_id": 1, "language": "ur"}` | `{"explanation": ...}` |
| `POST` | `/api/v1/ai/explain` | AI farm diagnostic explanation | `{"farm_id": 1, "language": "en"}` | `{"explanation": ...}` |

---

## Detailed Endpoint Examples

### 1. Crop Recommendations (`GET /api/v1/crops/recommendations`)

**Request:**
```http
GET /api/v1/crops/recommendations?province=Punjab&month=11 HTTP/1.1
Host: localhost:8000
```

**Response (200 OK):**
```json
{
  "status": "success",
  "province": "Punjab",
  "district": "Gujrat",
  "month": 11,
  "recommendations_count": 13,
  "ranked_crops": [
    {
      "crop_id": "WHEAT_001",
      "crop_name": "Wheat",
      "suitability_score": 96,
      "category": "Highly Suitable",
      "status": "PLANT NOW 🟢",
      "status_code": "PLANT",
      "days_until_window": 0,
      "days_remaining_in_window": 30,
      "days_since_window": 0,
      "todays_farm_action": [
        "Begin sowing Wheat immediately in the optimal planting window.",
        "Treat certified seeds with recommended fungicide/insecticide prior to sowing."
      ]
    }
  ]
}
```

### 2. Price Forecast (`GET /api/v1/prices/WHEAT_001/forecast`)

**Request:**
```http
GET /api/v1/prices/WHEAT_001/forecast?district=Gujrat HTTP/1.1
```

**Response (200 OK):**
```json
{
  "crop_id": "WHEAT_001",
  "crop_name": "Wheat",
  "district": "Gujrat",
  "current_price_100kg": 8250.0,
  "current_price_maund": 3300.0,
  "forecast_7d": 8350.0,
  "forecast_14d": 8500.0,
  "forecast_30d": 8800.0,
  "forecast_30d_maund": 3520.0,
  "price_change_30d_pct": 6.67,
  "direction": "bullish",
  "confidence": 0.74,
  "confidence_pct": 74.0
}
```

### 3. AI Explanation Assistant (`POST /api/v1/assistant`)

**Request:**
```json
{
  "farm_id": 1,
  "language": "ur"
}
```

**Response (200 OK):**
```json
{
  "summary": "Diagnostic & financial decision report for Wheat in Okara.",
  "health_status": "Optimal Condition",
  "risks": [
    "No Critical Environmental Risks Detected"
  ],
  "recommendations": [
    "گندم کے لیے نائٹروجن کی پہلی قسط کور آبپاشی (20-25 دن) پر دیں۔"
  ],
  "explanation": "آپ کے فارم (اوکاڑہ) کے موسمی اور زمینی تجزیے کے مطابق گندم کی کاشت کے لیے حالات انتہائی موزوں ہیں...",
  "confidence": 0.96
}
```
