"use client";

import Link from "next/link";
import { useState } from "react";

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-7 h-7 rounded bg-nvidia flex items-center justify-center">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
            </svg>
          </div>
          <span className="font-semibold text-sm tracking-tight">
            NVIDIA <span className="text-nvidia">Startup AI Radar</span>
          </span>
        </Link>

        <nav className="hidden md:flex items-center gap-8">
          <Link href="/#como-funciona" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">
            Projeto
          </Link>
          <Link href="/#arquitetura" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">
            Arquitetura
          </Link>
          <Link href="/#tecnologias" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">
            Tecnologias
          </Link>
          <Link href="/#sobre" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">
            Sobre
          </Link>
          <Link
            href="https://github.com"
            className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
            target="_blank"
          >
            GitHub
          </Link>
          <Link
            href="/dashboard"
            className="inline-flex items-center px-4 py-1.5 bg-nvidia hover:bg-nvidia-hover text-white text-sm font-medium rounded-lg transition-colors"
          >
            Entrar
          </Link>
        </nav>

        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="md:hidden p-2 text-gray-600"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {menuOpen ? (
              <path d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      {menuOpen && (
        <div className="md:hidden bg-white border-b border-gray-200 px-6 py-4 space-y-3">
          <Link href="/#como-funciona" className="block text-sm text-gray-600">Projeto</Link>
          <Link href="/#arquitetura" className="block text-sm text-gray-600">Arquitetura</Link>
          <Link href="/#tecnologias" className="block text-sm text-gray-600">Tecnologias</Link>
          <Link href="/#sobre" className="block text-sm text-gray-600">Sobre</Link>
          <Link href="/dashboard" className="block text-sm text-nvidia font-medium">Entrar</Link>
        </div>
      )}
    </header>
  );
}
