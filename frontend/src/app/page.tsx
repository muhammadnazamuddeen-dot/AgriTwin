"use client";

import { useCallback, useEffect, useState } from "react";
import dynamic from "next/dynamic";
import {
  api,
  type Farm,
  type HealthScore,
  type Recommendation,
  type ForecastDay,
  type AuthUser,
} from "@/lib/api";
import Link from "next/link";
import HealthScoreCard from "@/components/HealthScoreCard";
import WeatherCard from "@/components/WeatherCard";
import NdviChart from "@/components/NdviChart";
import RecommendationPanel from "@/components/RecommendationPanel";
import ForecastChart from "@/components/ForecastChart";
import CropManager from "@/components/CropManager";
import FarmSelector from "@/components/FarmSelector";
import Icon from "@/components/Icon";
import ConfirmModal from "@/components/ConfirmModal";
import LazyCard from "@/components/LazyCard";
import SkeletonCard from "@/components/SkeletonCard";
import WarabandiAdvisor from "@/components/WarabandiAdvisor";
import SoilPhysicsCard from "@/components/SoilPhysicsCard";
import CropSuitabilityCard from "@/components/CropSuitabilityCard";
import PestRiskCard from "@/components/PestRiskCard";
import AiAssistantDrawer from "@/components/AiAssistantDrawer";
import KpiMetricsBar from "@/components/KpiMetricsBar";
import RecommendedCropCard from "@/components/RecommendedCropCard";
import MarketPriceCard from "@/components/MarketPriceCard";
import UpcomingAlertsCard from "@/components/UpcomingAlertsCard";
import { useLanguage } from "@/components/LanguageProvider";
import { useAuth } from "@/components/AuthProvider";


// Dynamic import prevents SSR issues with Leaflet
const FarmMap = dynamic(() => import("@/components/FarmMap"), { ssr: false });

const PUNJAB_CANALS = [
  "Lower Bari Doab Canal (LBDC)",
  "Upper Chenab Canal",
  "Muzaffargarh Canal",
  "Sidhnai Canal",
  "Thal Canal",
  "Fordwah Canal",
  "Dera Ghazi Khan Canal",
  "Pakpattan Canal",
  "Upper Jhelum Canal",
  "Central Bari Doab Canal",
];

const WEEKDAYS = [
  { en: "Monday", ur: "پیر" },
  { en: "Tuesday", ur: "منگل" },
  { en: "Wednesday", ur: "بدھ" },
  { en: "Thursday", ur: "جمعرات" },
  { en: "Friday", ur: "جمعہ" },
  { en: "Saturday", ur: "ہفتہ" },
  { en: "Sunday", ur: "اتوار" },
];

const PUNJAB_CANAL_DISTRICT_MAP: Record<string, string> = {
  // Bari Doab
  okara: "Lower Bari Doab Canal (LBDC)",
  sahiwal: "Lower Bari Doab Canal (LBDC)",
  khanewal: "Lower Bari Doab Canal (LBDC)",
  pakpattan: "Lower Bari Doab Canal (LBDC)",
  lahore: "Central Bari Doab Canal (CBDC)",
  kasur: "Central Bari Doab Canal (CBDC)",
  vehari: "Fordwah Canal",
  bahawalnagar: "Fordwah Canal",

  // Rechna Doab
  faisalabad: "Lower Chenab Canal (LCC)",
  "toba tek singh": "Lower Chenab Canal (LCC)",
  jhang: "Lower Chenab Canal (LCC)",
  chiniot: "Lower Chenab Canal (LCC)",
  "nankana sahib": "Lower Chenab Canal (LCC)",
  hafizabad: "Lower Chenab Canal (LCC)",
  gujranwala: "Upper Chenab Canal",
  sialkot: "Upper Chenab Canal",
  sheikhupura: "Upper Chenab Canal",
  narowal: "Upper Chenab Canal",

  // Chaj Doab
  sargodha: "Lower Jhelum Canal",
  "mandi bahauddin": "Lower Jhelum Canal",
  gujrat: "Upper Jhelum Canal",
  jhelum: "Upper Jhelum Canal",
  rawalpindi: "Upper Jhelum Canal",
  chakwal: "Upper Jhelum Canal",
  attock: "Upper Jhelum Canal",

  // Thal
  bhakkar: "Thal Canal",
  layyah: "Thal Canal",
  khushab: "Thal Canal",
  mianwali: "Thal Canal",

  // Indus & Lower Punjab
  multan: "Sidhnai Canal",
  lodhran: "Sidhnai Canal",
  muzaffargarh: "Muzaffargarh Canal",
  "kot addu": "Muzaffargarh Canal",
  "dera ghazi khan": "Dera Ghazi Khan Canal",
  "dg khan": "Dera Ghazi Khan Canal",
  rajanpur: "Dera Ghazi Khan Canal",
  bahawalpur: "Panjnad & Abbasia Canals",
  "rahim yar khan": "Panjnad & Abbasia Canals",
};

