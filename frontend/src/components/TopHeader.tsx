"use client";

import { useAuth } from "@/components/AuthProvider";
import { useLanguage } from "@/components/LanguageProvider";
import Icon from "@/components/Icon";
import LanguageToggle from "@/components/LanguageToggle";

interface TopHeaderProps {
  onOpenMobileMenu?: () => void;
}

export default function TopHeader({ onOpenMobileMenu }: TopHeaderProps) {
  const { user } = useAuth();
  const { isUrdu } = useLanguage();

  // Formatted current date (e.g., "2 June 2025" or current local date)
  const currentDate = new Date().toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-edge bg-abyss/80 px-4 sm:px-8 backdrop-blur-md">
      {/* Mobile Toggle & Greeting */}
      <div className="flex items-center gap-3">
        {onOpenMobileMenu && (
          <button
            onClick={onOpenMobileMenu}
            className="lg:hidden flex h-9 w-9 items-center justify-center rounded-xl border border-edge bg-panel text-mist hover:text-ink"
            aria-label="Open sidebar menu"
          >
            <Icon name="menu" size={18} />
          </button>
        )}

        <div>
          <h1 className="text-lg sm:text-xl font-bold tracking-tight text-ink flex items-center gap-2">
            <span>
              {isUrdu
                ? `جی آیاں نوں، ${user?.name || "فارمر"} 👋`
                : `Welcome back, ${user?.name || "Farmer"} 👋`}
            </span>
          </h1>
          <p className="hidden sm:block text-xs text-mist mt-0.5">
            {isUrdu
              ? "تہاڈے فارمز دی اج دی تازہ ترین صورتحال"
              : "Here's what's happening with your farms today."}
          </p>
        </div>
      </div>

      {/* Right Utilities: Date + Language + Bell + Profile Avatar */}
      <div className="flex items-center gap-3 sm:gap-4">
        {/* Language selector */}
        <LanguageToggle />

        {/* Date Display Badge */}
        <div className="hidden sm:block text-xs font-medium text-mist">
          {currentDate}
        </div>

        {/* Notification Bell with alert indicator */}
        <button
          type="button"
          aria-label="Notifications"
          className="relative flex h-9 w-9 items-center justify-center rounded-xl border border-edge bg-panel text-mist hover:text-ink hover:bg-abyss transition-colors"
        >
          <Icon name="bell" size={17} />
          <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-rose-500 ring-2 ring-panel" />
        </button>

        {/* User Circle Avatar */}
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand text-white font-bold text-sm shadow-sm shrink-0">
          {user?.name ? user.name.charAt(0).toUpperCase() : "F"}
        </div>
      </div>
    </header>
  );
}
