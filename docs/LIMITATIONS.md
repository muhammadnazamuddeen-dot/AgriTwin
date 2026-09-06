# AgriTwin AI — Platform Limitations & Real-World Considerations

## Overview

AgriTwin AI is designed to deliver real-time agronomic intelligence and precision decision support. To ensure transparency, the following technical and operational limitations are documented.

---

## 1. Data Source Resolution & Latency Limitations

- **Satellite Imagery (MODIS):** MOD13Q1 offers 250m spatial resolution and 16-day composite updates. Cloud cover during monsoon months (July–August) may obstruct optical imagery, falling back to Sentinel-2 or synthetic SAR indices.
- **Soil Grids (ISRIC SoilGrids 2.0):** SoilGrids provides 250m gridded topsoil estimates. Localized field micro-variations (e.g. recent laser land leveling or heavy organic amendment) require direct soil sample overrides.
- **Mandi Price Feeds (AMIS / PAR):** AMIS mandi rates update daily during trading hours. Off-market or private farmgate deals may vary ±5% from wholesale mandi rates.

---

## 2. Model & Algorithmic Bounds

- **Price Prediction Horizon:** GradientBoosting price forecasts are most accurate for 7-day and 14-day horizons (MAE ~48–85 PKR/100kg). 30-day forecasts carry wider confidence intervals due to macro-economic inflation and policy shifts.
- **Canal Water Rights (Warabandi):** Schedules model official Punjab Irrigation Department rotational timetables. Unannounced canal breaches or main canal closures require manual schedule overrides.
- **Microclimate Extremes:** Sudden unseasonal localized hailstorms or severe frost events outside global NWP forecast grids may require immediate field inspection.

---

## 3. Recommended Operational Best Practices

1. **Soil Sampling Overrides:** Farmers are encouraged to input custom pH and soil test values when available to override satellite gridded baselines.
2. **Local Mandi Verification:** Always cross-reference 30-day market forecasts with local commission agents (Arhti) before executing bulk forward contracts.
