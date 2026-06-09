import type { Metadata } from "next";
import { Geist, Geist_Mono, Cormorant_Garamond, DM_Mono } from "next/font/google";
import { LenisProvider } from "@/components/providers/LenisProvider";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const cormorant = Cormorant_Garamond({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  style: ["normal", "italic"],
  variable: "--font-cormorant",
  display: "swap",
});

const dmMono = DM_Mono({
  subsets: ["latin"],
  weight: ["300", "400", "500"],
  style: ["normal", "italic"],
  variable: "--font-dmmono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "FinanceAI — Autonomous Finance Operations Platform",
  description: "Replace repetitive finance operations with intelligent autonomous workflows. OCR, risk analysis, multi-agent automation, and cashflow forecasting in one platform.",
  keywords: [
    "AI finance automation",
    "invoice processing AI",
    "multi-agent workflows",
    "finance operations",
    "OCR intelligence",
    "vendor risk analysis",
    "cashflow forecasting",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} ${cormorant.variable} ${dmMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <LenisProvider>{children}</LenisProvider>
      </body>
    </html>
  );
}
