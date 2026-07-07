"use client";

import { useEffect, useState, useCallback } from "react";
import { getStartups, searchStartups, StartupListItem } from "@/lib/api";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { toast } from "sonner";

export default function StartupsPage() {
  const [startups, setStartups] = useState<StartupListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchMode, setSearchMode] = useState(false);
  const [searchResult, setSearchResult] = useState<{
    reason: string;
    total: number;
  } | null>(null);

  // Filter States
  const [selectedSector, setSelectedSector] = useState("");
  const [selectedAiLabel, setSelectedAiLabel] = useState("");
  const [selectedFunding, setSelectedFunding] = useState("");
  const [selectedState, setSelectedState] = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      if (searchQuery && searchMode) {
        const result = await searchStartups(searchQuery);
        setStartups(
          result.results.map((r) => ({
            id: r.id,
            name: r.name,
            sector: r.sector,
            funding_stage: r.funding_stage,
            state: r.state,
            ai_label: r.has_ai ? "ai_native" : null,
            ai_confidence: null,
            source_count: 0,
          }))
        );
        setTotal(result.total);
        setSearchResult({ reason: result.reason, total: result.total });
      } else {
        const data = await getStartups({
          page,
          page_size: 20,
          sector: selectedSector || undefined,
          ai_label: selectedAiLabel || undefined,
          funding: selectedFunding || undefined,
          state: selectedState || undefined,
        });
        setStartups(data.results);
        setTotal(data.count);
        setSearchResult(null);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [page, searchQuery, searchMode, selectedSector, selectedAiLabel, selectedFunding, selectedState]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      toast.warning("Digite um termo de pesquisa.");
      return;
    }
    setSearchMode(true);
    setPage(1);
    toast.promise(fetchData(), {
      loading: 'Pesquisando startups...',
      success: 'Busca concluída!',
      error: 'Erro ao realizar a busca.',
    });
  };

  const clearSearch = () => {
    setSearchQuery("");
    setSearchMode(false);
    setPage(1);
    toast.success("Pesquisa limpa.");
  };

  const handleFilterChange = (setter: (val: string) => void) => (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSearchMode(false);
    setSearchQuery("");
    setter(e.target.value);
    setPage(1);
  };

  const clearFilters = () => {
    setSelectedSector("");
    setSelectedAiLabel("");
    setSelectedFunding("");
    setSelectedState("");
    setPage(1);
    toast.success("Todos os filtros foram limpos.");
  };

  const totalPages = Math.ceil(total / 20);

  const aiBadge = (label: string | null) => {
    if (!label) return null;
    const colors: Record<string, string> = {
      ai_native: "bg-nvidia/10 text-nvidia",
      ai_enabled: "bg-blue-50 text-blue-600",
      non_ai: "bg-gray-100 text-gray-500",
    };
    const labels: Record<string, string> = {
      ai_native: "AI Native",
      ai_enabled: "AI Enabled",
      non_ai: "Non-AI",
    };
    return (
      <span
        className={cn(
          "inline-flex px-2 py-0.5 text-[10px] font-medium rounded-full",
          colors[label] || "bg-gray-100 text-gray-500"
        )}
      >
        {labels[label] || label}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Startups</h1>
        <p className="text-sm text-gray-500 mt-1">
          Explore as {total} startups brasileiras mapeadas
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="M21 21l-4.35-4.35" />
          </svg>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder='Buscar por linguagem natural — ex: "startups de IA em saúde"'
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-nvidia/20 focus:border-nvidia transition-all"
          />
        </div>
        <button
          type="submit"
          className="px-5 py-2.5 bg-nvidia hover:bg-nvidia-hover text-white text-sm font-medium rounded-xl transition-colors"
        >
          Buscar
        </button>
        {searchMode && (
          <button
            type="button"
            onClick={clearSearch}
            className="px-4 py-2.5 text-sm text-gray-500 hover:text-gray-700 rounded-xl border border-gray-200 hover:border-gray-300 transition-all"
          >
            Limpar
          </button>
        )}
      </form>

      <div className="bg-white p-4 rounded-2xl border border-gray-200 card-shadow space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs text-gray-500 font-semibold uppercase tracking-wider">
            Filtros do Banco de Dados
          </h3>
          {(selectedSector || selectedAiLabel || selectedFunding || selectedState) && (
            <button
              onClick={clearFilters}
              className="text-xs text-nvidia hover:underline font-medium cursor-pointer"
            >
              Limpar Filtros
            </button>
          )}
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-[11px] text-gray-400 font-medium mb-1">Setor</label>
            <select
              value={selectedSector}
              onChange={handleFilterChange(setSelectedSector)}
              className="w-full px-3 py-2 bg-gray-50 hover:bg-gray-100/50 border border-gray-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-nvidia/20 focus:border-nvidia transition-all cursor-pointer"
            >
              <option value="">Todos os setores</option>
              <option value="Tecnologia da Informação e Comunicação">TIC</option>
              <option value="Saúde">Saúde</option>
              <option value="Educação">Educação</option>
              <option value="Setor financeiro">Setor Financeiro</option>
              <option value="Agronegócio">Agronegócio</option>
              <option value="Fintech">Fintech</option>
              <option value="Outros serviços">Outros Serviços</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] text-gray-400 font-medium mb-1">Classificação IA</label>
            <select
              value={selectedAiLabel}
              onChange={handleFilterChange(setSelectedAiLabel)}
              className="w-full px-3 py-2 bg-gray-50 hover:bg-gray-100/50 border border-gray-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-nvidia/20 focus:border-nvidia transition-all cursor-pointer"
            >
              <option value="">Todas</option>
              <option value="ai_native">AI Native</option>
              <option value="ai_enabled">AI Enabled</option>
              <option value="non_ai">Non-AI</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] text-gray-400 font-medium mb-1">Estágio de Funding</label>
            <select
              value={selectedFunding}
              onChange={handleFilterChange(setSelectedFunding)}
              className="w-full px-3 py-2 bg-gray-50 hover:bg-gray-100/50 border border-gray-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-nvidia/20 focus:border-nvidia transition-all cursor-pointer"
            >
              <option value="">Todos</option>
              <option value="Seed">Seed</option>
              <option value="Série A">Série A</option>
              <option value="Série B">Série B</option>
              <option value="Série C">Série C</option>
              <option value="Bootstrapped">Bootstrapped</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] text-gray-400 font-medium mb-1">Estado</label>
            <select
              value={selectedState}
              onChange={handleFilterChange(setSelectedState)}
              className="w-full px-3 py-2 bg-gray-50 hover:bg-gray-100/50 border border-gray-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-nvidia/20 focus:border-nvidia transition-all cursor-pointer"
            >
              <option value="">Todos</option>
              <option value="SP">São Paulo (SP)</option>
              <option value="RJ">Rio de Janeiro (RJ)</option>
              <option value="MG">Minas Gerais (MG)</option>
              <option value="RS">Rio Grande do Sul (RS)</option>
              <option value="SC">Santa Catarina (SC)</option>
              <option value="PR">Paraná (PR)</option>
            </select>
          </div>
        </div>
      </div>

      {searchResult && (
        <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
          <p className="text-xs text-gray-500">
            <span className="font-medium text-gray-700">Estratégia:</span>{" "}
            {searchResult.reason}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            {searchResult.total} resultados encontrados
          </p>
        </div>
      )}

      <div className="bg-white rounded-2xl border border-gray-200 card-shadow overflow-hidden">
        {loading ? (
          <div className="p-8 space-y-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : startups.length === 0 ? (
          <div className="p-8 text-center text-sm text-gray-400">
            Nenhuma startup encontrada
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left text-[11px] text-gray-500 font-medium uppercase tracking-wider px-5 py-3">
                    Startup
                  </th>
                  <th className="text-left text-[11px] text-gray-500 font-medium uppercase tracking-wider px-5 py-3">
                    Setor
                  </th>
                  <th className="text-left text-[11px] text-gray-500 font-medium uppercase tracking-wider px-5 py-3">
                    Funding
                  </th>
                  <th className="text-left text-[11px] text-gray-500 font-medium uppercase tracking-wider px-5 py-3">
                    AI Label
                  </th>
                  <th className="text-right text-[11px] text-gray-500 font-medium uppercase tracking-wider px-5 py-3">
                    Fontes
                  </th>
                </tr>
              </thead>
              <tbody>
                {startups.map((s) => (
                  <tr
                    key={s.id}
                    className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors"
                  >
                    <td className="px-5 py-3.5">
                      <Link
                        href={`/dashboard/startups/${s.id}`}
                        className="text-sm font-medium text-gray-900 hover:text-nvidia transition-colors"
                      >
                        {s.name}
                      </Link>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-gray-500">
                      {s.sector || "—"}
                    </td>
                    <td className="px-5 py-3.5 text-sm text-gray-500">
                      {s.funding_stage || "—"}
                    </td>
                    <td className="px-5 py-3.5">{aiBadge(s.ai_label)}</td>
                    <td className="px-5 py-3.5 text-sm text-gray-500 text-right">
                      {s.source_count}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!searchMode && totalPages > 1 && (
          <div className="flex items-center justify-between px-5 py-3 border-t border-gray-100">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="px-3 py-1.5 text-xs text-gray-600 hover:text-gray-900 disabled:text-gray-300 disabled:cursor-not-allowed border border-gray-200 rounded-lg transition-colors"
            >
              Anterior
            </button>
            <span className="text-xs text-gray-400">
              Página {page} de {totalPages}
            </span>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              className="px-3 py-1.5 text-xs text-gray-600 hover:text-gray-900 disabled:text-gray-300 disabled:cursor-not-allowed border border-gray-200 rounded-lg transition-colors"
            >
              Próxima
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
