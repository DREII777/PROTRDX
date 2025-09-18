import "./globals.css";
import type { Metadata } from "next";
import { ReactNode } from "react";

export const metadata: Metadata = {
  title: "PROTRDX Dashboard",
  description: "Quant research automation"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background text-foreground">
        <main className="max-w-6xl mx-auto p-6 space-y-6">
          <header className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold">PROTRDX Control Center</h1>
          </header>
          {children}
        </main>
      </body>
    </html>
  );
}
