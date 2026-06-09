import type { Metadata } from "next";
import { Cormorant_Garamond, DM_Mono } from "next/font/google";
import { LenisProvider } from "@/components/providers/LenisProvider";
import "./globals.css";

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
  description:
    "Replace repetitive finance operations with intelligent autonomous workflows. OCR, risk analysis, multi-agent automation, and cashflow forecasting in one platform.",
  keywords: [
    "AI finance automation",
    "invoice processing AI",
    "multi-agent workflows",
    "finance operations",
    "OCR intelligence",
    "vendor risk analysis",
    "cashflow forecasting",
  ],
  openGraph: {
    title: "FinanceAI — Autonomous Finance Operations Platform",
    description:
      "Your AI Finance Team. Replace repetitive finance operations with intelligent autonomous workflows.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${cormorant.variable} ${dmMono.variable}`}>
      <body>
        <LenisProvider>{children}</LenisProvider>
      </body>
    </html>
  );
}
