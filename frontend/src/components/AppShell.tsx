"use client";

import { useState, type ReactNode } from "react";
import Sidebar from "@/components/Sidebar";
import TopHeader from "@/components/TopHeader";
import Footer from "@/components/Footer";
import OfflineBanner from "@/components/OfflineBanner";
import ServiceWorkerRegistration from "@/components/ServiceWorkerRegistration";

export default function AppShell({ children }: { children: ReactNode }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex min-h-screen w-full bg-abyss text-ink">
      {/* Offline Connectivity Status Banner */}
      <OfflineBanner />

      {/* Left Navigation Sidebar */}
      <Sidebar
        mobileOpen={mobileMenuOpen}
        onCloseMobile={() => setMobileMenuOpen(false)}
      />

      {/* Main Content Viewport */}
      <div className="flex flex-1 flex-col min-w-0 overflow-x-hidden">
        {/* Top App Bar Header */}
        <TopHeader onOpenMobileMenu={() => setMobileMenuOpen(true)} />

        {/* Page Content Body */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 space-y-6 max-w-[1600px] w-full mx-auto">
          {children}
        </main>

        {/* Global Footer */}
        <Footer />
      </div>

      {/* PWA Registration */}
      <ServiceWorkerRegistration />
    </div>
  );
}
