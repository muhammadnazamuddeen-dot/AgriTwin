"use client";

import Link from "next/link";
import Icon from "@/components/Icon";
import { useLanguage } from "@/components/LanguageProvider";

export default function Footer() {
  const { isUrdu } = useLanguage();

  const docsUrl =
    typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL
      ? process.env.NEXT_PUBLIC_API_URL.replace("/api/v1", "/docs")
      : "http://127.0.0.1:8000/docs";

  return (
    <footer className="border-t border-edge py-8 text-sm text-mist">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Brand & Mission */}
          <div className="flex flex-col sm:flex-row items-center gap-3 text-center sm:text-left">
            <Link href="/" className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand text-abyss">
                <Icon name="sprout" size={14} strokeWidth={2.2} />
              </span>
              <span className="text-sm font-semibold tracking-tight text-ink">
                Agri<span className="text-brand">Twin</span> AI
              </span>
            </Link>
            <span className="hidden sm:inline text-edge">|</span>
            <span className="text-xs">
              {isUrdu
                ? "پنجاب ڈیجیٹل ٹوئن زرعی پلیٹ فارم"
                : "Pakistan Precision Agriculture & Digital Twin Platform"}
            </span>
          </div>

          {/* Nav Links */}
          <div className="flex flex-wrap items-center justify-center gap-5 text-xs font-medium">
            <Link href="/" className="text-mist hover:text-brand transition-colors">
              {isUrdu ? "ڈیش بورڈ" : "Dashboard"}
            </Link>
            <Link href="/farms" className="text-mist hover:text-brand transition-colors">
              {isUrdu ? "فارمز" : "Farms"}
            </Link>
            <Link href="/about" className="text-mist hover:text-brand transition-colors">
              {isUrdu ? "پلیٹ فارم تعارف" : "About"}
            </Link>
            <a
              href={docsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-mist hover:text-brand transition-colors"
            >
              <span>{isUrdu ? "اے پی آئی دستاویزات" : "API Docs"}</span>
              <Icon name="externalLink" size={11} className="text-dim" />
            </a>
          </div>
        </div>

        {/* Bottom row */}
        <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-edge pt-5 text-xs text-dim">
          <span>
            {isUrdu ? "ڈیٹا ذرائع" : "Data"} · Open-Meteo · MODIS Terra · ISRIC SoilGrids · NASA POWER
          </span>
          <span>AgriTwin · MIT License</span>
        </div>
      </div>
    </footer>
  );
}
