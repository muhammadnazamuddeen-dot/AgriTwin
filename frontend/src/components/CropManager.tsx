"use client";

import { useEffect, useState } from "react";
import { api, type Crop, type CropKnowledge } from "@/lib/api";
import Icon from "@/components/Icon";

interface CropManagerProps {
  farmId: number;
  onCropAdded?: () => void;
}

const STAGES = [
  { name: "Sowing", minDays: 0, maxDays: 14 },
  { name: "Emergence", minDays: 15, maxDays: 35 },
  { name: "Vegetative", minDays: 36, maxDays: 70 },
  { name: "Flowering", minDays: 71, maxDays: 105 },
  { name: "Ripening", minDays: 106, maxDays: 140 },
  { name: "Harvest", minDays: 141, maxDays: 999 },
];

function getStageFromSowingDate(sowingDateStr: string | null): { stageIndex: number; daysAfterSowing: number } {
  if (!sowingDateStr) return { stageIndex: 2, daysAfterSowing: 45 };
  const sowing = new Date(sowingDateStr);
  const now = new Date();
  const diffDays = Math.max(0, Math.floor((now.getTime() - sowing.getTime()) / (1000 * 60 * 60 * 24)));

  const idx = STAGES.findIndex((s) => diffDays >= s.minDays && diffDays <= s.maxDays);
  return { stageIndex: idx !== -1 ? idx : STAGES.length - 1, daysAfterSowing: diffDays };
}

