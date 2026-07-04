import type { Metadata } from "next";
import Sidebar from "@/components/sidebar";

export const metadata: Metadata = {
  title: "Dashboard — NVIDIA Startup AI Radar",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <main className="flex-1 p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
