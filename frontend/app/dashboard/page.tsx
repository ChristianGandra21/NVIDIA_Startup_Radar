"use client";

import { useEffect, useState } from "react";
import Globe from "@/components/globe";
import { cn, formatNumber } from "@/lib/utils";
import { getStats, Stats } from "@/lib/api";
import Link from "next/link";

export default function DashboardHome() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      <Header />

      {error && (
        <div className="p-4 bg-red-50 border border-red-100 rounded-xl text-sm text-red-600">
          {error}
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-8 items-start">
        <GlobeSection />
        <KPIsSection stats={stats} loading={loading} />
      </div>

      <RecentSection stats={stats} loading={loading} />
    </div>
  );
}

function Header() {
  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">
          Bem-vindo ao NVIDIA Startup AI Radar
        </p>
      </div>
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-medium text-gray-600">
          U
        </div>
      </div>
    </div>
  );
}

function GlobeSection() {
  return (
    <div className="relative bg-white rounded-2xl border border-gray-200 card-shadow overflow-hidden">
      <div className="absolute top-4 left-4 z-10">
        <span className="inline-flex px-2 py-0.5 bg-nvidia/10 text-nvidia text-[10px] font-medium rounded-full">
          AO VIVO
        </span>
      </div>
      <div className="aspect-square w-full max-w-lg mx-auto">
        <Globe />
      </div>
      <div className="absolute bottom-4 left-4 right-4 text-center">
        <p className="text-xs text-gray-400">
          Ecossistema de startups brasileiras com IA
        </p>
      </div>
    </div>
  );
}

function KPIsSection({
  stats,
  loading,
}: {
  stats: Stats | null;
  loading: boolean;
}) {
  const cards = [
    {
      label: "Startups Mapeadas",
      value: stats ? formatNumber(stats.total_startups) : "—",
      sub: "Em todo o Brasil",
      color: "text-gray-900",
    },
    {
      label: "AI Native",
      value: stats ? formatNumber(stats.by_ai_label.ai_native) : "—",
      sub: "IA é o centro do produto",
      color: "text-nvidia",
    },
    {
      label: "AI Enabled",
      value: stats ? formatNumber(stats.by_ai_label.ai_enabled) : "—",
      sub: "IA como funcionalidade",
      color: "text-gray-700",
    },
    {
      label: "Classificadas",
      value: stats ? formatNumber(stats.classified) : "—",
      sub: `${stats ? formatNumber(stats.unclassified) : "—"} pendentes`,
      color: "text-gray-900",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className={cn(
            "p-5 bg-white rounded-xl border border-gray-200 card-shadow",
            loading && "animate-pulse"
          )}
        >
          <p className="text-xs text-gray-500 mb-1">{card.label}</p>
          <p className={cn("text-2xl font-semibold", card.color)}>{card.value}</p>
          <p className="text-[11px] text-gray-400 mt-0.5">{card.sub}</p>
        </div>
      ))}
    </div>
  );
}

function RecentSection({
  stats,
  loading,
}: {
  stats: Stats | null;
  loading: boolean;
}) {
  return (
    <div className="grid lg:grid-cols-2 gap-6">
      <div className="bg-white rounded-2xl border border-gray-200 card-shadow p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-sm font-semibold">Setores com mais startups</h2>
          <Link href="/dashboard/analytics" className="text-xs text-nvidia hover:underline">
            Ver todos
          </Link>
        </div>
        {loading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-8 bg-gray-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {stats?.top_sectors.slice(0, 6).map((s, i) => (
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

      <div className="bg-white rounded-2xl border border-gray-200 card-shadow p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-sm font-semibold">Tecnologias mais recomendadas</h2>
          <Link href="/dashboard/nvidia-base" className="text-xs text-nvidia hover:underline">
            Ver base
          </Link>
        </div>
        {loading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-8 bg-gray-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {stats?.top_recommended_technologies.map((t, i) => (
              <div
                key={t.nvidia_technology}
                className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-400 w-5">{i + 1}</span>
                  <span className="text-sm text-gray-700">{t.nvidia_technology}</span>
                </div>
                <span className="text-sm font-medium text-nvidia">
                  {formatNumber(t.count)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
