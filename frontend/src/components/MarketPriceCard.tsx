"use client";

import { useState } from "react";
import Icon from "@/components/Icon";
import { useLanguage } from "@/components/LanguageProvider";

interface MarketPriceCardProps {
  cropName?: string;
  currentPricePkr?: number;
  changePct?: number;
}

export default function MarketPriceCard({
  cropName = "Maize",
  currentPricePkr = 3000,
  changePct = 8.4,
}: MarketPriceCardProps) {
  const { isUrdu } = useLanguage();
  const [unit, setUnit] = useState("PKR / 40kg");

  // Unit multiplier: 40kg = 1.0, Maund = 1.0 (40kg), Ton = 25x (1000kg)
  const multiplier = unit === "PKR / Ton" ? 25 : 1;
  const displayPrice = Math.round(currentPricePkr * multiplier);

  // Synthetic price trend points matching reference screenshot curve
  const points = [
    { label: "30d ago" },
    { label: "20d ago" },
    { label: "10d ago" },
    { label: "Today" },
  ];

  return (
    <div className="glass-panel p-5 relative flex flex-col justify-between">
      {/* Header with Unit Selector */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold text-mist uppercase tracking-wider">
          {isUrdu ? `مارکیٹ قیمت (${cropName})` : `Market Price (${cropName})`}
        </h3>
        <select
          value={unit}
          onChange={(e) => setUnit(e.target.value)}
          className="rounded-lg border border-edge bg-abyss px-2.5 py-1 text-[11px] font-medium text-mist outline-none cursor-pointer"
        >
          <option value="PKR / 40kg">PKR / 40kg</option>
          <option value="PKR / Maund">PKR / Maund</option>
          <option value="PKR / Ton">PKR / Ton</option>
        </select>
      </div>

      {/* Main Price & Trend Indicator */}
      <div className="flex items-baseline gap-2.5 mb-4">
        <span className="text-2xl font-bold text-ink tracking-tight">
          PKR {displayPrice.toLocaleString()}
        </span>
        <span className="flex items-center gap-1 text-xs font-semibold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-md">
          <Icon name="trendUp" size={13} />
          <span>↑ {changePct}%</span>
          <span className="text-[10px] text-dim font-normal">vs last 30 days</span>
        </span>
      </div>

      {/* 30-Day Gradient Area Chart */}
      <div className="relative h-28 w-full mt-1">
        <svg viewBox="0 0 300 90" className="h-full w-full overflow-visible">
          <defs>
            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22C55E" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#22C55E" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          <line x1="0" y1="20" x2="300" y2="20" stroke="rgba(128,128,128,0.1)" strokeDasharray="3 3" />
          <line x1="0" y1="50" x2="300" y2="50" stroke="rgba(128,128,128,0.1)" strokeDasharray="3 3" />

          {/* Area Fill */}
          <path
            d="M 0 65 Q 50 55, 100 60 T 200 35 T 300 20 L 300 90 L 0 90 Z"
            fill="url(#priceGradient)"
          />

          {/* Smooth Trend Line */}
          <path
            d="M 0 65 Q 50 55, 100 60 T 200 35 T 300 20"
            fill="none"
            stroke="#22C55E"
            strokeWidth="2.5"
            strokeLinecap="round"
          />

          {/* End Point Glow Indicator */}
          <circle cx="300" cy="20" r="4" fill="#22C55E" className="animate-pulse" />
        </svg>

        {/* X-Axis Labels */}
        <div className="flex justify-between text-[10px] text-dim mt-2">
          {points.map((p) => (
            <span key={p.label}>{p.label}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
