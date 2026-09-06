"use client";

import Icon from "@/components/Icon";
import { useLanguage } from "@/components/LanguageProvider";

interface RecommendedCropCardProps {
  cropName?: string;
  score?: number;
  reasons?: string[];
  onViewAnalysis?: () => void;
}

export default function RecommendedCropCard({
  cropName = "Maize",
  score = 87,
  reasons,
  onViewAnalysis,
}: RecommendedCropCardProps) {
  const { isUrdu } = useLanguage();

  const defaultHighlights = [
    isUrdu ? "تہاڈی زمین لئی انتہائی موزوں" : "High suitability for your land",
    isUrdu ? "مارکیٹ دا بہترین رجحان" : "Positive market trend",
    isUrdu ? "منافع دا بہترین امکان" : "Good profit potential",
    isUrdu ? "پانی دی گھٹ لوڑ" : "Low water requirement",
  ];

  const highlights = reasons && reasons.length > 0 ? reasons : defaultHighlights;

  return (
    <div className="glass-panel p-5 flex flex-col justify-between h-full">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xs font-semibold text-mist uppercase tracking-wider">
            {isUrdu ? "تجویز کردہ فصل" : "Recommended Crop"}
          </h3>
          <span className="rounded-full bg-emerald-500/15 border border-emerald-500/30 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-500">
            {isUrdu ? "بہترین انتخاب" : "Best Choice"}
          </span>
        </div>

        {/* Hero Crop Image & Score */}
        <div className="flex items-center gap-4 mb-5">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-500 ring-1 ring-emerald-500/20 text-3xl shrink-0">
            🌽
          </div>
          <div>
            <h2 className="text-2xl font-bold text-ink tracking-tight">{cropName}</h2>
            <p className="text-xs font-medium text-mist mt-0.5">
              {isUrdu ? "اسکور:" : "Score:"} <strong className="text-emerald-500">{score}/100</strong>
            </p>
          </div>
        </div>

        {/* Bullet checklist */}
        <div className="space-y-2.5 mb-6 text-xs text-ink font-medium">
          {highlights.map((item, idx) => (
            <div key={idx} className="flex items-center gap-2.5">
              <span className="flex h-4 w-4 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-500 shrink-0">
                <Icon name="check" size={11} strokeWidth={3} />
              </span>
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Action Button */}
      <button
        onClick={onViewAnalysis}
        className="flex w-full items-center justify-center gap-2 rounded-xl bg-brand py-3 text-xs font-bold text-white transition-all hover:bg-brand-dark shadow-sm"
      >
        <span>{isUrdu ? "مکمل تجزیہ دیکھو" : "View Full Analysis"}</span>
        <Icon name="chevronRight" size={15} />
      </button>
    </div>
  );
}