export default function CropManager({ farmId, onCropAdded }: CropManagerProps) {
  const [crops, setCrops] = useState<Crop[]>([]);
  const [knowledge, setKnowledge] = useState<CropKnowledge[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(true);

  // Add form state
  const [selectedCrop, setSelectedCrop] = useState("");
  const [selectedSeason, setSelectedSeason] = useState("");
  const [sowingDate, setSowingDate] = useState("");

  // Load crops + knowledge
  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.listCrops(farmId).catch(() => []),
      api.getCropKnowledge().catch(() => []),
    ]).then(([c, k]) => {
      setCrops(c);
      setKnowledge(k);
      if (k.length > 0) {
        setSelectedCrop(k[0].name);
        setSelectedSeason(k[0].season);
      }
      setLoading(false);
    });
  }, [farmId]);

  const handleAddCrop = async () => {
    if (!selectedCrop) return;
    try {
      const crop = await api.addCrop(farmId, {
        crop_name: selectedCrop,
        season: selectedSeason || undefined,
        sowing_date: sowingDate ? new Date(sowingDate).toISOString() : undefined,
      });
      setCrops((prev) => [...prev, crop]);
      setShowAddForm(false);
      setSowingDate("");
      onCropAdded?.();
    } catch (err) {
      alert(`Failed to add crop: ${err}`);
    }
  };

  if (loading) {
    return (
      <div className="glass-panel p-5">
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-widest text-mist">
          Crop Lifecycle Intelligence
        </h3>
        <div className="flex items-center justify-center py-6">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-brand border-t-transparent" />
        </div>
      </div>
    );
  }

  const selectedInfo = knowledge.find((k) => k.name === selectedCrop);
  const activeCrop = crops[0]; // primary active crop
  const { stageIndex, daysAfterSowing } = activeCrop
    ? getStageFromSowingDate(activeCrop.sowing_date)
    : { stageIndex: 0, daysAfterSowing: 0 };

  return (
    <div className="glass-panel p-5 relative overflow-hidden">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-emerald-500/15 text-brand ring-1 ring-emerald-400/30">
            <Icon name="wheat" size={14} />
          </span>
          <h3 className="text-xs font-semibold uppercase tracking-widest text-mist">
            Crop Lifecycle &amp; Phenology
          </h3>
        </div>

        {!showAddForm && (
          <button
            onClick={() => setShowAddForm(true)}
            className="flex items-center gap-1 rounded-lg bg-brand/15 border border-brand/30 px-2.5 py-1 text-xs font-semibold text-brand transition-all hover:bg-brand/25"
          >
            <Icon name="plus" size={12} strokeWidth={2.5} />
            Add Crop
          </button>
        )}
      </div>

      {/* Active Crop Lifecycle Stepper */}
      {activeCrop ? (
        <div className="mb-4 rounded-xl border border-white/6 bg-white/[0.03] p-4">
          <div className="flex items-start justify-between gap-2 mb-3">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold text-ink">
                  {activeCrop.crop_name}
                </span>
                <span className="rounded-md border border-brand/30 bg-brand/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-brand">
                  {activeCrop.season || "Punjab Season"}
                </span>
              </div>
              <p className="text-xs text-mist mt-0.5">
                {activeCrop.sowing_date ? (
                  <>Sown {new Date(activeCrop.sowing_date).toLocaleDateString("en-PK", { month: "short", day: "numeric", year: "numeric" })} &middot; <span className="text-ink font-semibold">{daysAfterSowing} days after sowing</span></>
                ) : (
                  "Active cropping cycle"
                )}
              </p>
            </div>
          </div>

          {/* Growth Stage Horizontal Stepper */}
          <div className="pt-2">
            <div className="flex items-center justify-between text-[10px] font-mono text-dim mb-2">
              <span>Growth Timeline</span>
              <span className="text-brand font-semibold">{STAGES[stageIndex].name} Phase</span>
            </div>

            <div className="grid grid-cols-6 gap-1">
              {STAGES.map((s, idx) => {
                const isPast = idx < stageIndex;
                const isCurrent = idx === stageIndex;
                return (
                  <div key={s.name} className="flex flex-col items-center gap-1 text-center">
                    <div
                      className={`h-1.5 w-full rounded-full transition-all ${isCurrent
                          ? "bg-brand shadow-[0_0_8px_rgba(52,211,153,0.8)]"
                          : isPast
                            ? "bg-emerald-500/60"
                            : "bg-white/10"
                        }`}
                    />
                    <span
                      className={`text-[9px] font-medium leading-tight truncate w-full ${isCurrent
                          ? "text-brand font-bold"
                          : isPast
                            ? "text-mist"
                            : "text-dim"
                        }`}
                    >
                      {s.name}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ) : (
        <div className="mb-4 rounded-xl border border-white/6 bg-white/[0.02] p-6 text-center">
          <Icon name="wheat" size={24} className="mx-auto text-dim mb-2" />
          <p className="text-sm font-medium text-ink">No Crops Registered</p>
          <p className="text-xs text-dim mt-1">
            Register your planted crop (e.g. Wheat, Cotton, Rice) to unlock growth stage intelligence.
          </p>
        </div>
      )}

      {/* Add Crop Modal Form (Moved to fixed modal) */}
      {showAddForm && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="rounded-2xl border border-brand/40 bg-panel/95 p-6 shadow-2xl w-full max-w-md relative animate-in fade-in zoom-in-95 duration-300">
            <div className="flex items-center justify-between mb-5">
              <h4 className="text-sm font-bold uppercase tracking-wider text-brand flex items-center gap-2">
                <Icon name="wheat" size={16} />
                Register Planted Crop
              </h4>
              <button
                onClick={() => setShowAddForm(false)}
                className="flex h-8 w-8 items-center justify-center rounded-lg text-dim hover:bg-white/10 hover:text-ink transition-colors"
              >
                <Icon name="x" size={16} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-mist mb-1.5 block">
                  Crop Variety (Punjab Agricultural Index)
                </label>
                <select
                  value={selectedCrop}
                  onChange={(e) => {
                    setSelectedCrop(e.target.value);
                    const info = knowledge.find((k) => k.name === e.target.value);
                    if (info) setSelectedSeason(info.season);
                  }}
                  className="input-dark bg-panel w-full"
                >
                  {knowledge.map((k) => (
                    <option key={k.name} value={k.name}>
                      {k.name} &mdash; {k.season} Season
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-mist mb-1.5 block">
                  Sowing Date (for phenology tracking)
                </label>
                <input
                  type="date"
                  value={sowingDate}
                  onChange={(e) => setSowingDate(e.target.value)}
                  className="input-dark [color-scheme:dark] w-full"
                />
              </div>

              {/* Crop Info Preview */}
              {selectedInfo && (
                <div className="grid grid-cols-2 gap-3 rounded-xl border border-white/6 bg-white/[0.03] p-3.5 text-xs text-mist">
                  <div>
                    <span className="text-dim block text-[10px] uppercase font-semibold mb-0.5">Sowing Window</span>
                    <span className="font-medium text-ink">{selectedInfo.sowing_window}</span>
                  </div>
                  <div>
                    <span className="text-dim block text-[10px] uppercase font-semibold mb-0.5">Water Demand</span>
                    <span className="font-medium text-ink">{selectedInfo.water_requirement_mm} mm</span>
                  </div>
                  <div className="col-span-2 pt-2 mt-1 border-t border-white/6">
                    <span className="text-dim block text-[10px] uppercase font-semibold mb-0.5">Common Punjab Pests</span>
                    <span className="text-ink">{selectedInfo.common_pests.slice(0, 3).join(", ")}</span>
                  </div>
                </div>
              )}

              <div className="flex gap-3 pt-3 mt-4 border-t border-white/10">
                <button
                  onClick={handleAddCrop}
                  className="flex-1 rounded-xl bg-gradient-to-b from-emerald-400 to-emerald-600 px-4 py-2.5 text-sm font-bold text-abyss shadow-md hover:shadow-lg transition-all"
                >
                  Save Crop Data
                </button>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="rounded-xl border border-white/12 bg-white/5 px-4 py-2.5 text-sm font-medium text-mist hover:bg-white/10 hover:text-ink transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
