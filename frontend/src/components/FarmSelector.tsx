"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Farm } from "@/lib/api";
import Icon from "@/components/Icon";
import { useLanguage } from "./LanguageProvider";

interface FarmSelectorProps {
  farms: Farm[];
  selected: Farm | null;
  onSelect: (farm: Farm | null) => void;
}

/**
 * Location-aware farm picker: searchable, grouped by district,
 * showing area + coordinates for each farm.
 */
export default function FarmSelector({ farms, selected, onSelect }: FarmSelectorProps) {
  const { t, isUrdu } = useLanguage();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const rootRef = useRef<HTMLDivElement>(null);

  // Close on outside click / Escape
  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      document.removeEventListener("keydown", onKey);
    };
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return farms;
    return farms.filter(
      (f) =>
        f.name.toLowerCase().includes(q) ||
        (f.district ?? "").toLowerCase().includes(q) ||
        f.province.toLowerCase().includes(q)
    );
  }, [farms, query]);

  const grouped = useMemo(() => {
    const m = new Map<string, Farm[]>();
    for (const f of filtered) {
      const key = f.district?.trim() || f.province || "Punjab District";
      const list = m.get(key) ?? [];
      list.push(f);
      m.set(key, list);
    }
    return [...m.entries()];
  }, [filtered]);

  return (
    <div ref={rootRef} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex min-w-[200px] items-center justify-between gap-2 rounded-lg border border-edge bg-panel px-3 py-1.5 text-xs font-medium text-ink transition-colors hover:border-brand/40 shadow-sm"
      >
        <span className="flex items-center gap-2 truncate">
          <Icon name="wheat" size={13} className="shrink-0 text-brand" />
          <span className="truncate">
            {selected ? selected.name : t("selectFarm", "Select Farm…")}
          </span>
        </span>

        <div className="flex items-center gap-1 shrink-0">
          {selected && (
            <span
              role="button"
              tabIndex={0}
              onClick={(e) => {
                e.stopPropagation();
                onSelect(null);
                setOpen(false);
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.stopPropagation();
                  onSelect(null);
                  setOpen(false);
                }
              }}
              className="rounded p-0.5 text-dim hover:text-rose-500 hover:bg-rose-500/10"
              title="Clear selection"
            >
              <Icon name="x" size={11} />
            </span>
          )}
          <Icon
            name="chevronDown"
            size={13}
            className={`text-dim transition-transform duration-200 ${open ? "rotate-180" : ""}`}
          />
        </div>
      </button>

      {open && (
        <div className="absolute left-0 md:left-auto md:right-0 z-50 mt-1.5 w-[calc(100vw-32px)] md:w-80 max-w-sm rounded-xl border border-edge bg-panel p-2 shadow-xl">
          <div className="mb-2">
            <div className="relative">
              <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-dim">
                <Icon name="search" size={13} />
              </span>
              <input
                autoFocus
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={t("searchFarmPlaceholder", "Search farm name or district…")}
                className="input-theme pl-8 py-1.5 text-xs"
              />
            </div>
          </div>

          <div className="max-h-72 overflow-y-auto space-y-2 pr-1">
            {grouped.length === 0 && (
              <p className="px-3 py-6 text-center text-xs text-dim">
                {farms.length === 0
                  ? t("noFarmsRegistered", "No farms created yet — draw on the map")
                  : t("noFarmsMatch", "No farms match your search")}
              </p>
            )}
            {grouped.map(([district, list]) => (
              <div key={district} className="space-y-1">
                <p className="flex items-center gap-1 px-2 text-[10px] font-medium uppercase tracking-wide text-dim">
                  <Icon name="mapPin" size={10} className="text-brand" />
                  {district} &middot; {list.length}
                </p>
                {list.map((f) => {
                  const active = selected?.id === f.id;
                  return (
                    <button
                      key={f.id}
                      onClick={() => {
                        onSelect(f);
                        setOpen(false);
                        setQuery("");
                      }}
                      className={`w-full rounded-lg px-2.5 py-2 text-left transition-colors ${active
                        ? "border border-brand/40 bg-brand/10 text-brand"
                        : "border border-transparent hover:bg-ink/[0.04] text-ink"
                        }`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="truncate text-xs font-medium">
                          {f.name}
                        </span>
                        {f.area_acres != null && (
                          <span className="shrink-0 rounded-md border border-edge bg-abyss px-1.5 py-0.5 text-[10px] tabular-nums text-mist">
                            {f.area_acres} ac
                          </span>
                        )}
                      </div>
                      <p className="mt-0.5 text-[10px] tabular-nums text-dim truncate">
                        {f.latitude != null && f.longitude != null
                          ? `${f.latitude.toFixed(4)}, ${f.longitude.toFixed(4)}`
                          : f.province}
                      </p>
                    </button>
                  );
                })}
              </div>
            ))}
          </div>

          <div className="mt-2 border-t border-edge pt-1.5 px-2 flex items-center justify-between text-[10px] text-dim">
            <span>{farms.length} {isUrdu ? "فارمز" : "farms"}</span>
            <span>{isUrdu ? "پنجاب، پاکستان" : "Punjab, PK"}</span>
          </div>
        </div>
      )}
    </div>
  );
}