function inferCanalFromLocation(
  district?: string,
  lat?: number,
  lng?: number
): string {
  if (district) {
    const clean = district.trim().toLowerCase();
    for (const [key, canal] of Object.entries(PUNJAB_CANAL_DISTRICT_MAP)) {
      if (clean.includes(key) || key.includes(clean)) {
        return canal;
      }
    }
  }

  // Coordinate geographic zones if district is not yet resolved
  if (lat !== undefined && lng !== undefined) {
    if (lat >= 30.3 && lat <= 31.3 && lng >= 72.8 && lng <= 74.0) return "Lower Bari Doab Canal (LBDC)";
    if (lat >= 30.8 && lat <= 31.9 && lng >= 72.3 && lng <= 73.6) return "Lower Chenab Canal (LCC)";
    if (lat >= 31.8 && lat <= 32.7 && lng >= 73.8 && lng <= 75.0) return "Upper Chenab Canal";
    if (lat >= 31.0 && lat <= 31.8 && lng >= 74.0 && lng <= 74.6) return "Central Bari Doab Canal (CBDC)";
    if (lat >= 29.8 && lat <= 30.6 && lng >= 71.0 && lng <= 72.2) return "Sidhnai Canal";
    if (lat >= 29.8 && lat <= 30.9 && lng >= 70.7 && lng <= 71.4) return "Muzaffargarh Canal";
    if (lat >= 29.5 && lat <= 30.9 && lng >= 70.0 && lng <= 70.8) return "Dera Ghazi Khan Canal";
    if (lat >= 30.7 && lat <= 32.2 && lng >= 70.8 && lng <= 71.9) return "Thal Canal";
    if (lat >= 29.5 && lat <= 30.5 && lng >= 72.5 && lng <= 74.0) return "Fordwah Canal";
    if (lat >= 28.0 && lat <= 29.8 && lng >= 69.8 && lng <= 72.0) return "Panjnad & Abbasia Canals";
    if (lat >= 31.7 && lat <= 32.7 && lng >= 72.2 && lng <= 73.5) return "Lower Jhelum Canal";
    if (lat >= 32.4 && lat <= 33.5 && lng >= 73.4 && lng <= 74.5) return "Upper Jhelum Canal";
  }

  return "Lower Bari Doab Canal (LBDC)";
}

