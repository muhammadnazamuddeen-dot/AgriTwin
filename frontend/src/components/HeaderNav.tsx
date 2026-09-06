"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Icon from "@/components/Icon";
import { usePwaInstall } from "@/components/ServiceWorkerRegistration";

import ThemeToggle from "@/components/ThemeToggle";
import LanguageToggle from "@/components/LanguageToggle";
import { useLanguage } from "@/components/LanguageProvider";
import { api, type AuthUser } from "@/lib/api";

export default function HeaderNav() {
  const pathname = usePathname();
  const { t, isUrdu } = useLanguage();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { canInstall, installApp } = usePwaInstall();


  useEffect(() => {
    // Check API health
    api
      .healthCheck()
      .then((h) => setApiOnline(h.status === "ok"))
      .catch(() => setApiOnline(false));

    // Load auth user
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("agri_user");
      if (stored) {
        try {
          setUser(JSON.parse(stored));
        } catch {
          // ignore
        }
      }
    }
  }, []);

  const handleLogout = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("agri_token");
      localStorage.removeItem("agri_user");
      setUser(null);
      window.location.href = "/";
    }
  };

  const navLinks = [
    { href: "/", label: t("navDashboard", "Dashboard"), icon: "activity" as const },
    { href: "/farms", label: t("navFarmsHub", "Farms Hub"), icon: "wheat" as const },
    { href: "/about", label: t("navAbout", "About"), icon: "info" as const },
  ];

  return (
    <header className="sticky top-0 z-[2000] border-b border-edge bg-abyss/90 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6">
        {/* Brand */}
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand text-abyss">
              <Icon name="sprout" size={17} strokeWidth={2.2} />
            </span>
            <span className="text-[17px] font-semibold tracking-tight text-ink">
              Agri<span className="text-brand">Twin</span>
            </span>
          </Link>

          {/* Navigation links (Desktop) */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const isActive =
                link.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(link.href);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-ink/[0.06] text-ink"
                      : "text-mist hover:bg-ink/[0.04] hover:text-ink"
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}

            {/* FastAPI Docs External Link */}
            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-semibold text-mist transition-colors hover:bg-ink/6 hover:text-ink"
              title="Open Swagger REST API Docs (Backend :8000)"
            >
              <span>{t("navDocs", "API Docs")}</span>
              <Icon name="externalLink" size={11} className="text-dim" />
            </a>
          </nav>
        </div>

        {/* Right utilities: Status + Language + Theme + User */}
        <div className="flex items-center gap-2">
          {/* API status (Desktop) */}
          <div className="hidden lg:flex items-center gap-1.5 text-xs text-mist">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                apiOnline === true
                  ? "bg-emerald-500"
                  : apiOnline === false
                    ? "bg-rose-500"
                    : "bg-amber-400"
              }`}
            />
            <span>
              {apiOnline === true
                ? t("nodeLive", "Online")
                : apiOnline === false
                  ? "Offline"
                  : "Connecting…"}
            </span>
          </div>

          {/* Language Toggle (Desktop & Tablet) */}
          <div className="hidden sm:block">
            <LanguageToggle />
          </div>

          {/* Theme Toggle (Always visible) */}
          <ThemeToggle />


          {/* Install App (Desktop) */}
          {canInstall && (
            <button
              onClick={installApp}
              className="hidden lg:flex items-center gap-1.5 rounded-lg border border-edge px-2.5 py-1.5 text-xs font-medium text-mist hover:bg-ink/[0.04] hover:text-ink transition-colors"
              title="Install AgriTwin PWA"
            >
              <Icon name="download" size={12} />
              <span>{isUrdu ? "ایپ انسٹال" : "Install App"}</span>
            </button>
          )}

          {/* User Auth or Sign In (Desktop & Tablet) */}
          {user ? (
            <div className="hidden sm:flex items-center gap-2 rounded-lg border border-edge py-1 pl-1 pr-1.5">
              <span className="flex h-6 w-6 items-center justify-center rounded-md bg-brand/10 text-[11px] font-semibold text-brand">
                {user.name.charAt(0).toUpperCase()}
              </span>
              <span className="max-w-[120px] truncate text-xs font-medium text-ink">
                {user.name}
              </span>
              <span
                className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
                  user.role === "extension_officer"
                    ? "bg-sky-500/10 text-sky-600 dark:text-sky-400"
                    : "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                }`}
              >
                {user.role === "extension_officer" ? "Officer" : "Farmer"}
              </span>

              <button
                onClick={handleLogout}
                title="Sign out"
                className="flex h-6 w-6 items-center justify-center rounded-md text-mist hover:bg-rose-500/10 hover:text-rose-500 transition-colors"
              >
                <Icon name="logOut" size={13} />
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className="hidden sm:flex items-center gap-1.5 rounded-lg bg-brand px-3.5 py-1.5 text-sm font-medium text-abyss transition-colors hover:bg-brand-dark"
            >
              <span>{t("signIn", "Sign In")}</span>
            </Link>
          )}

          {/* Mobile menu toggle button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden flex h-8 w-8 items-center justify-center rounded-lg border border-edge text-mist hover:bg-ink/[0.04] hover:text-ink transition-colors"
            aria-label="Toggle navigation menu"
          >
            <Icon name={mobileMenuOpen ? "x" : "menu"} size={16} />
          </button>
        </div>
      </div>

      {/* Mobile dropdown drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-ink/8 bg-panel/95 backdrop-blur-2xl px-4 py-4 shadow-2xl space-y-4 animate-slide-down">
          {/* User Profile or Sign In Button on Mobile */}
          {user ? (
            <div className="flex items-center justify-between rounded-xl border border-edge bg-abyss p-3">
              <div className="flex items-center gap-2.5">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand/10 text-sm font-semibold text-brand">
                  {user.name.charAt(0).toUpperCase()}
                </div>

                <div className="min-w-0">
                  <div className="flex items-center gap-1.5">
                    <p className="truncate text-sm font-semibold text-ink">{user.name}</p>
                    <span
                      className={`rounded px-1.5 py-0.5 text-[9px] font-medium ${
                        user.role === "extension_officer"
                          ? "bg-sky-500/10 text-sky-600 dark:text-sky-400"
                          : "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                      }`}
                    >
                      {user.role === "extension_officer" ? "Officer" : "Farmer"}
                    </span>
                  </div>
                  <p className="truncate text-xs text-mist">{user.email || "Punjab Farmer"}</p>

                </div>
              </div>
              <button
                onClick={() => {
                  handleLogout();
                  setMobileMenuOpen(false);
                }}
                className="flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-medium text-rose-500 hover:bg-rose-500/10 transition-colors"
              >
                <Icon name="logOut" size={13} />
                <span>{t("signOut", "Sign Out")}</span>
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center justify-center gap-2 w-full rounded-lg bg-brand py-2.5 text-sm font-medium text-abyss active:opacity-90 transition-opacity"
            >
              <Icon name="user" size={14} strokeWidth={2.2} />
              <span>{t("signIn", "Sign In")}</span>
            </Link>
          )}


          {/* PWA Install Button inside Mobile Menu */}
          {canInstall && (
            <button
              onClick={() => {
                installApp();
                setMobileMenuOpen(false);
              }}
              className="flex w-full items-center justify-between rounded-xl border border-edge p-3 text-left transition-colors hover:bg-abyss"
            >
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand/10 text-brand shrink-0">
                  <Icon name="download" size={15} />
                </div>
                <div>
                  <p className="text-sm font-medium text-ink">
                    {isUrdu ? "ایگری ٹوئن ایپ انسٹال کرو" : "Install AgriTwin App"}
                  </p>
                  <p className="text-xs text-mist">
                    {isUrdu ? "ہوم اسکرین تے آف لائن رسائی" : "Add to home screen for offline access"}
                  </p>
                </div>
              </div>
              <span className="rounded-lg bg-brand px-2.5 py-1 text-xs font-medium text-abyss shrink-0">
                {isUrdu ? "انسٹال" : "Install"}
              </span>
            </button>
          )}


          {/* Navigation Links */}
          <nav className="flex flex-col gap-1">
            {navLinks.map((link) => {
              const isActive =
                link.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(link.href);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}

                  className={`flex items-center justify-between rounded-xl px-3.5 py-2.5 text-sm font-semibold transition-all ${isActive
                      ? "border border-brand/30 bg-brand/12 text-brand"
                      : "text-mist hover:bg-ink/5 hover:text-ink"
                    }`}

                >
                  <Icon
                    name={link.icon}
                    size={16}
                    className={isActive ? "text-brand" : "text-dim"}
                  />
                  <span>{link.label}</span>
                </Link>
              );
            })}

            {/* API Docs External Link (Mobile) */}
            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium text-mist hover:bg-ink/[0.04] hover:text-ink transition-colors"
            >
              <Icon name="externalLink" size={15} className="text-dim" />
              <span>API Docs</span>
            </a>
          </nav>


          {/* Mobile Footer: Language Selector + Node Status */}
          <div className="pt-3 border-t border-ink/8 flex items-center justify-between gap-2">
            <div className="flex items-center gap-1.5">
              <span className="relative flex h-2 w-2">
                <span
                  className={`relative inline-flex h-2 w-2 rounded-full ${apiOnline === true
                      ? "bg-emerald-400"
                      : apiOnline === false
                        ? "bg-rose-500"
                        : "bg-amber-400"
                    }`}
                />
              </span>
              <span className="text-[10px] font-mono text-mist">
                {apiOnline === true ? "Punjab Node Live" : "API Offline"}

              </span>
            </div>
            <div className="sm:hidden">
              <LanguageToggle />
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
