"use client";

import { useEffect, useState } from "react";
import { getStats, Stats } from "@/lib/api";
import { formatNumber } from "@/lib/utils";

export default function AnalyticsPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
          <p className="text-sm text-gray-500 mt-1">Carregando...</p>
        </div>
        <div className="grid sm:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-24 bg-white rounded-xl border border-gray-200 animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
        <p className="text-sm text-gray-400">Erro ao carregar dados.</p>
      </div>
    );
  }

  const classified = stats.classified;
  const unclassified = stats.unclassified;
  const total = stats.total_startups;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
        <p className="text-sm text-gray-500 mt-1">
          Visão geral do ecossistema de startups
        </p>
      </div>

      <div className="grid sm:grid-cols-3 gap-4">
        <div className="p-5 bg-white rounded-xl border border-gray-200 card-shadow">
          <p className="text-xs text-gray-500 mb-1">Classificadas</p>
          <p className="text-2xl font-semibold text-gray-900">
            {formatNumber(classified)}
          </p>
          <div className="mt-3 h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-nvidia rounded-full transition-all duration-500"
              style={{ width: `${total ? (classified / total) * 100 : 0}%` }}
            />
          </div>
          <p className="text-[11px] text-gray-400 mt-1.5">
            {total ? ((classified / total) * 100).toFixed(1) : 0}% do total
          </p>
        </div>

        <div className="p-5 bg-white rounded-xl border border-gray-200 card-shadow">
          <p className="text-xs text-gray-500 mb-1">AI Native</p>
          <p className="text-2xl font-semibold text-nvidia">
            {formatNumber(stats.by_ai_label.ai_native)}
          </p>
          <div className="mt-3 h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-nvidia rounded-full transition-all duration-500"
              style={{
                width: `${classified ? (stats.by_ai_label.ai_native / classified) * 100 : 0}%`,
              }}
            />
          </div>
          <p className="text-[11px] text-gray-400 mt-1.5">
            {classified ? ((stats.by_ai_label.ai_native / classified) * 100).toFixed(1) : 0}%
            das classificadas
          </p>
        </div>

        <div className="p-5 bg-white rounded-xl border border-gray-200 card-shadow">
          <p className="text-xs text-gray-500 mb-1">Pendentes</p>
          <p className="text-2xl font-semibold text-gray-900">
            {formatNumber(unclassified)}
          </p>
          <p className="text-[11px] text-gray-400 mt-1.5">
            Aguardando análise dos agentes
          </p>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl border border-gray-200 card-shadow p-6">
          <h2 className="text-sm font-semibold mb-5">Distribuição por Label</h2>
          {classified === 0 ? (
            <p className="text-sm text-gray-400">Nenhuma startup classificada ainda.</p>
          ) : (
            <div className="space-y-4">
              {([
                { label: "AI Native", value: stats.by_ai_label.ai_native, color: "bg-nvidia" },
                { label: "AI Enabled", value: stats.by_ai_label.ai_enabled, color: "bg-blue-500" },
                { label: "Non-AI", value: stats.by_ai_label.non_ai, color: "bg-gray-300" },
              ] as const).map((item) => (
                <div key={item.label}>
                  <div className="flex items-center justify-between text-sm mb-1.5">
                    <span className="text-gray-700">{item.label}</span>
                    <span className="font-medium text-gray-900">
                      {formatNumber(item.value)}
                    </span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${item.color} rounded-full transition-all duration-500`}
                      style={{
                        width: `${classified ? (item.value / classified) * 100 : 0}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 card-shadow p-6">
          <h2 className="text-sm font-semibold mb-5">Top Setores</h2>
          {stats.top_sectors.length === 0 ? (
            <p className="text-sm text-gray-400">Nenhum dado disponível.</p>
          ) : (
            <div className="space-y-2">
              {stats.top_sectors.slice(0, 8).map((s, i) => (
                <div
                  key={s.sector}
                  className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-400 w-5">{i + 1}</span>
                    <span className="text-sm text-gray-700">{s.sector}</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {formatNumber(s.count)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
