# AgriTwin AI — Data Sources & Telemetry Integration Specification

## Overview

AgriTwin AI combines multi-spectral satellite imagery, global numerical weather prediction (NWP), high-resolution soil pedology grids, and local wholesale market (mandi) rate feeds into a unified digital twin state space.

---

## 1. Primary Data Sources

| Telemetry Domain | Provider / Source | Resolution | Coverage | Query Method |
|---|---|---|---|---|
| **Agrometeorology** | Open-Meteo REST API | ~11 km | Global / Pakistan | Asynchronous HTTP REST |
| **Historical Climate Normals** | NASA POWER MERRA-2 | 0.5° × 0.625° | Global (30 years) | Asynchronous HTTP REST |
| **Air Quality & Smog Index** | Copernicus CAMS / Open-Meteo | 10 km | Punjab / Pakistan | Asynchronous HTTP REST |
| **Soil Texture & Physics** | ISRIC SoilGrids 2.0 | 250 m | Global Grid | REST API Query (Clay, Sand, Silt, SOC) |
| **Canal Water Commands** | Punjab Irrigation Department | Canal Command | LBDC, LCC, Upper Chenab, Thal, etc. | Internal Warabandi Knowledge Base |
| **Wholesale Mandi Rates** | AMIS Pakistan & PAR REST API | District Mandis | 12 Primary Punjab Mandis | Market Price Service Ingestion |
| **Orbital Vegetation Imagery** | NASA MODIS Terra (MOD13Q1) | 250 m | 16-Day Composites | MODIS ORNL REST API |

---

## 2. Soil Physics & Saxton-Rawls Pedotransfer Equations

Topsoil properties queried from ISRIC SoilGrids 2.0 (0-30 cm) are processed through Saxton and Rawls (2006) pedotransfer formulations:

1. **Permanent Wilting Point (\(\theta_{1500}\)):** Water content at 1500 kPa suction pressure.
2. **Field Capacity (\(\theta_{33}\)):** Water content at 33 kPa suction pressure.
3. **Available Water Capacity (AWC):** \(\text{AWC} = \theta_{33} - \theta_{1500}\) (expressed in mm water per meter of soil).
4. **Saturated Hydraulic Conductivity (\(K_{sat}\)):** Rate of water movement through saturated soil (mm/hr).

---

## 3. Fallback & Resilience Strategy

If external APIs (Open-Meteo, ISRIC SoilGrids, AMIS) encounter rate limits or network latency:

1. **Weather Fallback:** Uses regional seasonal normals for the farm's district (Okara, Faisalabad, Sahiwal, Multan, Gujrat, etc.).
2. **Soil Fallback:** Uses Punjab Alluvium Doab baseline parameters based on geographic coordinates:
   - **Central Punjab (Rechna / Bari Doab):** Sandy Loam (Sand 36%, Silt 46%, Clay 18%, OM 1.15%).
   - **Northern Punjab (Potohar Plateau):** Silt Loam (Sand 28%, Silt 44%, Clay 28%, OM 1.40%).
   - **Southern Punjab (Thal / Cholistan):** Loamy Sand (Sand 58%, Silt 28%, Clay 14%, OM 0.85%).
3. **Market Price Fallback:** Uses verified Punjab Agriculture Department benchmark mandi rates for September 2026.
