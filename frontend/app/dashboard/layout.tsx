"use client";

import React, { useState } from "react";
import { Sidebar, SidebarBody, SidebarLink } from "@/components/ui/sidebar";
import { LayoutDashboard, Search, Database, BarChart3, FileText } from "lucide-react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import Image from "next/image";

const Logo = () => {
  return (
    <div className="h-12 flex items-center gap-2.5 px-1 relative z-20">
      <Image
        src="/logo_red.svg"
        alt="NVIDIA Logo"
        width={28}
        height={18}
        className="w-7 h-auto shrink-0"
        priority
      />
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-xs font-semibold truncate text-white"
      >
        Startup <span className="text-nvidia">Radar</span>
      </motion.p>
    </div>
  );
};

const LogoIcon = () => {
  return (
    <div className="h-12 flex items-center gap-2.5 px-1 relative z-20">
      <Image
        src="/logo_red.svg"
        alt="NVIDIA Logo"
        width={28}
        height={18}
        className="w-7 h-auto shrink-0"
        priority
      />
    </div>
  );
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const links = [
    {
      label: "Dashboard",
      href: "/dashboard",
      icon: (
        <LayoutDashboard className="h-5 w-5 flex-shrink-0 transition-colors" />
      ),
    },
    {
      label: "Pesquisar Startup",
      href: "/dashboard/startups",
      icon: (
        <Search className="h-5 w-5 flex-shrink-0 transition-colors" />
      ),
    },
    {
      label: "Base NVIDIA",
      href: "/dashboard/nvidia-base",
      icon: (
        <Database className="h-5 w-5 flex-shrink-0 transition-colors" />
      ),
    },
    {
      label: "Analytics",
      href: "/dashboard/analytics",
      icon: (
        <BarChart3 className="h-5 w-5 flex-shrink-0 transition-colors" />
      ),
    },
    {
      label: "Briefings",
      href: "/dashboard/briefings",
      icon: (
        <FileText className="h-5 w-5 flex-shrink-0 transition-colors" />
      ),
    },
  ];

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden w-full">
      <Sidebar open={open} setOpen={setOpen}>
        <SidebarBody className="justify-between gap-10">
          <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
            {open ? <Logo /> : <LogoIcon />}
            <div className="mt-8 flex flex-col gap-2">
              {links.map((link, idx) => {
                const isActive = pathname === link.href || (link.href !== "/dashboard" && pathname.startsWith(link.href));
                return (
                  <SidebarLink
                    key={idx}
                    link={{
                      ...link,
                      icon: React.cloneElement(link.icon as React.ReactElement<any>, {
                        className: cn(
                          "h-5 w-5 flex-shrink-0 transition-colors",
                          isActive ? "text-nvidia" : "text-neutral-400 group-hover/sidebar:text-white"
                        )
                      })
                    }}
                    className={cn(
                      isActive
                        ? "bg-nvidia/10 text-nvidia font-medium hover:bg-nvidia/15"
                        : "text-neutral-400 hover:bg-white/5 hover:text-white"
                    )}
                  />
                );
              })}
            </div>
          </div>
          <div className="pb-4">
            <div className="flex items-center gap-3 px-3 py-2 text-xs text-gray-400">
              <div className="w-2 h-2 rounded-full bg-nvidia animate-pulse flex-shrink-0" />
              {open && <span className="truncate">Agente IA ativo</span>}
            </div>
          </div>
        </SidebarBody>
      </Sidebar>
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <main className="flex-1 p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
