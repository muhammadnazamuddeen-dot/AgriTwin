"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Icon, { type IconName } from "@/components/Icon";
import { useLanguage } from "@/components/LanguageProvider";
import { useTheme } from "@/components/ThemeProvider";
import { useAuth } from "@/components/AuthProvider";

interface SidebarProps {
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export default function Sidebar({ mobileOpen = false, onCloseMobile }: SidebarProps) {
  const pathname = usePathname();
  const { t, isUrdu } = useLanguage();
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuth();
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [activeHash, setActiveHash] = useState<string>("");

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  const navItems: { href: string; label: string; icon: IconName }[] = [
    { href: "/", label: isUrdu ? "ڈیش بورڈ" : "Dashboard", icon: "grid" },
    { href: "/farms", label: isUrdu ? "فارمز" : "Farms", icon: "wheat" },
    { href: "#crop-advisor", label: isUrdu ? "کراپ ایڈوائزر" : "Crop Advisor", icon: "sprout" },
    { href: "#market-trends", label: isUrdu ? "مارکیٹ رجحانات" : "Market Trends", icon: "trendUp" },
    { href: "#weather", label: isUrdu ? "موسم" : "Weather", icon: "cloudSun" },
    { href: "#alerts", label: isUrdu ? "الرٹس" : "Alerts", icon: "bell" },
    { href: "#reports", label: isUrdu ? "رپورٹس" : "Reports", icon: "fileText" },
    { href: "#settings", label: isUrdu ? "سیٹنگز" : "Settings", icon: "settings" },
  ];

  // Sync hash on mount and pathname change
  useEffect(() => {
    if (typeof window !== "undefined") {
      setActiveHash(window.location.hash);
    }
  }, [pathname]);

  // Real-time active section tracking on scroll when on the dashboard
  useEffect(() => {
    if (pathname !== "/" || typeof window === "undefined") return;

    const sections = navItems
      .filter((item) => item.href.startsWith("#"))
      .map((item) => item.href.slice(1));

    const handleScroll = () => {
      if (window.scrollY < 180) {
        setActiveHash("");
        return;
      }

      let currentSection = "";
      for (const sectionId of sections) {
        const el = document.getElementById(sectionId);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.top <= 240 && rect.bottom >= 100) {
            currentSection = `#${sectionId}`;
            break;
          }
        }
      }
      if (currentSection) {
        setActiveHash(currentSection);
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();

    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [pathname]);

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    if (onCloseMobile) onCloseMobile();

    if (href.startsWith("#")) {
      const targetId = href.slice(1);
      if (pathname === "/") {
        e.preventDefault();
        setActiveHash(href);
        if (typeof window !== "undefined") {
          window.history.pushState(null, "", href);
        }
        const targetEl = document.getElementById(targetId);
        if (targetEl) {
          targetEl.scrollIntoView({ behavior: "smooth" });
        }
      }
    } else if (href === "/") {
      if (pathname === "/") {
        e.preventDefault();
        setActiveHash("");
        if (typeof window !== "undefined") {
          window.scrollTo({ top: 0, behavior: "smooth" });
          window.history.pushState(null, "", "/");
        }
      }
    }
  };

  const sidebarContent = (
    <div className="flex h-full flex-col justify-between p-4 bg-panel border-edge ltr:border-r rtl:border-l select-none">
      {/* Top Brand & Navigation Section */}
      <div className="space-y-6">
        {/* Brand Header */}
        <div className="flex items-center justify-between px-2 pt-1">
          <Link href="/" className="flex items-center gap-2.5">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand text-white shadow-sm">
              <Icon name="sprout" size={20} strokeWidth={2.2} />
            </span>
            <span className="text-lg font-bold tracking-tight text-ink">
              Agri<span className="text-brand">Twin AI</span>
            </span>
          </Link>
          {onCloseMobile && (
            <button
              onClick={onCloseMobile}
              className="lg:hidden flex h-8 w-8 items-center justify-center rounded-lg text-mist hover:bg-ink/5"
            >
              <Icon name="x" size={18} />
            </button>
          )}
        </div>

        {/* Navigation Menu Links */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const isHashItem = item.href.startsWith("#");
            const targetHref = isHashItem && pathname !== "/" ? `/${item.href}` : item.href;

            const isActive = isHashItem
              ? pathname === "/" && activeHash === item.href
              : item.href === "/"
              ? pathname === "/" && !activeHash
              : pathname.startsWith(item.href);

            return (
              <Link
                key={item.label}
                href={targetHref}
                onClick={(e: React.MouseEvent<HTMLAnchorElement>) => handleNavClick(e, item.href)}
                className={`group flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition-all ${
                  isActive
                    ? "bg-brand text-white shadow-md font-semibold"
                    : "text-mist hover:bg-ink/[0.04] dark:hover:bg-ink/10 hover:text-ink"
                }`}
              >
                <Icon
                  name={item.icon}
                  size={18}
                  className={isActive ? "text-white" : "text-dim group-hover:text-ink transition-colors"}
                />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Bottom Controls: Theme Toggle & User Account Card */}
      <div className="space-y-3 pt-4 border-t border-edge">
        {/* Dark Mode / Light Mode Toggle Pill Switch */}
        <div className="flex items-center justify-between rounded-xl border border-edge bg-abyss p-2.5">
          <div className="flex items-center gap-2 text-xs font-medium text-mist">
            <Icon name={theme === "dark" ? "moon" : "sun"} size={15} className="text-brand" />
            <span>{theme === "dark" ? (isUrdu ? "ڈارک موڈ" : "Dark Mode") : (isUrdu ? "لائٹ موڈ" : "Light Mode")}</span>
          </div>

          <button
            onClick={toggleTheme}
            type="button"
            role="switch"
            dir="ltr"
            aria-checked={theme === "dark"}
            aria-label="Toggle color theme"
            className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
              theme === "dark" ? "bg-brand" : "bg-edge"
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                theme === "dark" ? "translate-x-5" : "translate-x-0"
              }`}
            />
          </button>
        </div>

        {/* User Account Profile Card with Dropdown Menu */}
        <div className="relative">
          <button
            onClick={() => setUserDropdownOpen(!userDropdownOpen)}
            type="button"
            className="flex w-full items-center justify-between rounded-xl border border-edge bg-panel p-2.5 transition-colors hover:bg-abyss text-left"
          >
            <div className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand/15 text-brand text-xs font-bold shrink-0">
                {user?.name ? user.name.charAt(0).toUpperCase() : "F"}
              </div>
              <div className="min-w-0">
                <p className="truncate text-xs font-semibold text-ink">{user?.name || "Farmer"}</p>
                <p className="truncate text-[10px] text-dim">{user?.email || "Gujrat, Punjab"}</p>
              </div>
            </div>
            <Icon
              name="chevronDown"
              size={14}
              className={`text-dim shrink-0 transition-transform duration-200 ${
                userDropdownOpen ? "rotate-180" : ""
              }`}
            />
          </button>

          {/* Account Popover Menu */}
          {userDropdownOpen && (
            <div className="absolute bottom-full left-0 right-0 mb-2 rounded-xl border border-edge bg-panel p-1.5 shadow-xl animate-slide-down z-50 space-y-1">
              <div className="px-3 py-2 border-b border-edge">
                <p className="text-xs font-semibold text-ink">{user?.name || "Punjab Farmer"}</p>
                <p className="text-[10px] text-mist capitalize">
                  {user?.role === "extension_officer" ? (isUrdu ? "زرعی افسر" : "Extension Officer") : (isUrdu ? "کسان" : "Farmer")}
                </p>
              </div>
              {user && (
                <button
                  onClick={async () => {
                    setUserDropdownOpen(false);
                    await logout();
                  }}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium text-rose-500 hover:bg-rose-500/10 transition-colors"
                >
                  <Icon name="logOut" size={14} />
                  <span>{isUrdu ? "لاگ آؤٹ" : "Sign Out"}</span>
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar (Fixed) */}
      <aside className="hidden lg:block w-64 shrink-0 h-screen sticky top-0 z-40">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer (Overlay) */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
            onClick={onCloseMobile}
          />
          <div className="fixed inset-y-0 ltr:left-0 rtl:right-0 w-72 max-w-full shadow-2xl animate-slide-down">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
}
