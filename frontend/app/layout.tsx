import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NVIDIA Startup AI Radar",
  description:
    "Plataforma de inteligência para identificação e análise de startups brasileiras com maturidade em IA, utilizando agentes autônomos LangGraph e tecnologias NVIDIA.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
