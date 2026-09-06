"use client";

import { useEffect, useState } from "react";
import Icon from "@/components/Icon";
import { useLanguage } from "@/components/LanguageProvider";
import { api, type CropSuitabilityResponse, type CropSuitabilityItem } from "@/lib/api";

interface CropSuitabilityCardProps {
  farmId: number;
}

export default function CropSuitabilityCard({ farmId }: CropSuitabilityCardProps) {
  const { t, isUrdu } = useLanguage();
  const [data, setData] = useState<CropSuitabilityResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedCropIndex, setSelectedCropIndex] = useState(0);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    api
      .getCropSuitability(farmId)
      .then((res) => {
        if (mounted) {
          setData(res);
          setSelectedCropIndex(0);
        }
      })
      .catch((err) => {
        console.warn("Failed to load crop suitability:", err);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [farmId]);

  if (loading) {
    return (
      <div className="glass-panel p-5 animate-pulse">
        <div className="h-4 w-48 bg-ink/10 rounded mb-4" />
        <div className="h-24 bg-ink/5 rounded-xl" />
      </div>
    );
  }

  if (!data || !data.ranked_crops || data.ranked_crops.length === 0) return null;

  const currentCrop: CropSuitabilityItem = data.ranked_crops[selectedCropIndex] || data.ranked_crops[0];

  const getCategoryBadgeClass = (category: string) => {
    switch (category.toLowerCase()) {
      case "highly suitable":
        return "bg-emerald-500/15 text-emerald-500 border-emerald-500/30";
      case "suitable":
        return "bg-blue-500/15 text-blue-500 border-blue-500/30";
      case "moderately suitable":
        return "bg-amber-500/15 text-amber-500 border-amber-500/30";
      default:
        return "bg-rose-500/15 text-rose-500 border-rose-500/30";
    }
  };

  return (
    <div className="glass-panel p-5 relative overflow-hidden transition-all duration-300">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-500 ring-1 ring-emerald-400/30">
            <Icon name="sprout" size={13} />
          </div>
          <span className="text-xs font-semibold uppercase tracking-widest text-mist">
            {isUrdu ? "فصل دی موزونیت (کراپ سوٹیبلٹی)" : "Crop Suitability Engine"}
          </span>
        </div>

        {/* Crop Switcher Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 max-w-full">
          {data.ranked_crops.map((item, idx) => (
            <button
              key={item.crop_name}
              onClick={() => setSelectedCropIndex(idx)}
              className={`px-2.5 py-1 text-xs font-medium rounded-lg border transition-all whitespace-nowrap ${
                selectedCropIndex === idx
                  ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/40 shadow-sm"
                  : "bg-ink/5 text-mist hover:text-ink border-transparent"
              }`}
            >
              {item.crop_name} ({item.suitability_score}%)
            </button>
          ))}
        </div>
      </div>

      {/* Main Score Card */}
      <div className="rounded-xl border border-ink/10 bg-ink/5 p-4 mb-4">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
          <div>
            <h4 className="text-base font-semibold text-ink flex items-center gap-2">
              {currentCrop.crop_name}
              <span
                className={`text-xs px-2.5 py-0.5 rounded-full border font-medium ${getCategoryBadgeClass(
                  currentCrop.category
                )}`}
              >
                {currentCrop.category}
              </span>
            </h4>
            <p className="text-xs text-mist mt-0.5">
              {isUrdu
                ? `زمین دے 4 اہم اجزاء دی بنیاد تے مجموعی سکور`
                : `Land suitability score derived from soil, climate, water & season match`}
            </p>
          </div>

          <div className="text-right">
            <span className="text-2xl font-bold text-emerald-500">
              {currentCrop.suitability_score}
            </span>
            <span className="text-xs text-mist font-medium"> / 100</span>
          </div>
        </div>

        {/* Sub-scores Progress Bars */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 pt-3 border-t border-ink/10">
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-mist">{isUrdu ? "زمین (سوائل)" : "Soil Match"}</span>
              <span className="font-medium text-ink">{currentCrop.soil_score}%</span>
            </div>
            <div className="h-1.5 w-full bg-ink/10 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-500 rounded-full transition-all duration-500"
                style={{ width: `${currentCrop.soil_score}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-mist">{isUrdu ? "موسم (کلائمیٹ)" : "Climate Match"}</span>
              <span className="font-medium text-ink">{currentCrop.climate_score}%</span>
            </div>
            <div className="h-1.5 w-full bg-ink/10 rounded-full overflow-hidden">
              <div
                className="h-full bg-sky-500 rounded-full transition-all duration-500"
                style={{ width: `${currentCrop.climate_score}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-mist">{isUrdu ? "پانی (واٹر)" : "Water Access"}</span>
              <span className="font-medium text-ink">{currentCrop.water_score}%</span>
            </div>
            <div className="h-1.5 w-full bg-ink/10 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full transition-all duration-500"
                style={{ width: `${currentCrop.water_score}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-mist">{isUrdu ? "موسمی وقت" : "Sowing Window"}</span>
              <span className="font-medium text-ink">{currentCrop.season_score}%</span>
            </div>
            <div className="h-1.5 w-full bg-ink/10 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                style={{ width: `${currentCrop.season_score}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Limiting Factors & Recommendations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {currentCrop.limiting_factors.length > 0 && (
          <div className="rounded-lg bg-amber-500/10 border border-amber-500/20 p-3">
            <h5 className="text-xs font-semibold text-amber-500 flex items-center gap-1.5 mb-1.5">
              <Icon name="alert" size={12} />
              {isUrdu ? "محدود کرنے والے عوامل" : "Limiting Factors"}
            </h5>
            <ul className="space-y-1">
              {currentCrop.limiting_factors.map((factor, idx) => (
                <li key={idx} className="text-xs text-ink/90 flex items-start gap-1.5">
                  <span className="text-amber-500">•</span>
                  <span>{factor}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {currentCrop.recommendations.length > 0 && (
          <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-3">
            <h5 className="text-xs font-semibold text-emerald-500 flex items-center gap-1.5 mb-1.5">
              <Icon name="checkCircle" size={12} />
              {isUrdu ? "زرعی تجاویز" : "Agronomic Remediation"}
            </h5>
            <ul className="space-y-1">
              {currentCrop.recommendations.map((rec, idx) => (
                <li key={idx} className="text-xs text-ink/90 flex items-start gap-1.5">
                  <span className="text-emerald-500">✓</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
