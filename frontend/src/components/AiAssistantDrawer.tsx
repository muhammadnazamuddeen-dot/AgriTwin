"use client";

import { useState } from "react";
import Icon from "@/components/Icon";
import { useLanguage } from "@/components/LanguageProvider";
import { api, type AskAiResponse } from "@/lib/api";

interface AiAssistantDrawerProps {
  farmId: number;
}

export default function AiAssistantDrawer({ farmId }: AiAssistantDrawerProps) {
  const { t, isUrdu } = useLanguage();
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AskAiResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const suggestedQuestions = isUrdu
    ? [
        "گندم نوں کدو پانی لایا جائے؟",
        "کیڑیاں (تیلہ / بیماری) دا کی علاج اے؟",
        "یوریا کھاد کدو تے کتنی پاؤ؟",
        "سیٹلائٹ ہریالی کیسی اے؟",
      ]
    : [
        "When should I irrigate my crop?",
        "Should I spray for pests or yellow rust?",
        "How to optimize my canal Warabandi water?",
        "What is the best fertilizer schedule?",
      ];

  const handleAsk = async (qText?: string) => {
    const targetQ = qText || question;
    if (!targetQ.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await api.askAiAdvisor(farmId, targetQ);
      setResponse(res);
      if (!qText) setQuestion("");
    } catch (err: any) {
      console.error("AI Ask error:", err);
      setError(err?.message || "Failed to get AI advisory response");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel p-5 relative overflow-hidden transition-all duration-300 hover:shadow-xl border-emerald-500/20">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-400 ring-1 ring-emerald-500/40 shadow-sm">
            <Icon name="bot" size={15} />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-ink flex items-center gap-2">
              {isUrdu ? "اگڑی ٹوئن اے آئی کسان رہنما" : "AgriTwin AI Precision Advisor"}
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-medium">
                Online
              </span>
            </h4>
            <p className="text-[11px] text-mist">
              {isUrdu
                ? "اپنی فصل، پانی، موسم یا کھاد بارے کوئی وی سوال پوچھو"
                : "Ask any agronomic question about irrigation, pests, weather or soil"}
            </p>
          </div>
        </div>
      </div>

      {/* Suggested Query Chips */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-2 mb-3 max-w-full">
        {suggestedQuestions.map((sq, idx) => (
          <button
            key={idx}
            onClick={() => {
              setQuestion(sq);
              handleAsk(sq);
            }}
            disabled={loading}
            className="px-2.5 py-1 text-xs rounded-lg bg-ink/5 hover:bg-emerald-500/10 text-mist hover:text-emerald-400 border border-ink/10 hover:border-emerald-500/30 transition-all whitespace-nowrap"
          >
            💬 {sq}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleAsk();
        }}
        className="flex items-center gap-2 mb-4"
      >
        <div className="relative flex-1">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder={
              isUrdu
                ? "مثلاً: گندم نوں کدو پانی لایا جائے؟"
                : "e.g. When should I irrigate my crop or spray for pests?"
            }
            disabled={loading}
            className="w-full rounded-xl bg-ink/5 border border-ink/15 px-3.5 py-2.5 text-xs text-ink placeholder:text-mist/60 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-white font-medium text-xs flex items-center gap-1.5 transition-all shadow-md"
        >
          {loading ? (
            <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              <span>{isUrdu ? "پوچھو" : "Ask AI"}</span>
              <Icon name="spark" size={13} />
            </>
          )}
        </button>
      </form>

      {/* Response Box */}
      {error && (
        <div className="rounded-xl bg-rose-500/10 border border-rose-500/20 p-3 text-xs text-rose-400">
          ⚠️ {error}
        </div>
      )}

      {response && (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-4 space-y-3 animate-fadeIn">
          <div className="flex items-center justify-between gap-2 pb-2 border-b border-ink/10">
            <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
              <Icon name="spark" size={12} />
              {isUrdu ? "تجویز کردہ اے آئی مشورہ" : "AI Agronomic Advisory"}
            </span>

            <div className="flex items-center gap-2">
              <span className="text-[11px] text-mist">
                Confidence: <strong className="text-emerald-400">{Math.round(response.confidence * 100)}%</strong>
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-ink/10 text-mist uppercase font-medium">
                {response.risk_level} Risk
              </span>
            </div>
          </div>

          {/* Urdu / Punjabi Advice */}
          {isUrdu && response.recommendation_ur && (
            <div className="rounded-lg bg-emerald-500/10 p-3 border border-emerald-500/20">
              <p className="text-sm font-medium text-emerald-300 leading-relaxed dir-rtl">
                {response.recommendation_ur}
              </p>
              {response.reasoning_ur && (
                <p className="text-xs text-mist/90 mt-1.5 leading-relaxed dir-rtl">
                  سبب: {response.reasoning_ur}
                </p>
              )}
            </div>
          )}

          {/* English Advice */}
          {(!isUrdu || !response.recommendation_ur) && (
            <div className="space-y-1">
              <p className="text-xs font-medium text-ink leading-relaxed">
                {response.recommendation}
              </p>
              <p className="text-[11px] text-mist leading-relaxed">
                Reasoning: {response.reasoning}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
