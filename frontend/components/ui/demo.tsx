"use client";

import { ArrowRight } from "lucide-react";
import Link from "next/link";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Marquee } from "@/components/ui/marquee";

const teamAvatars = [
  {
    initials: "CG",
    src: "/perfil.jpeg",
  },
];

const stats = [
  { emoji: "🚀", label: "STARTUPS BRASILEIRAS MAPEADAS", value: "3.800+" },
  { emoji: "📈", label: "FONTES DE DADOS MAPEADAS", value: "16+" },
  { emoji: "🧠", label: "AGENTES DE IA AUTÔNOMOS", value: "5" },
];

function AvatarStack() {
  return (
    <div className="flex">
      <a
        href="https://www.linkedin.com/in/christian-gandra/"
        target="_blank"
        rel="noopener noreferrer"
        className="group/avatar transition-transform hover:scale-105 duration-200"
      >
        <Avatar className="size-13 border-2 border-primary bg-neutral-800">
          <AvatarImage alt="Christian Gandra" src="/perfil.jpeg" />
          <AvatarFallback className="bg-neutral-700 text-white text-xs">
            CG
          </AvatarFallback>
        </Avatar>
      </a>
    </div>
  );
}

function StatsMarquee() {
  return (
    <Marquee
      className="border-white/10 border-y bg-black/30 py-2 backdrop-blur-sm [--duration:30s] [--gap:2rem]"
      pauseOnHover
      repeat={4}
    >
      {stats.map((stat) => (
        <div
          className="flex items-center gap-3 whitespace-nowrap"
          key={stat.label}
        >
          <span className="font-bold font-mono text-primary text-sm tracking-wide">
            {stat.value}
          </span>
          <span className="font-medium font-mono text-sm text-white/70 uppercase tracking-[0.15em]">
            {stat.label}
          </span>
          <span className="text-base">{stat.emoji}</span>
        </div>
      ))}
    </Marquee>
  );
}

export default function Hero() {
  return (
    <section className="relative flex h-screen w-full flex-col items-start justify-end">
      <div
        className="absolute inset-0 bg-center bg-cover"
        style={{
          backgroundImage:
            "url(https://images.unsplash.com/photo-1541746972996-4e0b0f43e02a)",
        }}
      >
        <div className="absolute inset-0 bg-black/40" />
      </div>

      <div className="relative z-10 w-full max-w-4xl px-4 text-white sm:px-8 lg:px-16">
        <div className="space-y-4">
          <AvatarStack />
          <StatsMarquee />
        </div>
      </div>
      <div className="relative z-10 w-full px-4 pb-16 sm:px-8 sm:pb-24 lg:px-16 lg:pb-32">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-end">
          <div className="w-full space-y-4 sm:w-1/2">
            <h1 className="font-medium text-4xl text-white leading-[1.05] tracking-tight sm:text-5xl md:text-6xl lg:text-7xl">
              NVIDIA <span className="text-primary">Startup</span>
              <br />
              <span className="text-white">AI Radar</span>
            </h1>
            <Link href="/dashboard" passHref>
              <Button className="rounded-none py-0 pr-0 font-normal text-white text-lg cursor-pointer flex items-center">
                Acessar Radar
                <span className="border-white/20 border-l p-3 ml-3 inline-flex items-center justify-center">
                  <ArrowRight />
                </span>
              </Button>
            </Link>
          </div>
          <div className="w-full sm:w-1/2">
            <p className="text-base text-primary italic sm:text-right md:text-2xl">
              Identificando maturidade técnica, mapeando ecossistemas e recomendando a stack NVIDIA ideal para startups brasileiras impulsionarem seus modelos de IA.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
