"use client";

import Icon, { type IconName } from "@/components/Icon";
import { useLanguage } from "@/components/LanguageProvider";

interface AlertItem {
  id: number;
  title: string;
  description: string;
  time: string;
  type: string;
  icon: IconName;
}

interface UpcomingAlertsCardProps {
  items?: AlertItem[];
}

export default function UpcomingAlertsCard({ items }: UpcomingAlertsCardProps) {
  const { isUrdu } = useLanguage();

  const defaultAlerts: AlertItem[] = [
    {
      id: 1,
      title: isUrdu ? "درجہ حرارت وچ اضافے دا الرٹ" : "High Temperature Alert",
      description: isUrdu ? "شدید گرمی فصل دی صحت نوں متاثر کر سکدی اے۔" : "High temperature may affect crop health.",
      time: "3 Jun - 5 Jun",
      type: "amber",
      icon: "alert" as const,
    },
    {
      id: 2,
      title: isUrdu ? "بارش دیاں کم توقعات" : "Low Rainfall Expected",
      description: isUrdu ? "آبپاشی دا شیڈول ترتیب دیو۔" : "Consider irrigation scheduling.",
      time: isUrdu ? "اگلے 7 دن" : "Next 7 Days",
      type: "blue",
      icon: "droplet" as const,
    },
    {
      id: 3,
      title: isUrdu ? "مکئی دا نشوونما مرحلہ" : "Maize Growth Stage",
      description: isUrdu ? "تہاڈی فصل ویجیٹیٹو مرحلے وچ اے۔" : "Your crop is in vegetative stage.",
      time: isUrdu ? "ویجیٹیٹو مرحلہ" : "Vegetative Stage",
      type: "green",
      icon: "sprout" as const,
    },
  ];

  const alerts = items && items.length > 0 ? items : defaultAlerts;

  return (
    <div className="glass-panel p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-semibold text-mist uppercase tracking-wider">
          {isUrdu ? "آئندہ الرٹس" : "Upcoming Alerts"}
        </h3>
        <button className="text-xs font-semibold text-brand hover:underline">
          {isUrdu ? "سب دیکھو" : "View All"}
        </button>
      </div>

      {/* Alert items list */}
      <div className="space-y-3.5">
        {alerts.map((item) => (
          <div key={item.id} className="flex items-start justify-between gap-3 text-xs">
            <div className="flex items-start gap-3">
              <span
                className={`flex h-8 w-8 items-center justify-center rounded-xl shrink-0 mt-0.5 ${
                  item.type === "amber"
                    ? "bg-amber-500/15 text-amber-500"
                    : item.type === "blue"
                    ? "bg-sky-500/15 text-sky-500"
                    : "bg-emerald-500/15 text-emerald-500"
                }`}
              >
                <Icon name={item.icon} size={16} />
              </span>
              <div>
                <p className="font-semibold text-ink">{item.title}</p>
                <p className="text-mist text-[11px] mt-0.5 leading-snug">{item.description}</p>
              </div>
            </div>

            <span className="text-[10px] font-medium text-dim whitespace-nowrap shrink-0">
              {item.time}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
