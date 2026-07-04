"use client";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Configurações</h1>
        <p className="text-sm text-gray-500 mt-1">
          Preferências da plataforma
        </p>
      </div>

      <div className="max-w-xl space-y-4">
        <div className="bg-white rounded-2xl border border-gray-200 card-shadow p-6">
          <h2 className="text-sm font-semibold mb-4">Conexão com API</h2>
          <div className="space-y-3">
            <div>
              <label className="text-xs text-gray-500 font-medium mb-1 block">
                API URL
              </label>
              <input
                type="text"
                defaultValue="/api/v1 (proxy Next.js → Django)"
                readOnly
                className="w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg text-gray-500 cursor-not-allowed"
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 card-shadow p-6">
          <h2 className="text-sm font-semibold mb-4">Sobre</h2>
          <div className="text-sm text-gray-500 leading-relaxed space-y-2">
            <p>
              <strong className="text-gray-700">NVIDIA Startup AI Radar</strong> v1.0
            </p>
            <p>
              Plataforma de inteligência para identificação e análise de startups
              brasileiras com maturidade em IA.
            </p>
            <p>
              Construído com Next.js, Django, LangGraph e ChromaDB.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
