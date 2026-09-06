"use client";

import Icon from "@/components/Icon";
import { useLanguage } from "@/components/LanguageProvider";

interface KpiMetricsBarProps {
  healthScore?: number;
  weatherTemp?: number;
  weatherStatus?: string;
  marketTrendPct?: number;
  yieldPredictionTHa?: number | null;
  farmAcres?: number;
  cropName?: string;
}

export default function KpiMetricsBar({
  healthScore = 78,
  weatherTemp = 32,
  weatherStatus = "Partly Cloudy",
  marketTrendPct = 8.4,
  yieldPredictionTHa = 4.25,
  farmAcres = 10.24,
  cropName = "Wheat",
}: KpiMetricsBarProps) {
  const { isUrdu } = useLanguage();

  const totalYieldEst = yieldPredictionTHa
    ? Math.round(yieldPredictionTHa * (farmAcres * 0.404686) * 10) / 10
    : null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* KPI 1: Farm Health Score */}
      <div className="glass-panel p-4 flex items-center justify-between relative overflow-hidden">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand/15 text-brand shrink-0">
              <Icon name="sprout" size={15} />
            </span>
            <span className="text-[11px] font-semibold text-mist uppercase tracking-wider">
              {isUrdu ? "فارم ہیلتھ انڈیکس" : "Farm Health Index"}
            </span>
          </div>

          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-ink tracking-tight">{healthScore}</span>
            <span className="text-xs text-dim font-medium">/100</span>
          </div>

          <span className="mt-1 inline-block text-[11px] font-semibold text-emerald-500">
            {healthScore >= 75
              ? (isUrdu ? "بہترین (حالت تسلی بخش)" : "Optimal Condition")
              : (isUrdu ? "درمیانہ دباؤ" : "Moderate Stress")}
          </span>
        </div>

        {/* Right Sparkline Graph */}
        <div className="w-20 h-10 shrink-0">
          <svg viewBox="0 0 80 40" className="w-full h-full">
            <path
              d="M 0 30 Q 20 25, 40 20 T 80 5"
              fill="none"
              stroke="#22C55E"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
            <circle cx="80" cy="5" r="3" fill="#22C55E" />
          </svg>
        </div>
      </div>

      {/* KPI 2: Current Weather */}
      <div className="glass-panel p-4 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-sky-500/15 text-sky-500 shrink-0">
              <Icon name="cloudSun" size={15} />
            </span>
            <span className="text-[11px] font-semibold text-mist uppercase tracking-wider">
              {isUrdu ? "موجودہ موسم" : "Current Weather"}
            </span>
          </div>

          <div className="text-2xl font-bold text-ink tracking-tight">
            {weatherTemp}°C
          </div>

          <p className="mt-1 text-[11px] font-medium text-mist">
            {weatherStatus}
          </p>
        </div>

        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-500/10 text-sky-500">
          <Icon name="sun" size={20} />
        </span>
      </div>

      {/* KPI 3: Market Trend */}
      <div className="glass-panel p-4 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand/15 text-brand shrink-0">
              <Icon name="trendUp" size={15} />
            </span>
            <span className="text-[11px] font-semibold text-mist uppercase tracking-wider">
              {isUrdu ? `منڈی ریٹ رجحان (${cropName})` : `Market Trend (${cropName})`}
            </span>
          </div>

          <div className="text-2xl font-bold text-emerald-500 tracking-tight flex items-center gap-1">
            <Icon name="trendUp" size={18} />
            <span>+{marketTrendPct}%</span>
          </div>

          <p className="mt-1 text-[11px] font-medium text-mist">
            {isUrdu ? "پنجاب منڈی اوسط (30 دن)" : "Punjab Mandi 30d Avg"}
          </p>
        </div>

        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-500">
          <Icon name="trendUp" size={20} />
        </span>
      </div>

      {/* KPI 4: ML Yield Prediction */}
      <div className="glass-panel p-4 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-500/15 text-amber-500 shrink-0">
              <Icon name="activity" size={15} />
            </span>
            <span className="text-[11px] font-semibold text-mist uppercase tracking-wider">
              {isUrdu ? "تخمینہ پیداوار (ML Model)" : "Yield Prediction (ML)"}
            </span>
          </div>

          <div className="text-xl sm:text-2xl font-bold text-ink tracking-tight">
            {yieldPredictionTHa ? `${yieldPredictionTHa.toFixed(2)} t/ha` : "N/A"}
          </div>

          <p className="mt-1 text-[11px] font-medium text-mist">
            {totalYieldEst ? `${totalYieldEst} Tons (${farmAcres} Acres)` : `${farmAcres} Acres · ${cropName}`}
          </p>
        </div>

        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 text-amber-500">
          <Icon name="layers" size={20} />
        </span>
      </div>
    </div>
  );
}
