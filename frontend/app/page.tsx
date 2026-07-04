"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import Navbar from "@/components/navbar";
import Globe from "@/components/globe";
import Hero from "@/components/ui/demo";

export default function LandingPage() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <HowItWorks />
        <Architecture />
        <Technologies />
        <About />
        <Footer />
      </main>
    </>
  );
}

// Local Hero function removed. Using imported Hero from components/ui/demo.

function HowItWorks() {
  const steps = [
    {
      number: "01",
      title: "Coleta Multifonte",
      description: "Agentes de scraping inteligentes coletam dados de 16+ fontes: APIs, diretórios de startups, portais de inovação e blogs de tecnologia.",
      icon: (
        <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
        </svg>
      ),
    },
    {
      number: "02",
      title: "Classificação por IA",
      description: "Classifier Agent avalia maturidade em IA: startups são rotuladas como AI Native, AI Enabled ou Non-AI com alto índice de confiança.",
      icon: (
        <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 002 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" />
          <path d="M12 22V12" />
        </svg>
      ),
    },
    {
      number: "03",
      title: "Validação de Evidências",
      description: "Validator Agent cruza múltiplas fontes para verificar claims, detectar conflitos e avaliar a qualidade dos dados coletados.",
      icon: (
        <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
          <path d="M22 4L12 14.01l-3-3" />
        </svg>
      ),
    },
    {
      number: "04",
      title: "Recomendação NVIDIA",
      description: "RAG Agent consulta base vetorial de documentações NVIDIA + Recommender Agent sugere tecnologias específicas com casos de uso concretos.",
      icon: (
        <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 6v6l4 2" />
        </svg>
      ),
    },
    {
      number: "05",
      title: "Briefing Executivo",
      description: "Briefer Agent gera relatórios completos para o time NVIDIA: resumo, justificativas técnicas, análise de negócio e próximas ações.",
      icon: (
        <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
          <path d="M14 2v6h6" />
          <path d="M16 13H8" />
          <path d="M16 17H8" />
          <path d="M10 9H8" />
        </svg>
      ),
    },
  ];

  return (
    <section id="como-funciona" className="py-24 bg-gray-50">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16 space-y-4">
          <span className="inline-flex px-3 py-1 bg-nvidia/10 text-nvidia text-xs font-medium rounded-full">
            Pipeline
          </span>
          <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight">
            Como funciona
          </h2>
          <p className="text-gray-500 max-w-lg mx-auto">
            Cinco agentes autônomos trabalham em cascata para transformar dados brutos em
            inteligência acionável.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {steps.map((step) => (
            <div
              key={step.number}
              className="group relative p-6 bg-white rounded-2xl border border-gray-200 card-shadow hover:card-shadow-hover transition-all duration-200"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-nvidia/10 text-nvidia flex items-center justify-center group-hover:bg-nvidia group-hover:text-white transition-colors duration-200">
                  {step.icon}
                </div>
                <span className="text-xs font-mono text-gray-400">{step.number}</span>
              </div>
              <h3 className="text-base font-semibold mb-2">{step.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Architecture() {
  return (
    <section id="arquitetura" className="py-24">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16 space-y-4">
          <span className="inline-flex px-3 py-1 bg-nvidia/10 text-nvidia text-xs font-medium rounded-full">
            LangGraph
          </span>
          <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight">
            Arquitetura Multiagente
          </h2>
          <p className="text-gray-500 max-w-lg mx-auto">
            Sistema orquestrado com LangGraph — cada agente tem uma responsabilidade única
            e o grafo gerencia o fluxo e estado entre eles.
          </p>
        </div>

        <div className="relative bg-white rounded-3xl border border-gray-200 p-8 sm:p-12 card-shadow">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-8">
            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-nvidia/10 flex items-center justify-center text-nvidia">
                <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 002 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" />
                </svg>
              </div>
              <span className="text-xs font-mono bg-gray-100 px-2 py-0.5 rounded text-gray-600">01</span>
              <p className="text-sm font-medium">Scraping</p>
            </div>

            <svg className="w-8 h-8 text-gray-300 hidden lg:block" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
              <path d="M5 12h14" />
              <path d="M12 5l7 7-7 7" />
            </svg>

            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-nvidia/10 flex items-center justify-center text-nvidia">
                <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" />
                  <path d="M12 17h.01" />
                </svg>
              </div>
              <span className="text-xs font-mono bg-gray-100 px-2 py-0.5 rounded text-gray-600">02</span>
              <p className="text-sm font-medium">Classifier</p>
            </div>

            <svg className="w-8 h-8 text-gray-300 hidden lg:block" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
              <path d="M5 12h14" />
              <path d="M12 5l7 7-7 7" />
            </svg>

            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-nvidia/10 flex items-center justify-center text-nvidia">
                <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
                  <path d="M22 4L12 14.01l-3-3" />
                </svg>
              </div>
              <span className="text-xs font-mono bg-gray-100 px-2 py-0.5 rounded text-gray-600">03</span>
              <p className="text-sm font-medium">Validator</p>
            </div>

            <svg className="w-8 h-8 text-gray-300 hidden lg:block" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
              <path d="M5 12h14" />
              <path d="M12 5l7 7-7 7" />
            </svg>

            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-nvidia/10 flex items-center justify-center text-nvidia">
                <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 2L2 7l10 5 10-5-10-5z" />
                  <path d="M2 17l10 5 10-5" />
                  <path d="M2 12l10 5 10-5" />
                </svg>
              </div>
              <span className="text-xs font-mono bg-gray-100 px-2 py-0.5 rounded text-gray-600">04</span>
              <p className="text-sm font-medium">RAG + Recommender</p>
            </div>

            <svg className="w-8 h-8 text-gray-300 hidden lg:block" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
              <path d="M5 12h14" />
              <path d="M12 5l7 7-7 7" />
            </svg>

            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-nvidia/10 flex items-center justify-center text-nvidia">
                <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                  <path d="M14 2v6h6" />
                  <path d="M16 13H8" />
                  <path d="M16 17H8" />
                  <path d="M10 9H8" />
                </svg>
              </div>
              <span className="text-xs font-mono bg-gray-100 px-2 py-0.5 rounded text-gray-600">05</span>
              <p className="text-sm font-medium">Briefer</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Technologies() {
  const techs = [
    { name: "Python", description: "Linguagem principal do ecossistema" },
    { name: "LangGraph", description: "Orquestração de agentes autônomos" },
    { name: "Groq", description: "Inferência LLM ultra-rápida (Llama 3.1 8B)" },
    { name: "ChromaDB", description: "Base vetorial para RAG NVIDIA" },
    { name: "PostgreSQL", description: "Banco relacional em Supabase" },
    { name: "Next.js", description: "Interface web moderna e responsiva" },
    { name: "Django", description: "REST API backend" },
    { name: "Sentence Transformers", description: "Embeddings semânticos" },
  ];

  return (
    <section id="tecnologias" className="py-24 bg-gray-50">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16 space-y-4">
          <span className="inline-flex px-3 py-1 bg-nvidia/10 text-nvidia text-xs font-medium rounded-full">
            Stack
          </span>
          <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight">
            Tecnologias
          </h2>
          <p className="text-gray-500 max-w-lg mx-auto">
            Stack moderno e eficiente para processar, analisar e visualizar dados
            de milhares de startups.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {techs.map((tech) => (
            <div
              key={tech.name}
              className="p-5 bg-white rounded-xl border border-gray-200 card-shadow hover:card-shadow-hover transition-all duration-200"
            >
              <h3 className="font-semibold text-sm">{tech.name}</h3>
              <p className="text-xs text-gray-500 mt-1">{tech.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function About() {
  return (
    <section id="sobre" className="py-24">
      <div className="max-w-7xl mx-auto px-6">
        <div className="max-w-2xl mx-auto text-center space-y-6">
          <span className="inline-flex px-3 py-1 bg-nvidia/10 text-nvidia text-xs font-medium rounded-full">
            Sobre
          </span>
          <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight">
            Um projeto para o ecossistema NVIDIA
          </h2>
          <p className="text-gray-500 leading-relaxed">
            O NVIDIA Startup AI Radar foi desenvolvido como ferramenta estratégica para
            o time de Startups & VCs da NVIDIA na América Latina. O sistema mapeia o
            ecossistema brasileiro de startups, identifica aquelas com real maturidade
            em IA e recomenda tecnologias NVIDIA com alto potencial de adoção.
          </p>
          <p className="text-gray-500 leading-relaxed">
            Cada análise passa por 5 agentes especializados: classificação de maturidade
            em IA, validação de evidências, busca vetorial na base de documentações NVIDIA,
            recomendação técnica e geração de briefing executivo.
          </p>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="py-12 border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded bg-nvidia flex items-center justify-center">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="white">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" />
            </svg>
          </div>
          <span className="text-xs text-gray-400">
            NVIDIA Startup AI Radar &mdash; 2026
          </span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs text-gray-400">Construído com Next.js + Django + LangGraph</span>
        </div>
      </div>
    </footer>
  );
}
