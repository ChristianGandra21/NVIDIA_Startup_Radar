"use client";

import { useEffect, useState } from "react";
import { getStartups, StartupListItem } from "@/lib/api";
import Link from "next/link";

export default function BriefingsPage() {
  const [classified, setClassified] = useState<StartupListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const aiNative = await getStartups({ ai_label: "ai_native", page_size: 50 });
        const aiEnabled = await getStartups({ ai_label: "ai_enabled", page_size: 50 });
        const nonAi = await getStartups({ ai_label: "non_ai", page_size: 50 });
        setClassified([...aiNative.results, ...aiEnabled.results, ...nonAi.results]);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Briefings</h1>
        <p className="text-sm text-gray-500 mt-1">
          Relatórios executivos gerados pelos agentes de IA
        </p>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-24 bg-white rounded-xl border border-gray-200 animate-pulse" />
          ))}
        </div>
      ) : classified.length === 0 ? (
        <div className="p-8 bg-white rounded-2xl border border-gray-200 card-shadow text-center">
          <p className="text-sm text-gray-400">
            Nenhum briefing disponível. Classifique startups primeiro.
          </p>
          <Link
            href="/dashboard/startups"
            className="inline-flex mt-4 px-4 py-2 text-sm text-nvidia border border-nvidia/30 rounded-lg hover:bg-nvidia/5 transition-colors"
          >
            Explorar startups
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {classified.map((s) => (
            <Link
              key={s.id}
              href={`/dashboard/startups/${s.id}`}
              className="p-5 bg-white rounded-xl border border-gray-200 card-shadow hover:card-shadow-hover transition-all duration-200 flex items-center justify-between"
            >
              <div>
                <h3 className="text-sm font-semibold text-gray-900">{s.name}</h3>
                <p className="text-xs text-gray-500 mt-0.5">{s.sector}</p>
              </div>
              <div className="flex items-center gap-3">
                {s.ai_label && (
                  <span className="inline-flex px-2 py-0.5 text-[10px] font-medium rounded-full bg-nvidia/10 text-nvidia">
                    {s.ai_label === "ai_native" ? "AI Native" : s.ai_label}
                  </span>
                )}
                <svg
                  className="w-4 h-4 text-gray-300"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M9 18l6-6-6-6" />
                </svg>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
