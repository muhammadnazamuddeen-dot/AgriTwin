"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api, type Farm } from "@/lib/api";
import Icon from "@/components/Icon";

export default function FarmsHubPage() {
  const [farms, setFarms] = useState<Farm[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDistrict, setSelectedDistrict] = useState<string>("all");

  useEffect(() => {
    setLoading(true);
    api
      .listFarms()
      .then((data) => setFarms(data))
      .catch(() => setFarms([]))
      .finally(() => setLoading(false));
  }, []);

  const districts = useMemo(() => {
    const set = new Set<string>();
    farms.forEach((f) => {
      if (f.district) set.add(f.district);
    });
    return ["all", ...Array.from(set)];
  }, [farms]);

  const filteredFarms = useMemo(() => {
    return farms.filter((f) => {
      const matchesSearch =
        searchQuery === "" ||
        f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (f.district && f.district.toLowerCase().includes(searchQuery.toLowerCase())) ||
        f.province.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesDistrict =
        selectedDistrict === "all" || f.district === selectedDistrict;

      return matchesSearch && matchesDistrict;
    });
  }, [farms, searchQuery, selectedDistrict]);

  const totalAcres = useMemo(() => {
    return farms.reduce((acc, f) => acc + (f.area_acres || 0), 0);
  }, [farms]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* ── Top Header & Stats ────────────────────────────────────────── */}
      <div className="mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/15 text-brand ring-1 ring-emerald-400/30">
                <Icon name="wheat" size={16} />
              </span>
              <h1 className="text-2xl font-bold tracking-tight text-ink">
                Farms <span className="bg-gradient-to-r from-emerald-400 to-lime-300 bg-clip-text text-transparent">Hub</span>
              </h1>
            </div>
            <p className="mt-1 text-sm text-mist">
              Manage your agricultural digital twin nodes across Punjab, Pakistan.
            </p>
          </div>

          <Link
            href="/"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-b from-emerald-400 to-emerald-600 px-4 py-2.5 text-sm font-semibold text-abyss shadow-[0_4px_16px_rgba(16,185,129,0.35)] transition-all hover:scale-[1.02] hover:shadow-[0_4px_24px_rgba(16,185,129,0.55)]"
          >
            <Icon name="pencil" size={14} strokeWidth={2.4} />
            Draw New Farm on Map
          </Link>
        </div>

        {/* Telemetry quick stats */}
        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="glass-card p-4">
            <p className="text-xs font-medium uppercase tracking-wider text-dim">
              Registered Farms
            </p>
            <p className="mt-1 text-2xl font-bold tabular-nums text-ink">
              {farms.length}
            </p>
            <p className="mt-0.5 text-[11px] text-brand">Active Twin Nodes</p>
          </div>

          <div className="glass-card p-4">
            <p className="text-xs font-medium uppercase tracking-wider text-dim">
              Monitored Area
            </p>
            <p className="mt-1 text-2xl font-bold tabular-nums text-ink">
              {totalAcres.toLocaleString()} <span className="text-xs font-normal text-mist">ac</span>
            </p>
            <p className="mt-0.5 text-[11px] text-mist">
              ≈ {(totalAcres * 0.404686).toFixed(1)} ha
            </p>
          </div>

          <div className="glass-card p-4">
            <p className="text-xs font-medium uppercase tracking-wider text-dim">
              Districts Covered
            </p>
            <p className="mt-1 text-2xl font-bold tabular-nums text-ink">
              {Math.max(1, districts.length - 1)}
            </p>
            <p className="mt-0.5 text-[11px] text-mist">Punjab Province</p>
          </div>

          <div className="glass-card p-4">
            <p className="text-xs font-medium uppercase tracking-wider text-dim">
              Satellite Sync
            </p>
            <p className="mt-1 text-base font-bold text-emerald-300 flex items-center gap-1.5 truncate">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              MODIS Terra
            </p>
            <p className="mt-0.5 text-[11px] text-dim">250m 16-Day NDVI</p>
          </div>
        </div>
      </div>

      {/* ── Search & Filter Toolbar ─────────────────────────────────────── */}
      <div className="mb-6 flex flex-col sm:flex-row items-center justify-between gap-3 glass-panel p-3">
        {/* Search input */}
        <div className="relative w-full sm:w-80">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-dim">
            <Icon name="search" size={14} />
          </span>
          <input
            type="text"
            placeholder="Search farm name or district…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-dark pl-9 pr-3 py-2 text-xs"
          />
        </div>

        {/* District Filter Pills */}
        <div className="flex w-full sm:w-auto items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          <span className="text-xs text-dim flex items-center gap-1 shrink-0 mr-1">
            <Icon name="filter" size={12} />
            District:
          </span>
          {districts.map((d) => {
            const isActive = selectedDistrict === d;
            return (
              <button
                key={d}
                onClick={() => setSelectedDistrict(d)}
                className={`shrink-0 rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${isActive
                    ? "bg-brand/20 text-brand border border-brand/35 shadow-[0_0_10px_rgba(52,211,153,0.25)]"
                    : "text-mist hover:bg-white/6 hover:text-ink border border-white/6"
                  }`}
              >
                {d === "all" ? "All Districts" : d}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Farms Grid ──────────────────────────────────────────────────── */}
      {loading ? (
        <div className="glass-panel p-12 text-center">
          <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-brand border-t-transparent" />
          <p className="text-sm text-mist">Loading farm telemetry...</p>
        </div>
      ) : filteredFarms.length === 0 ? (
        <div className="glass-panel p-12 text-center">
          <span className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/6 text-dim">
            <Icon name="wheat" size={28} />
          </span>
          <h3 className="text-base font-semibold text-ink">No farms found</h3>
          <p className="mt-1 text-sm text-mist max-w-sm mx-auto">
            {searchQuery || selectedDistrict !== "all"
              ? "No farms match your search criteria. Try resetting your filters."
              : "No farms registered yet. Open the Mission Control map to draw your first farm boundary."}
          </p>
          <div className="mt-5">
            <Link
              href="/"
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-b from-emerald-400 to-emerald-600 px-4 py-2 text-sm font-semibold text-abyss shadow-[0_4px_16px_rgba(16,185,129,0.35)]"
            >
              <Icon name="pencil" size={14} />
              Open Map &amp; Draw Farm
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
          {filteredFarms.map((farm) => (
            <div
              key={farm.id}
              className="glass-card-hover group flex flex-col justify-between p-5 relative overflow-hidden"
            >
              {/* Subtle top glow bar */}
              <div className="absolute top-0 inset-x-0 h-0.5 bg-gradient-to-r from-emerald-500/40 via-brand to-lime-400/40 opacity-0 group-hover:opacity-100 transition-opacity" />

              <div>
                {/* Card Header */}
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div>
                    <h3 className="text-base font-bold text-ink group-hover:text-brand transition-colors">
                      {farm.name}
                    </h3>
                    <p className="flex items-center gap-1.5 text-xs text-mist mt-0.5">
                      <Icon name="mapPin" size={12} className="text-brand shrink-0" />
                      {farm.district || "Punjab"}, {farm.province}
                    </p>
                  </div>
                  <span className="hud-pill text-emerald-300 border-emerald-400/30 bg-emerald-500/10 shrink-0">
                    Twin #{farm.id}
                  </span>
                </div>

                {/* Metrics Grid */}
                <div className="my-4 grid grid-cols-2 gap-2 rounded-xl border border-white/6 bg-white/[0.02] p-3 text-xs">
                  <div>
                    <span className="text-[10px] uppercase font-mono tracking-wider text-dim block">
                      Field Area
                    </span>
                    <span className="text-sm font-semibold tabular-nums text-ink">
                      {farm.area_acres != null ? `${farm.area_acres.toLocaleString()} ac` : "—"}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-mono tracking-wider text-dim block">
                      Centroid
                    </span>
                    <span className="text-xs font-mono text-mist truncate block">
                      {farm.latitude != null && farm.longitude != null
                        ? `${farm.latitude.toFixed(3)}, ${farm.longitude.toFixed(3)}`
                        : "—"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-3 border-t border-white/6 flex items-center gap-2">
                <Link
                  href={`/farms/${farm.id}`}
                  className="flex-1 flex items-center justify-center gap-1.5 rounded-lg bg-white/8 px-3 py-2 text-xs font-semibold text-ink hover:bg-brand hover:text-abyss transition-all shadow-sm"
                >
                  <Icon name="activity" size={13} />
                  Intelligence
                </Link>
                <Link
                  href={`/farms/${farm.id}/history`}
                  className="flex items-center justify-center gap-1 rounded-lg border border-white/10 px-3 py-2 text-xs font-semibold text-mist hover:text-ink hover:border-white/20 transition-colors"
                  title="View History"
                >
                  <Icon name="clock" size={13} />
                  History
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