export default function DashboardPage() {
  const { t, isUrdu } = useLanguage();
  const { user } = useAuth();
  const [farms, setFarms] = useState<Farm[]>([]);
  const [selectedFarm, setSelectedFarm] = useState<Farm | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Weather
  const [weatherData, setWeatherData] = useState<Record<string, unknown> | null>(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherError, setWeatherError] = useState<string | null>(null);

  // Forecast chart
  const [forecastData, setForecastData] = useState<ForecastDay[]>([]);
  const [forecastLoading, setForecastLoading] = useState(false);

  // NDVI time series (real MODIS satellite data)
  const [ndviSeries, setNdviSeries] = useState<{ date: string; ndvi: number }[]>([]);
  const [ndviChange, setNdviChange] = useState<number | null>(null);
  const [ndviSource, setNdviSource] = useState<string | null>(null);
  const [ndviLoading, setNdviLoading] = useState(false);

  // Health score (from AgriCore)
  const [health, setHealth] = useState<HealthScore | null>(null);
  const [healthLoading, setHealthLoading] = useState(false);

  // Crop suitability data (for dynamic top recommended crop)
  const [suitabilityData, setSuitabilityData] = useState<any | null>(null);

  // ML Yield prediction from trained model
  const [yieldPrediction, setYieldPrediction] = useState<number | null>(null);

  // Recommendation (from AgriCore)
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [recLoading, setRecLoading] = useState(false);

  // Farm creation state
  const [newFarmName, setNewFarmName] = useState("");
  const [newFarmDistrict, setNewFarmDistrict] = useState("");
  const [newCanalName, setNewCanalName] = useState("Lower Bari Doab Canal (LBDC)");
  const [newCanalTurnDay, setNewCanalTurnDay] = useState("Thursday");
  const [newCanalTurnTime, setNewCanalTurnTime] = useState("02:00");
  const [newCanalTurnDuration, setNewCanalTurnDuration] = useState(4.0);
  const [newTubewellPowerSource, setNewTubewellPowerSource] = useState("diesel");
  const [newTubewellHourlyCost, setNewTubewellHourlyCost] = useState(1400.0);
  const [showTurnConfig, setShowTurnConfig] = useState(false);
  const [canalAutoDetected, setCanalAutoDetected] = useState(false);
  const [drawnPolygon, setDrawnPolygon] = useState<string | null>(null);
  const [drawnCentroid, setDrawnCentroid] = useState<[number, number] | null>(null);
  const [drawnArea, setDrawnArea] = useState<number | null>(null);
  const [districtAutoDetected, setDistrictAutoDetected] = useState(false);
  const [drawReset, setDrawReset] = useState(0);

  // Farm deletion modal state
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const confirmDeleteFarm = async () => {
    if (!selectedFarm) return;
    setDeleting(true);
    try {
      await api.deleteFarm(selectedFarm.id);
      const remaining = farms.filter((f) => f.id !== selectedFarm.id);
      setFarms(remaining);
      setSelectedFarm(remaining.length > 0 ? remaining[0] : null);
      setShowDeleteModal(false);
    } catch {
      alert("Failed to delete farm. Please try again.");
    } finally {
      setDeleting(false);
    }
  };

  // ── Load farms on mount ───────────────────────────────────────────────────
  useEffect(() => {
    api.listFarms().then((list) => {
      setFarms(list);
      // Auto-select first farm if available for instant data
      if (list.length > 0 && !selectedFarm) {
        setSelectedFarm(list[0]);
      }
    }).catch(() => setFarms([]));
  }, []);

  // ── Fetch all farm data when a farm is selected ─────────────────────────
  useEffect(() => {
    if (!selectedFarm) {
      setWeatherData(null);
      setForecastData([]);
      setHealth(null);
      setRecommendation(null);
      setNdviSeries([]);
      setNdviChange(null);
      setNdviSource(null);
      setYieldPrediction(null);
      return;
    }

    const farmId = selectedFarm.id;

    // Current weather
    setWeatherLoading(true);
    setWeatherError(null);
    api
      .getCurrentWeather(farmId)
      .then((res) => setWeatherData(res.data as Record<string, unknown>))
      .catch((err) => setWeatherError(err.message))
      .finally(() => setWeatherLoading(false));

    // 7-day forecast for chart
    setForecastLoading(true);
    api
      .getForecastChart(farmId)
      .then((res) => setForecastData(res.forecast))
      .catch(() => setForecastData([]))
      .finally(() => setForecastLoading(false));

    // AgriCore health score
    setHealthLoading(true);
    api
      .getHealthScore(farmId)
      .then((res) => setHealth(res.health))
      .catch(() => {
        // Fallback default health score if network fails
        setHealth({
          overall: 65,
          vegetation: 60,
          water: 55,
          weather: 75,
          pest_risk: 70,
          climate: 75,
        });
      })
      .finally(() => setHealthLoading(false));

    // Real NDVI time series (MODIS)
    setNdviLoading(true);
    api
      .getNdviSeries(farmId)
      .then((res) => {
        setNdviSeries(res.series ?? []);
        setNdviChange(res.ndvi_change);
        setNdviSource(res.source);
      })
      .catch(() => {
        setNdviSeries([]);
        setNdviChange(null);
        setNdviSource(null);
      })
      .finally(() => setNdviLoading(false));

    // Crop suitability for dynamic top crop recommendation card
    api
      .getCropSuitability(farmId)
      .then((res) => setSuitabilityData(res))
      .catch(() => setSuitabilityData(null));

    // Farm Intelligence for ML Yield Prediction
    api
      .getFarmIntelligence(farmId)
      .then((intel) => {
        if (intel?.farm?.yield_prediction_t_ha != null) {
          setYieldPrediction(intel.farm.yield_prediction_t_ha);
        }
      })
      .catch(() => {});

    // Pre-fetch Warabandi canal schedule & Soil physics immediately in background
    api.getWarabandiAdvice(farmId).catch(() => {});
    api.getSoilPhysics(farmId).catch(() => {});
  }, [selectedFarm]);

  // ── Generate recommendation on demand ────────────────────────────────────
  const handleGetRecommendation = useCallback(async () => {
    if (!selectedFarm) return;
    setRecLoading(true);
    try {
      const rec = await api.getRecommendation(selectedFarm.id);
      setRecommendation(rec);
    } catch {
      setRecommendation(null);
    } finally {
      setRecLoading(false);
    }
  }, [selectedFarm]);

  // ── Handle polygon drawn on map ──────────────────────────────────────────
  const handlePolygonDrawn = useCallback(
    (
      geojson: string,
      centroid: [number, number],
      areaAcres: number,
      suggestedDistrict?: string
    ) => {
      setDrawnPolygon(geojson);
      setDrawnCentroid(centroid);
      setDrawnArea(areaAcres);
      if (suggestedDistrict) {
        setNewFarmDistrict(suggestedDistrict);
        setDistrictAutoDetected(true);
      } else {
        setDistrictAutoDetected(false);
      }
      const detectedCanal = inferCanalFromLocation(suggestedDistrict, centroid[0], centroid[1]);
      setNewCanalName(detectedCanal);
      setCanalAutoDetected(true);
      setShowCreateForm(true);
    },
    []
  );

  // ── Handle live location detected on map ──────────────────────────────────
  const handleLocationFound = useCallback(
    (lat: number, lng: number, district?: string) => {
      setDrawnCentroid([lat, lng]);
      if (district) {
        setNewFarmDistrict(district);
        setDistrictAutoDetected(true);
      }
      const detectedCanal = inferCanalFromLocation(district, lat, lng);
      setNewCanalName(detectedCanal);
      setCanalAutoDetected(true);
    },
    []
  );

  // ── Create farm ─────────────────────────────────────────────────────────
  const handleCreateFarm = async () => {
    if (!newFarmName.trim()) return;
    try {
      const farm = await api.createFarm({
        name: newFarmName,
        geometry_geojson: drawnPolygon ?? undefined,
        area_acres: drawnArea ?? undefined,
        district: newFarmDistrict || undefined,
        province: "Punjab",
        latitude: drawnCentroid?.[0],
        longitude: drawnCentroid?.[1],
        canal_name: newCanalName,
        canal_turn_day: newCanalTurnDay,
        canal_turn_time: newCanalTurnTime,
        canal_turn_duration_hours: newCanalTurnDuration,
        tubewell_power_source: newTubewellPowerSource,
        tubewell_hourly_cost_pkr: newTubewellHourlyCost,
      });
      setFarms((prev) => [...prev, farm]);
      setSelectedFarm(farm);
      setShowCreateForm(false);
      setNewFarmName("");
      setShowTurnConfig(false);
      setDrawnPolygon(null);
      setDrawnCentroid(null);
      setDrawnArea(null);
      setDistrictAutoDetected(false);
      setDrawReset((n) => n + 1);
    } catch (err) {
      alert(`Failed to create farm: ${err}`);
    }
  };

  const isOfficer = user?.role === "extension_officer";

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
      {/* ── Extension Officer Regional Surveillance Mode Banner ───────────── */}
      {isOfficer && (
        <div className="mb-6 rounded-xl border border-sky-500/20 bg-sky-500/5 p-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-500/10 text-sky-600 dark:text-sky-400 shrink-0">
                <Icon name="activity" size={20} />
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="text-sm font-semibold text-ink">
                    {isUrdu ? "ڈائریکٹوریٹ جنرل آف ایگریکلچر ایکسٹینشن پنجاب" : "Directorate General of Agriculture Extension Punjab"}
                  </h2>
                  <span className="rounded-md bg-sky-500/10 px-2 py-0.5 text-[10px] font-medium text-sky-600 dark:text-sky-400 uppercase tracking-wide">
                    {isUrdu ? "نگرانی موڈ" : "Supervisory Mode"}
                  </span>
                </div>
                <p className="mt-0.5 text-xs text-mist">
                  {isUrdu
                    ? "پنجاب دے تمام ضلعی ڈیجیٹل ٹوئن فارمز دی علاقائی نگرانی و تجزیہ فعال ہے۔"
                    : "Regional surveillance active across all Punjab district farms · Multi-farm agronomic telemetry"}
                </p>
              </div>
            </div>
            <span className="rounded-lg border border-sky-500/20 bg-sky-500/10 px-3 py-1.5 text-xs font-medium text-sky-600 dark:text-sky-400 self-start sm:self-auto">
              {farms.length} {isUrdu ? "ضلعی فارمز زیرِ نگرانی" : "District Farms Supervised"}
            </span>
          </div>
        </div>
      )}

      {/* ── Top Command Bar & Farm Selector ─────────────────────────────── */}
      <div className="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <FarmSelector farms={farms} selected={selectedFarm} onSelect={setSelectedFarm} />
        </div>

        {selectedFarm && (
          <div className="flex items-center gap-2">
            <Link
              href={`/farms/${selectedFarm.id}`}
              className="flex items-center gap-1.5 rounded-xl border border-edge bg-panel px-3 py-2 text-xs font-semibold text-ink transition-colors hover:bg-brand/10 hover:text-brand"
            >
              <Icon name="activity" size={14} className="text-brand" />
              <span>{t("viewAnalytics", "Full Analytics")}</span>
            </Link>

            <Link
              href={`/farms/${selectedFarm.id}/history`}
              className="flex items-center gap-1.5 rounded-xl border border-edge bg-panel px-3 py-2 text-xs font-semibold text-mist transition-colors hover:bg-ink/[0.05] hover:text-ink"
            >
              <Icon name="clock" size={14} className="text-dim" />
              <span>{t("viewHistory", "History Log")}</span>
            </Link>

            {!isOfficer && (
              <button
                onClick={() => setShowDeleteModal(true)}
                disabled={deleting}
                className="flex items-center gap-1.5 rounded-xl border border-rose-500/20 bg-rose-500/10 px-3 py-2 text-xs font-semibold text-rose-500 transition-colors hover:bg-rose-500/20 disabled:opacity-50"
              >
                <Icon name="trash" size={14} />
                <span>{t("deleteShort", "Delete")}</span>
              </button>
            )}
          </div>
        )}
      </div>

      {/* ── 1. Top KPI Row (4 Cards) ─────────────────────────────────────── */}
      <LazyCard delayMs={20}>
        <KpiMetricsBar
          healthScore={health?.overall ?? 78}
          weatherTemp={weatherData ? Math.round((((weatherData.current || weatherData) as Record<string, number>)?.temperature_2m ?? 32)) : 32}
          weatherStatus="Partly Cloudy"
          marketTrendPct={8.4}
          yieldPredictionTHa={yieldPrediction ?? 4.25}
          farmAcres={selectedFarm?.area_acres ?? 10.24}
          cropName={suitabilityData?.ranked_crops?.[0]?.crop_name ?? "Wheat"}
        />
      </LazyCard>

      {/* ── 2. Middle Main Dashboard Grid (Screenshot Layout) ─────────────── */}
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left/Center Box: Your Farm Map (7 Cols) */}
        <div className="lg:col-span-7 flex flex-col glass-panel p-0 overflow-hidden min-h-[460px] relative">
          <div className="flex items-center justify-between p-4 border-b border-edge bg-panel/50 backdrop-blur-sm z-10">
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-brand/15 text-brand">
                <Icon name="mapPin" size={14} />
              </span>
              <h3 className="text-sm font-bold text-ink">
                {isUrdu ? "تہاڈا فارم" : "Your Farm"}
              </h3>
            </div>
            {selectedFarm?.area_acres != null && (
              <span className="rounded-full bg-emerald-500/15 border border-emerald-500/30 px-3 py-1 text-xs font-bold text-emerald-500">
                {selectedFarm.area_acres.toLocaleString()} {t("acres", "Acres")}
              </span>
            )}
          </div>

          <div className="flex-1 w-full h-full min-h-[400px] relative">
            <FarmMap
              center={
                selectedFarm?.latitude && selectedFarm?.longitude
                  ? [selectedFarm.latitude, selectedFarm.longitude]
                  : undefined
              }
              zoom={16}
              polygonGeoJson={selectedFarm?.geometry_geojson}
              farmLabel={selectedFarm?.name ?? "10.24 Acres"}
              resetSignal={drawReset}
              onPolygonDrawn={handlePolygonDrawn}
              onLocationFound={handleLocationFound}
            />
          </div>
        </div>

        {/* Middle Box: Recommended Crop Card (5 Cols) */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          <div id="crop-advisor" className="flex-1">
            <RecommendedCropCard
              cropName={suitabilityData?.ranked_crops?.[0]?.crop_name ?? "Maize"}
              score={suitabilityData?.ranked_crops?.[0]?.suitability_score ?? 87}
              reasons={suitabilityData?.ranked_crops?.[0]?.key_strengths}
              onViewAnalysis={() => {
                const el = document.getElementById("crop-suitability-section");
                el?.scrollIntoView({ behavior: "smooth" });
              }}
            />
          </div>
        </div>
      </div>

      {/* ── 3. Market Price & Upcoming Alerts Grid Row ────────────────────── */}
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div id="market-trends">
          <MarketPriceCard cropName={suitabilityData?.ranked_crops?.[0]?.crop_name ?? "Maize"} />
        </div>
        <div id="alerts">
          <UpcomingAlertsCard />
        </div>
      </div>

      {/* ── 4. Detailed Field Health Index & Crop Manager ──────────────────── */}
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <HealthScoreCard
            overall={health?.overall ?? 65}
            vegetation={health?.vegetation ?? 60}
            water={health?.water ?? 55}
            weather={health?.weather ?? 75}
            pestRisk={health?.pest_risk ?? 70}
            climate={health?.climate ?? 75}
            loading={healthLoading}
          />
        </div>

        <div>
          {selectedFarm && (
            <CropManager
              farmId={selectedFarm.id}
              onCropAdded={() => {
                if (!selectedFarm) return;
                setHealthLoading(true);
                api
                  .getHealthScore(selectedFarm.id)
                  .then((res) => setHealth(res.health))
                  .catch(() => { })
                  .finally(() => setHealthLoading(false));
              }}
            />
          )}
        </div>
      </div>

          {/* Farm Creation Form (Moved to fixed modal) */}
          {showCreateForm && (
            <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 p-4">
              <div className="relative w-full max-w-md max-h-[90vh] overflow-y-auto rounded-xl border border-edge bg-panel p-6 shadow-xl">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand/10 text-brand">
                      <Icon name="pencil" size={14} />
                    </span>
                    <h3 className="text-base font-semibold text-ink">{t("registerFarm", "Register Farm Boundary")}</h3>
                  </div>
                  <button
                    onClick={() => {
                      setShowCreateForm(false);
                      setDrawnPolygon(null);
                      setDrawnCentroid(null);
                      setDrawnArea(null);
                      setDistrictAutoDetected(false);
                      setDrawReset((n) => n + 1);
                    }}
                    className="flex h-7 w-7 items-center justify-center rounded-lg text-dim hover:bg-ink/[0.06] hover:text-ink transition-colors"
                  >
                    <Icon name="x" size={14} />
                  </button>
                </div>

                <div className="space-y-4 text-xs">
                  <div>
                    <label className="mb-1 block font-semibold text-mist uppercase tracking-wider text-[10px]">
                      {t("farmName", "Farm Name")} *
                    </label>
                    <input
                      value={newFarmName}
                      onChange={(e) => setNewFarmName(e.target.value)}
                      placeholder={t("farmNamePlaceholder", "e.g. Chak 45 South Field")}
                      className="input-theme"
                      autoFocus
                    />
                  </div>

                  <div>
                    <label className="mb-1 block font-semibold text-mist uppercase tracking-wider text-[10px]">
                      {t("district", "District (Punjab)")}
                    </label>
                    <input
                      value={newFarmDistrict}
                      onChange={(e) => {
                        const val = e.target.value;
                        setNewFarmDistrict(val);
                        setDistrictAutoDetected(false);
                        const inferred = inferCanalFromLocation(val, drawnCentroid?.[0], drawnCentroid?.[1]);
                        setNewCanalName(inferred);
                        setCanalAutoDetected(true);
                      }}
                      placeholder={t("districtPlaceholder", "e.g. Faisalabad, Multan, Bahawalpur")}
                      className="input-theme"
                    />
                    {districtAutoDetected && (
                      <p className="mt-1 flex items-center gap-1 text-[10px] text-brand">
                        <Icon name="spark" size={10} />
                        {t("autoDetected", "Auto-detected from boundary centroid")}
                      </p>
                    )}
                  </div>

                  {drawnCentroid && (
                    <div className="rounded-xl border border-ink/8 bg-ink/[0.02] p-3 text-mist font-mono text-[11px]">
                      <p className="flex items-center gap-2">
                        <Icon name="mapPin" size={14} className="text-brand shrink-0" />
                        {drawnCentroid[0].toFixed(5)}°N, {drawnCentroid[1].toFixed(5)}°E
                      </p>
                      {drawnArea !== null && (
                        <p className="mt-1.5 text-ink font-semibold flex items-center gap-2">
                          <Icon name="activity" size={14} className="text-emerald-400 shrink-0" />
                          {t("fieldBoundary", "Boundary")}: {drawnArea.toLocaleString()} {t("acres", "acres")} ({(drawnArea * 0.404686).toFixed(1)} {t("hectares", "ha")})
                        </p>
                      )}
                    </div>
                  )}

                  {/* ── Warabandi Canal & Tubewell Setup Accordion ────────────── */}
                  <div className="rounded-xl border border-ink/10 bg-ink/[0.03] p-3 transition-colors">
                    <button
                      type="button"
                      onClick={() => setShowTurnConfig(!showTurnConfig)}
                      className="flex w-full items-center justify-between text-left font-semibold text-ink"
                    >
                      <span className="flex items-center gap-1.5 text-xs text-ink font-semibold">
                        <span className="flex h-5 w-5 items-center justify-center rounded-md bg-brand/15 text-brand">
                          <Icon name="droplet" size={12} />
                        </span>
                        <span>{isUrdu ? "وارابندی تے ٹیوب ویل سیٹنگز (اختیاری)" : "Canal Turn & Tubewell (Optional)"}</span>
                      </span>
                      <span className="text-[10px] text-brand hover:underline font-medium">
                        {showTurnConfig ? (isUrdu ? "بند کرو" : "Hide") : (isUrdu ? "سیٹ کرو" : "Configure")}
                      </span>
                    </button>

                    {showTurnConfig && (
                      <div className="mt-3 space-y-3 border-t border-ink/8 pt-3 animate-fade-in">
                        <div>
                          <label className="mb-1 block font-semibold text-mist uppercase tracking-wider text-[10px]">
                            {isUrdu ? "نہری ڈسٹری بیوٹری" : "Canal / Distributary"}
                          </label>
                          <select
                            value={newCanalName}
                            onChange={(e) => {
                              setNewCanalName(e.target.value);
                              setCanalAutoDetected(false);
                            }}
                            className="input-theme w-full"
                          >
                            {PUNJAB_CANALS.map((c) => (
                              <option key={c} value={c} className="bg-panel text-ink">
                                {c}
                              </option>
                            ))}
                          </select>
                          {canalAutoDetected && (
                            <p className="mt-1 flex items-center gap-1 text-[10px] text-brand">
                              <Icon name="spark" size={10} />
                              <span>
                                {isUrdu
                                  ? `لوکیشن توں خودکار منتخب نہر: ${newCanalName}`
                                  : `Auto-selected for ${newFarmDistrict || "field location"}`}
                              </span>
                            </p>
                          )}
                        </div>

                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="mb-1 block font-semibold text-mist uppercase tracking-wider text-[10px]">
                              {isUrdu ? "واری دا دن" : "Canal Turn Day"}
                            </label>
                            <select
                              value={newCanalTurnDay}
                              onChange={(e) => setNewCanalTurnDay(e.target.value)}
                              className="input-theme w-full"
                            >
                              {WEEKDAYS.map((d) => (
                                <option key={d.en} value={d.en} className="bg-panel text-ink">
                                  {isUrdu ? `${d.ur} (${d.en})` : d.en}
                                </option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label className="mb-1 block font-semibold text-mist uppercase tracking-wider text-[10px]">
                              {isUrdu ? "واری دا وقت" : "Start Time"}
                            </label>
                            <input
                              type="time"
                              value={newCanalTurnTime}
                              onChange={(e) => setNewCanalTurnTime(e.target.value)}
                              className="input-theme w-full"
                            />
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="mb-1 block font-semibold text-mist uppercase tracking-wider text-[10px]">
                              {isUrdu ? "واری (گھنٹے)" : "Duration (Hours)"}
                            </label>
                            <input
                              type="number"
                              step="0.5"
                              min="1"
                              max="24"
                              value={newCanalTurnDuration}
                              onChange={(e) => setNewCanalTurnDuration(parseFloat(e.target.value) || 4.0)}
                              className="input-theme w-full"
                            />
                          </div>
                          <div>
                            <label className="mb-1 block font-semibold text-mist uppercase tracking-wider text-[10px]">
                              {isUrdu ? "ٹیوب ویل ایندھن" : "Tubewell Power"}
                            </label>
                            <select
                              value={newTubewellPowerSource}
                              onChange={(e) => {
                                setNewTubewellPowerSource(e.target.value);
                                setNewTubewellHourlyCost(
                                  e.target.value === "diesel" ? 1400.0 : e.target.value === "grid" ? 650.0 : 0.0
                                );
                              }}
                              className="input-theme w-full capitalize"
                            >
                              <option value="diesel" className="bg-panel text-ink">
                                {isUrdu ? "ڈیزل جنریٹر" : "Diesel"}
                              </option>
                              <option value="grid" className="bg-panel text-ink">
                                {isUrdu ? "بجلی گرڈ" : "Electric Grid"}
                              </option>
                              <option value="solar" className="bg-panel text-ink">
                                {isUrdu ? "سولر پینل" : "Solar"}
                              </option>
                            </select>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-3 pt-3 mt-4 border-t border-edge">
                    <button
                      onClick={handleCreateFarm}
                      disabled={!newFarmName.trim()}
                      className="flex-1 rounded-lg bg-brand px-4 py-2.5 text-sm font-medium text-abyss transition-colors hover:bg-brand-dark disabled:opacity-40"
                    >
                      {t("saveFarm", "Save Farm")}
                    </button>
                    <button
                      onClick={() => {
                        setShowCreateForm(false);
                        setDrawnPolygon(null);
                        setDrawnCentroid(null);
                        setDrawnArea(null);
                        setDistrictAutoDetected(false);
                        setCanalAutoDetected(false);
                        setDrawReset((n) => n + 1);
                      }}
                      className="rounded-lg border border-edge px-4 py-2.5 text-sm font-medium text-mist hover:bg-ink/[0.04] hover:text-ink transition-colors"
                    >
                      {t("cancel", "Cancel")}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

      {/* ── Warabandi Canal Water, Soil Hydraulics & Crop Intelligence ───── */}
      {selectedFarm && (
        <>
          <LazyCard delayMs={75} className="mt-6">
            <div id="settings">
              <WarabandiAdvisor farmId={selectedFarm.id} />
            </div>
          </LazyCard>
          <LazyCard delayMs={85} className="mt-6">
            <SoilPhysicsCard farmId={selectedFarm.id} />
          </LazyCard>
          <LazyCard delayMs={90} className="mt-6">
            <div id="crop-suitability-section" className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <CropSuitabilityCard farmId={selectedFarm.id} />
              <PestRiskCard farmId={selectedFarm.id} />
            </div>
          </LazyCard>
        </>
      )}

      {/* ── Agrometeorology & 7-Day Forecast ────────────────────── */}
      <LazyCard delayMs={100} className="mt-6">
        <div id="weather" className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <WeatherCard data={weatherData} loading={weatherLoading} error={weatherError} />
          <ForecastChart data={forecastData} loading={forecastLoading} />
        </div>
      </LazyCard>

      {/* ── MODIS Satellite NDVI History ──────────────────────────────── */}
      <LazyCard delayMs={150} className="mt-6">
        <div id="reports">
          {ndviLoading ? (
            <div className="glass-panel p-6">
              <h3 className="mb-3 text-xs font-semibold uppercase tracking-widest text-mist">
                MODIS Satellite NDVI
              </h3>
              <div className="flex items-center justify-center py-12">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-brand border-t-transparent" />
              </div>
            </div>
          ) : (
            <NdviChart series={ndviSeries} ndviChange={ndviChange} source={ndviSource ?? undefined} />
          )}
        </div>
      </LazyCard>

      {/* ── Fourth Row: AI Agronomy Copilot & Interactive Assistant Drawer ── */}
      <LazyCard delayMs={200} className="mt-6">
        <div className="space-y-6">
          {selectedFarm && <AiAssistantDrawer farmId={selectedFarm.id} />}

          <div>
            <div className="mb-3 flex items-center justify-between">
              <span className="flex items-center gap-2 text-sm font-semibold text-ink">
                <Icon name="spark" size={15} className="text-brand" />
                {t("aiCopilot", "AI Agronomy Assistant Summary")}
              </span>
              {selectedFarm && (
                <button
                  onClick={handleGetRecommendation}
                  disabled={recLoading}
                  className="flex items-center gap-1.5 rounded-lg bg-brand px-4 py-2 text-xs font-medium text-abyss transition-colors hover:bg-brand-dark disabled:opacity-50"
                >
                  <Icon name="bot" size={14} />
                  {recLoading ? t("synthesizingRec", "Generating…") : t("generateRec", "Generate Recommendation")}
                </button>
              )}
            </div>

            <RecommendationPanel recommendation={recommendation} loading={recLoading} />
          </div>
        </div>
      </LazyCard>


      {/* ── Data Sources Footer Ribbon ─────────────────────────────────────── */}
      <LazyCard delayMs={250} className="mt-8">
        <div className="glass-panel p-4">
          <h3 className="mb-2.5 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-dim">
            <Icon name="database" size={12} />
            Integrated Data Feeds
          </h3>
          <div className="flex flex-wrap gap-2 text-xs">
            <span className="inline-flex items-center gap-1.5 rounded-lg border border-edge bg-abyss px-2.5 py-1 text-mist">
              <span className="h-1.5 w-1.5 rounded-full bg-sky-500" />
              Open-Meteo &middot; Ground Weather &amp; Soil
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-lg border border-edge bg-abyss px-2.5 py-1 text-mist">
              <span className="h-1.5 w-1.5 rounded-full bg-orange-500" />
              NASA POWER &middot; 30-Year Climate Normals
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-lg border border-edge bg-abyss px-2.5 py-1 text-mist">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              MODIS Terra &middot; 250m 16-Day NDVI
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-lg border border-edge bg-abyss px-2.5 py-1 text-mist">
              <span className="h-1.5 w-1.5 rounded-full bg-violet-500" />
              AgriCore &middot; Multi-Vector Health Engine
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-lg border border-edge bg-abyss px-2.5 py-1 text-mist">
              <span className="h-1.5 w-1.5 rounded-full bg-teal-500" />
              Punjab Agriculture &middot; Crop Knowledge
            </span>
          </div>
        </div>
      </LazyCard>

      {/* ── Custom Delete Confirmation Modal ─────────────────────────────── */}
      <ConfirmModal
        isOpen={showDeleteModal}
        title="Delete Farm"
        message={`Are you sure you want to delete "${selectedFarm?.name}"? This will permanently delete all associated crop cycles, satellite NDVI data, and agronomic records.`}
        confirmText="Delete Farm"
        cancelText="Keep Farm"
        isDestructive={true}
        loading={deleting}
        onConfirm={confirmDeleteFarm}
        onClose={() => setShowDeleteModal(false)}
      />
    </div>
  );
}
