"use client";

import { useEffect, useState } from "react";
import Icon from "@/components/Icon";
import { useLanguage } from "@/components/LanguageProvider";
import { api, type PestRiskResponse, type PestRiskItem } from "@/lib/api";

interface PestRiskCardProps {
  farmId: number;
  cropName?: string;
}

export default function PestRiskCard({ farmId, cropName }: PestRiskCardProps) {
  const { t, isUrdu } = useLanguage();
  const [data, setData] = useState<PestRiskResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    api
      .getPestDiseaseRisk(farmId, cropName)
      .then((res) => {
        if (mounted) setData(res);
      })
      .catch((err) => {
        console.warn("Failed to load pest risk:", err);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [farmId, cropName]);

  if (loading) {
    return (
      <div className="glass-panel p-5 animate-pulse">
        <div className="h-4 w-48 bg-ink/10 rounded mb-4" />
        <div className="h-20 bg-ink/5 rounded-xl" />
      </div>
    );
  }

  if (!data || !data.risks || data.risks.length === 0) return null;

  const getOverallBadgeClass = (level: string) => {
    if (level.includes("High") || level.includes("Critical"))
      return "bg-rose-500/15 text-rose-500 border-rose-500/30";
    if (level.includes("Moderate"))
      return "bg-amber-500/15 text-amber-500 border-amber-500/30";
    return "bg-emerald-500/15 text-emerald-500 border-emerald-500/30";
  };

  const getRiskLevelBadgeClass = (level: string) => {
    switch (level.toLowerCase()) {
      case "high":
        return "bg-rose-500/20 text-rose-400 border-rose-500/30";
      case "medium":
      case "moderate":
        return "bg-amber-500/20 text-amber-400 border-amber-500/30";
      default:
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
    }
  };

  return (
    <div className="glass-panel p-5 relative overflow-hidden transition-all duration-300">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-rose-500/15 text-rose-500 ring-1 ring-rose-400/30">
            <Icon name="bug" size={13} />
          </div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-widest text-mist">
              {isUrdu ? "کیڑے تے بیماریاں دا خطرہ" : "Pest & Pathogen Risk Matrix"}
            </span>
            <p className="text-[11px] text-mist/80">
              {data.crop_name} {data.growth_stage ? `• ${data.growth_stage}` : ""}
            </p>
          </div>
        </div>

        <span
          className={`text-xs px-3 py-1 rounded-full border font-medium ${getOverallBadgeClass(
            data.overall_pest_risk
          )}`}
        >
          {data.overall_pest_risk}
        </span>
      </div>

      {/* Risk Items List */}
      <div className="space-y-3">
        {data.risks.map((item: PestRiskItem, idx: number) => {
          const isExpanded = expandedIndex === idx;

          return (
            <div
              key={item.pest_or_disease_name}
              className="rounded-xl border border-ink/10 bg-ink/5 overflow-hidden transition-all"
            >
              {/* Collapsible Item Header */}
              <button
                onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                className="w-full p-3 flex items-center justify-between text-left hover:bg-ink/10 transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <span
                    className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded font-medium border ${getRiskLevelBadgeClass(
                      item.risk_level
                    )}`}
                  >
                    {item.risk_level}
                  </span>
                  <div>
                    <h5 className="text-sm font-semibold text-ink flex items-center gap-2">
                      {item.pest_or_disease_name}
                      <span className="text-xs font-normal text-mist">({item.category})</span>
                    </h5>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <span className="text-sm font-bold text-ink">{item.risk_score}%</span>
                  </div>
                  <Icon
                    name={isExpanded ? "chevronDown" : "chevronRight"}
                    size={14}
                    className="text-mist"
                  />
                </div>
              </button>

              {/* Item Details */}
              {isExpanded && (
                <div className="p-3.5 pt-0 border-t border-ink/10 space-y-3 text-xs">
                  {/* Triggers */}
                  <div>
                    <span className="font-semibold text-mist uppercase tracking-wider text-[10px] block mb-1">
                      {isUrdu ? "وجوہات / محرکات" : "Trigger Conditions"}
                    </span>
                    <ul className="space-y-0.5">
                      {item.trigger_conditions.map((trig, tIdx) => (
                        <li key={tIdx} className="text-ink/90 flex items-start gap-1.5">
                          <span className="text-rose-400">•</span>
                          <span>{trig}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Organic & Chemical Controls */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 pt-2 border-t border-ink/10">
                    <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-2.5">
                      <span className="font-semibold text-emerald-400 block mb-1">
                        🌱 {isUrdu ? "نامیاتی (آرگینک) کنٹرول" : "Organic / Cultural Control"}
                      </span>
                      <p className="text-ink/90 leading-relaxed">{item.organic_control}</p>
                    </div>

                    <div className="rounded-lg bg-blue-500/10 border border-blue-500/20 p-2.5">
                      <span className="font-semibold text-blue-400 block mb-1">
                        🧪 {isUrdu ? "کیمیائی سپرے" : "Chemical Spray Intervention"}
                      </span>
                      <p className="text-ink/90 leading-relaxed">{item.chemical_control}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
