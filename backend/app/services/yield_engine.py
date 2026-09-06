import joblib
import os
import pandas as pd
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "yield_model.joblib"

_model = None

def get_yield_prediction(district: str | None, crop_name: str | None, telemetry: dict | None = None) -> float | None:
    global _model
    if not crop_name:
        return None
    if _model is None:
        if not MODEL_PATH.exists():
            return None
        try:
            _model = joblib.load(MODEL_PATH)
        except Exception:
            return None
            
    # Normalize crop name (expects "Wheat", "Rice", "Maize", "Cotton", "Sugarcane")
    crop_mapping = {
        "wheat": "Wheat",
        "rice (basmati)": "Rice",
        "rice": "Rice",
        "maize": "Maize",
        "cotton": "Cotton",
        "sugarcane": "Sugarcane"
    }
    
    normalized_crop = crop_mapping.get(crop_name.lower(), crop_name.capitalize())
    district_str = (district or "Faisalabad").strip().capitalize()
    
    tel = telemetry or {}
    temp = tel.get("temperature_c", 30.0)
    hum = tel.get("humidity_pct", 55.0)
    soil_m = tel.get("soil_moisture", 0.22)
    rain = tel.get("rainfall_mm", 0.0)
    et0 = tel.get("et0_mm", 4.8)
    ndvi = tel.get("ndvi", 0.42)

    # Feature columns matching trained model pipeline
    row = {
        "district": district_str,
        "crop": normalized_crop,
        "temperature_c": temp if temp is not None else 30.0,
        "humidity_pct": hum if hum is not None else 55.0,
        "soil_moisture": soil_m if soil_m is not None else 0.22,
        "rainfall_mm": rain if rain is not None else 0.0,
        "et0_mm": et0 if et0 is not None else 4.8,
        "ndvi": ndvi if ndvi is not None else 0.42,
    }
    
    df = pd.DataFrame([row])
    try:
        pred = _model.predict(df)[0]
        return round(float(pred), 2)
    except Exception as e:
        # Fallback to categorical-only prediction if feature mismatch
        try:
            df_cat = pd.DataFrame([{"district": district_str, "crop": normalized_crop}])
            pred = _model.predict(df_cat)[0]
            return round(float(pred), 2)
        except Exception:
            print(f"Prediction error: {e}")
            return None

