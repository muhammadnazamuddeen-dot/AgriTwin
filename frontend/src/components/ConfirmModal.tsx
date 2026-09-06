"use client";

import React from "react";
import Icon from "./Icon";

interface ConfirmModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isDestructive?: boolean;
  loading?: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

export default function ConfirmModal({
  isOpen,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  isDestructive = true,
  loading = false,
  onConfirm,
  onClose,
}: ConfirmModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 p-4 animate-in fade-in duration-200">
      <div
        className={`relative w-full max-w-md rounded-xl border p-5 sm:p-6 shadow-xl animate-in zoom-in-95 duration-200 ${isDestructive
            ? "border-rose-500/25 bg-panel text-ink"
            : "border-edge bg-panel text-ink"
          }`}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          disabled={loading}
          className="absolute right-4 top-4 flex h-7 w-7 items-center justify-center rounded-lg text-dim hover:bg-ink/10 hover:text-ink transition-colors"
        >
          <Icon name="x" size={14} />
        </button>

        {/* Icon Badge */}
        <div
          className={`mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl ${isDestructive
              ? "bg-rose-500/10 text-rose-600 dark:text-rose-400 ring-1 ring-rose-500/20"
              : "bg-brand/10 text-brand ring-1 ring-brand/20"
            }`}
        >
          <Icon name={isDestructive ? "trash" : "activity"} size={22} />
        </div>

        {/* Header Content */}
        <div className="text-center">
          <h3 className="text-base font-semibold text-ink">{title}</h3>
          <p className="mt-2 text-xs text-mist leading-relaxed">{message}</p>
        </div>

        {/* Action Buttons */}
        <div className="mt-6 flex flex-col-reverse sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="flex-1 rounded-lg border border-edge px-4 py-2.5 text-xs font-medium text-mist hover:bg-ink/[0.04] hover:text-ink transition-colors disabled:opacity-50 text-center"
          >
            {cancelText}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className={`flex-1 flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-xs font-medium transition-colors disabled:opacity-50 text-center ${isDestructive
                ? "bg-rose-600 text-white hover:bg-rose-700"
                : "bg-brand text-abyss hover:bg-brand-dark"
              }`}
          >
            {loading && <span className="h-3 w-3 rounded-full border-2 border-current border-r-transparent animate-spin shrink-0" />}
            <span className="whitespace-nowrap">{loading ? "Deleting…" : confirmText}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
