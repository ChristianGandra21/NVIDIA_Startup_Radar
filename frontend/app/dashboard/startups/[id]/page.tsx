"use client";

import { useEffect, useState, use } from "react";
import { getStartup, analyzeStartup, StartupDetail } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import Link from "next/link";
import { toast } from "sonner";

export default function StartupDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [startup, setStartup] = useState<StartupDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      const data = await getStartup(Number(id));
      setStartup(data);
    } catch (e) {
      setError("Startup não encontrada");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [id]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    toast.info("Iniciando análise com agentes de IA...");
    try {
      await analyzeStartup(Number(id));
      await load();
      toast.success("Análise concluída com sucesso!");
    } catch (e) {
      setError("Erro ao analisar startup");
      toast.error("Erro ao analisar startup com IA");
    } finally {
      setAnalyzing(false);
    }
  };

  const [copied, setCopied] = useState(false);

  const handleCopyBriefing = () => {
    if (!startup?.briefings?.[0]) return;
    navigator.clipboard.writeText(startup.briefings[0].briefing_text);
    setCopied(true);
    toast.success("Briefing copiado para a área de transferência!");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadBriefing = () => {
    if (!startup?.briefings?.[0]) return;
    const element = document.createElement("a");
    const file = new Blob([startup.briefings[0].briefing_text], {type: 'text/markdown'});
    element.href = URL.createObjectURL(file);
    element.download = `Briefing_${startup.name.replace(/\s+/g, '_')}.md`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    toast.success("Briefing exportado com sucesso (.md)!");
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 bg-gray-100 rounded-lg animate-pulse" />
        <div className="h-4 w-96 bg-gray-100 rounded-lg animate-pulse" />
        <div className="grid lg:grid-cols-2 gap-6 mt-8">
          <div className="h-64 bg-white rounded-2xl border border-gray-200 animate-pulse" />
          <div className="h-64 bg-white rounded-2xl border border-gray-200 animate-pulse" />
        </div>
      </div>
    );
  }

  if (error || !startup) {
    return (
      <div className="p-8 bg-white rounded-2xl border border-gray-200 card-shadow text-center">
        <p className="text-sm text-gray-400">{error || "Startup não encontrada"}</p>
        <Link
          href="/dashboard/startups"
          className="inline-flex mt-4 px-4 py-2 text-sm text-nvidia border border-nvidia/30 rounded-lg hover:bg-nvidia/5 transition-colors"
        >
          Voltar
        </Link>
      </div>
    );
  }

  const latestClassification = startup.classifications?.[0];
  const latestValidation = startup.validations?.[0];
  const latestBriefing = startup.briefings?.[0];

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard/startups"
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 12H5M12 19l-7-7 7-7" />
              </svg>
            </Link>
            <h1 className="text-2xl font-semibold tracking-tight">{startup.name}</h1>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            {startup.sector || "Setor não informado"}
            {startup.state ? ` — ${startup.state}` : ""}
          </p>
        </div>
        <button
          onClick={handleAnalyze}
          disabled={analyzing}
          className="px-5 py-2.5 bg-nvidia hover:bg-nvidia-hover disabled:bg-gray-300 text-white text-sm font-medium rounded-xl transition-all disabled:cursor-not-allowed"
        >
          {analyzing ? "Analisando..." : "Analisar com IA"}
        </button>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {startup.description && (
            <div className="bg-white rounded-2xl border border-gray-200 card-shadow p-6">
              <h2 className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-3">
                Descrição
              </h2>
              <p className="text-sm text-gray-700 leading-relaxed">{startup.description}</p>
            </div>
          )}

          {latestBriefing && (
            <div className="bg-white rounded-2xl border border-gray-200 card-shadow p-6">
              <div className="flex items-center justify-between mb-4 border-b border-gray-100 pb-3">
                <h2 className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                  Briefing Executivo
                </h2>
                <div className="flex gap-2">
                  <button
                    onClick={handleCopyBriefing}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 hover:text-nvidia hover:bg-nvidia/5 border border-gray-200 hover:border-nvidia/30 rounded-lg transition-all"
                  >
                    {copied ? (
                      <>
                        <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                        Copiado!
                      </>
                    ) : (
                      <>
                        <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                        </svg>
                        Copiar
                      </>
                    )}
                  </button>
                  <button
                    onClick={handleDownloadBriefing}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 hover:text-nvidia hover:bg-nvidia/5 border border-gray-200 hover:border-nvidia/30 rounded-lg transition-all"
                  >
                    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                      <polyline points="7 10 12 15 17 10" />
                      <line x1="12" y1="15" x2="12" y2="3" />
                    </svg>
                    Exportar MD
                  </button>
                </div>
              </div>
              <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
                {latestBriefing.briefing_text}
              </div>
              {latestBriefing.created_at && (
                <p className="text-xs text-gray-400 mt-3 border-t border-gray-50 pt-2 text-right">
                  Gerado em {formatDate(latestBriefing.created_at)}
                </p>
              )}
            </div>
          )}

          {startup.recommendations.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-200 card-shadow p-6">
              <h2 className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-4">
                Recomendações NVIDIA ({startup.recommendations.length})
              </h2>
              <div className="space-y-3">
                {startup.recommendations.map((rec) => (
                  <div
                    key={rec.id}
                    className="p-4 bg-gray-50 rounded-xl border border-gray-100"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-nvidia" />
                        <span className="text-sm font-semibold">
                          {rec.nvidia_technology}
                        </span>
                      </div>
                      <span
                        className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${
                          rec.priority === "high"
                            ? "bg-nvidia/10 text-nvidia"
                            : rec.priority === "medium"
                            ? "bg-blue-50 text-blue-600"
                            : "bg-gray-100 text-gray-500"
                        }`}
                      >
                        {rec.priority}
                      </span>
                    </div>
                    {rec.technical_justification && (
                      <p className="text-xs text-gray-500 mt-1">
                        {rec.technical_justification}
                      </p>
                    )}
                    {rec.suggested_next_action && (
                      <p className="text-xs text-gray-400 mt-2 italic">
                        Ação: {rec.suggested_next_action}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-gray-200 card-shadow p-5">
            <h2 className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-4">
              Informações
            </h2>
            <InfoRow label="Website" value={startup.website} href={startup.website} />
            <InfoRow
              label="Founders"
              value={startup.founders || "Não informado"}
            />
            <InfoRow
              label="Funding Stage"
              value={startup.funding_stage || "Não informado"}
            />
            <InfoRow
              label="Employee Count"
              value={startup.employee_count_estimate || "Não informado"}
            />
            <InfoRow label="Business Area" value={startup.business_area || "Não informado"} />
            <InfoRow label="Program" value={startup.program || "Não informado"} />
            <InfoRow
              label="Cohort"
              value={
                startup.cohort_year
                  ? `${startup.cohort_year}${startup.cohort_cycle ? ` / ${startup.cohort_cycle}` : ""}`
                  : "Não informado"
              }
            />
          </div>

          {latestClassification && (
            <div className="bg-white rounded-2xl border border-gray-200 card-shadow p-5">
              <h2 className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-4">
                Classificação IA
              </h2>
              <div className="flex items-center gap-2 mb-2">
                <div
                  className={`w-2.5 h-2.5 rounded-full ${
                    latestClassification.label === "ai_native"
                      ? "bg-nvidia"
                      : latestClassification.label === "ai_enabled"
                      ? "bg-blue-500"
                      : "bg-gray-400"
                  }`}
                />
                <span className="text-sm font-semibold capitalize">
                  {latestClassification.label === "ai_native"
                    ? "AI Native"
                    : latestClassification.label === "ai_enabled"
                    ? "AI Enabled"
                    : "Non-AI"}
                </span>
                {latestClassification.confidence && (
                  <span className="text-xs text-gray-400">
                    ({Math.round(latestClassification.confidence * 100)}%)
                  </span>
                )}
              </div>
              {latestClassification.justification && (
                <p className="text-xs text-gray-500 mt-2 leading-relaxed">
                  {latestClassification.justification}
                </p>
              )}
            </div>
          )}

          {latestValidation && (
            <div className="bg-white rounded-2xl border border-gray-200 card-shadow p-5">
              <h2 className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-3">
                Validação
              </h2>
              <div className="flex items-center gap-2 mb-2">
                <div
                  className={`w-2 h-2 rounded-full ${
                    latestValidation.is_valid ? "bg-nvidia" : "bg-yellow-500"
                  }`}
                />
                <span className="text-sm font-medium">
                  {latestValidation.is_valid ? "Válida" : "Requer atenção"}
                </span>
              </div>
              {latestValidation.issues && latestValidation.issues !== "[]" && (
                <div className="mt-2">
                  <p className="text-[11px] text-gray-500 font-medium mb-1">
                    Issues ({startup.validations?.length || 0})
                  </p>
                  <ul className="space-y-1">
                    {(startup.validations || []).slice(0, 3).map((v) => (
                      <li
                        key={v.id}
                        className="text-[11px] text-gray-400 flex items-start gap-1.5"
                      >
                        <span className="text-yellow-500 mt-0.5 shrink-0">•</span>
                        <span>{v.issues || "Sem detalhes"}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {startup.sources.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-200 card-shadow p-5">
              <h2 className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-3">
                Fontes ({startup.sources.length})
              </h2>
              <div className="space-y-2">
                {startup.sources.slice(0, 5).map((src) => (
                  <div key={src.id}>
                    <a
                      href={src.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-nvidia hover:underline block truncate"
                    >
                      {src.url}
                    </a>
                    <p className="text-[10px] text-gray-400">
                      {src.extraction_method}
                      {src.fetched_at ? ` · ${formatDate(src.fetched_at)}` : ""}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function InfoRow({
  label,
  value,
  href,
}: {
  label: string;
  value: string | null;
  href?: string | null;
}) {
  if (!value) return null;
  return (
    <div className="py-2 border-b border-gray-100 last:border-0">
      <p className="text-[11px] text-gray-400">{label}</p>
      {href ? (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-nvidia hover:underline truncate block"
        >
          {value}
        </a>
      ) : (
        <p className="text-sm text-gray-700 truncate">{value}</p>
      )}
    </div>
  );
}
