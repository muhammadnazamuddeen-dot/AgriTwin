# AgriTwin AI — Hackathon Live Demo Script & Walkthrough

## Overview

This step-by-step guide is tailored for live judge demonstrations and technical presentations of AgriTwin AI.

---

## 1. Demo Credentials & Quick Start

- **Frontend URL:** `http://localhost:3000`
- **Backend API Docs:** `http://localhost:8000/docs`
- **Farmer Login:** `farmer@agritwin.pk` / `password123`
- **Extension Officer Login:** `officer@agritwin.pk` / `password123`

---

## 2. Walkthrough Narrative & Key Features

### Step 1: Login & Persona Authentication
1. Navigate to `http://localhost:3000`.
2. Login as `farmer@agritwin.pk`. Notice the secure session initialization.

### Step 2: Mission Control & Digital Twin Parcel Mapping
1. View Okara Green Fields parcel on the interactive map.
2. Highlight 5-Dimension Health Index, live agrometeorological telemetry, and satellite NDVI trend.

### Step 3: Warabandi Canal Irrigation & Diesel Savings Engine
1. Point to the live countdown timer for the upcoming canal turn (e.g. Thursday 02:00 AM).
2. Show the Diesel Tubewell Savings Calculator: Incoming rain forecast triggers an automatic "HOLD TUBEWELL" advisory, saving PKR 2,800+ in fuel costs.

### Step 4: Decoupled Crop Recommendation Engine
1. Navigate to Crop Recommendations.
2. Select Sowing Month (November) and Agricultural Zone (Punjab).
3. View ranked crop recommendations (Wheat #1 with 96% Agronomic Suitability, Status: `PLANT NOW 🟢`, days remaining: 30).
4. Emphasize that agronomic suitability operates independently of price volatility.

### Step 5: Market Intelligence & ML Price Forecasting
1. Open Price Intelligence for `WHEAT_001`.
2. Review current mandi rates (PKR 3,850/maund), 7d/30d/90d/YoY trends, and ML GradientBoosting 7d, 14d, 30d price forecasts (+6.7% bullish trend).
3. Point out the model evaluation comparison against naive baseline.

### Step 6: Opportunity Engine & Bilingual AI Explanation
1. Access Opportunity Engine (`/api/v1/opportunities`).
2. Show composite Opportunity Score (0-100) combining agronomics, market trends, and gross profit margins.
3. Trigger Bilingual AI Explanation (ENG / Urdu / Shahmukhi Punjabi) for personalized advisory.
