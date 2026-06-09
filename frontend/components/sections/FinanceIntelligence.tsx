"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { EASE_OUT_EXPO } from "@/lib/motion";

const barData = [
  { month: "Jan", value: 65, amount: "$1.2M" },
  { month: "Feb", value: 72, amount: "$1.4M" },
  { month: "Mar", value: 58, amount: "$1.1M" },
  { month: "Apr", value: 88, amount: "$1.7M" },
  { month: "May", value: 94, amount: "$1.8M" },
  { month: "Jun", value: 100, amount: "$2.1M" },
];

const riskVendors = [
  { name: "Apex Global Logistics", grade: "A", score: 12, spend: "$345K" },
  { name: "Meridian Supply Co.", grade: "B", score: 28, spend: "$218K" },
  { name: "Fortis Industrial", grade: "B", score: 35, spend: "$190K" },
  { name: "Z-Axis Engineering", grade: "F", score: 82, spend: "$68K" },
];

const gradeColor: Record<string, string> = {
  A: "#6CE8C2",
  B: "#A9B4AE",
  C: "#F59E0B",
  D: "#F97316",
  F: "#F43F5E",
};

function AnimatedNumber({ value, suffix = "" }: { value: number; suffix?: string }) {
  return (
    <motion.span
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      className="font-serif text-[clamp(36px,4vw,56px)] font-semibold text-[#18362F] leading-none"
    >
      <motion.span
        initial={{ y: 20, opacity: 0 }}
        whileInView={{ y: 0, opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8, ease: EASE_OUT_EXPO }}
      >
        {value}{suffix}
      </motion.span>
    </motion.span>
  );
}

export default function FinanceIntelligence() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: sectionRef, offset: ["start end", "end start"] });
  const y1 = useTransform(scrollYProgress, [0, 1], [30, -30]);

  return (
    <section id="intelligence" ref={sectionRef} className="bg-[#F7F8F5] py-32 overflow-hidden">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="max-w-2xl mb-20">
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="font-mono text-[11px] uppercase tracking-widest text-[#6CE8C2] mb-4"
          >
            Financial Intelligence Engine
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1, ease: EASE_OUT_EXPO }}
            className="font-serif text-[clamp(36px,5vw,64px)] leading-[0.95] font-semibold text-[#18362F]"
          >
            Risk, anomalies,{" "}
            <span className="text-[#A9B4AE]">and forecasts.</span>
          </motion.h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Spending Trend Chart */}
          <motion.div
            initial={{ opacity: 0, y: 32 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, ease: EASE_OUT_EXPO }}
            className="lg:col-span-2 bg-white border border-[#18362F]/6 rounded-2xl p-6 shadow-[0_4px_32px_rgba(24,54,47,0.05)]"
          >
            <div className="flex items-start justify-between mb-6">
              <div>
                <p className="font-mono text-[10px] uppercase tracking-widest text-[#A9B4AE] mb-1">
                  Spend Velocity
                </p>
                <AnimatedNumber value={2.1} suffix="M" />
                <p className="font-mono text-[11px] text-[#6CE8C2] mt-1">↑ 16.7% vs prior period</p>
              </div>
              <div className="flex items-center gap-1.5 bg-[#6CE8C2]/10 px-3 py-1.5 rounded-full">
                <div className="w-1.5 h-1.5 rounded-full bg-[#6CE8C2] animate-pulse" />
                <span className="font-mono text-[9px] text-[#6CE8C2]">Live</span>
              </div>
            </div>

            {/* Bar chart */}
            <div className="flex items-end gap-3 h-36">
              {barData.map((bar, i) => (
                <div key={bar.month} className="flex-1 flex flex-col items-center gap-2">
                  <div className="w-full flex flex-col items-center justify-end h-28 gap-1">
                    <span className="font-mono text-[9px] text-[#A9B4AE]/60">{bar.amount}</span>
                    <div className="w-full rounded-t-md overflow-hidden bg-[#F7F8F5]" style={{ height: "100%" }}>
                      <motion.div
                        initial={{ height: 0 }}
                        whileInView={{ height: `${bar.value}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.9, delay: 0.3 + i * 0.1, ease: EASE_OUT_EXPO }}
                        className="w-full rounded-t-md"
                        style={{
                          background: i === barData.length - 1
                            ? "linear-gradient(to top, #6CE8C2, #6CE8C2cc)"
                            : "linear-gradient(to top, #18362F20, #18362F10)",
                          marginTop: "auto",
                        }}
                      />
                    </div>
                  </div>
                  <span className="font-mono text-[9px] text-[#A9B4AE]/60">{bar.month}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Key metrics column */}
          <div className="flex flex-col gap-4">
            {[
              {
                label: "Anomaly Detection",
                value: "340",
                sub: "invoices flagged this quarter",
                detail: "2.6% anomaly rate — industry avg 4.1%",
                accent: "#6CE8C2",
              },
              {
                label: "Cash Runway",
                value: "94 days",
                sub: "operating runway remaining",
                detail: "↑ 12 days vs 30-day forecast",
                accent: "#6CE8C2",
              },
              {
                label: "Duplicate Risk",
                value: "$127K",
                sub: "in potential duplicate exposure",
                detail: "3 vendors flagged for investigation",
                accent: "#F59E0B",
              },
            ].map((card, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: 24 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.7, delay: 0.1 + i * 0.12, ease: EASE_OUT_EXPO }}
                whileHover={{ y: -2 }}
                className="bg-white border border-[#18362F]/6 rounded-xl p-5 shadow-[0_2px_12px_rgba(24,54,47,0.04)] transition-all duration-200 cursor-default"
              >
                <p className="font-mono text-[9px] uppercase tracking-widest text-[#A9B4AE] mb-2">
                  {card.label}
                </p>
                <p className="font-mono text-2xl font-bold text-[#18362F] mb-0.5">{card.value}</p>
                <p className="font-mono text-[10px] text-[#A9B4AE] mb-2">{card.sub}</p>
                <p className="font-mono text-[10px]" style={{ color: card.accent }}>
                  {card.detail}
                </p>
              </motion.div>
            ))}
          </div>

          {/* Vendor Risk Table */}
          <motion.div
            initial={{ opacity: 0, y: 32 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.2, ease: EASE_OUT_EXPO }}
            className="lg:col-span-2 bg-white border border-[#18362F]/6 rounded-2xl p-6 shadow-[0_4px_32px_rgba(24,54,47,0.05)]"
          >
            <p className="font-mono text-[10px] uppercase tracking-widest text-[#A9B4AE] mb-5">
              Vendor Risk Ledger
            </p>
            <div className="space-y-0">
              <div className="grid grid-cols-4 pb-2 border-b border-[#18362F]/5">
                {["Vendor", "Grade", "Risk Score", "TTM Spend"].map((h) => (
                  <span key={h} className="font-mono text-[9px] uppercase tracking-widest text-[#A9B4AE]/50">{h}</span>
                ))}
              </div>
              {riskVendors.map((v, i) => (
                <motion.div
                  key={v.name}
                  initial={{ opacity: 0, x: -16 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.3 + i * 0.1 }}
                  whileHover={{ backgroundColor: "rgba(24,54,47,0.02)", x: 2 }}
                  className="grid grid-cols-4 py-3.5 border-b border-[#18362F]/4 transition-all duration-150 rounded-sm"
                >
                  <span className="font-mono text-[11px] text-[#18362F] font-medium truncate pr-4">{v.name}</span>
                  <div>
                    <span
                      className="font-mono text-[11px] font-bold px-2 py-0.5 rounded"
                      style={{
                        color: gradeColor[v.grade],
                        backgroundColor: gradeColor[v.grade] + "15",
                      }}
                    >
                      {v.grade}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1 bg-[#F7F8F5] rounded-full overflow-hidden max-w-16">
                      <motion.div
                        initial={{ width: 0 }}
                        whileInView={{ width: `${v.score}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8, delay: 0.4 + i * 0.1 }}
                        className="h-full rounded-full"
                        style={{ backgroundColor: gradeColor[v.grade] }}
                      />
                    </div>
                    <span className="font-mono text-[10px] text-[#A9B4AE]">{v.score}</span>
                  </div>
                  <span className="font-mono text-[11px] text-[#18362F]">{v.spend}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Forecast card */}
          <motion.div
            style={{ y: y1 }}
            initial={{ opacity: 0, y: 32 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="bg-[#18362F] text-white rounded-2xl p-6 flex flex-col justify-between"
          >
            <div>
              <p className="font-mono text-[10px] uppercase tracking-widest text-[#6CE8C2]/60 mb-4">
                Cashflow Forecast
              </p>
              <p className="font-serif text-5xl font-semibold mb-1">+12.4%</p>
              <p className="font-mono text-[11px] text-white/50 mb-6">Projected MoM growth · Q3 2026</p>
            </div>

            <div className="space-y-2.5">
              {[
                { label: "Projected inflows", val: "$2.4M", trend: "↑" },
                { label: "Committed outflows", val: "$1.8M", trend: "→" },
                { label: "Net projected", val: "$620K", trend: "↑" },
              ].map((row) => (
                <div key={row.label} className="flex justify-between">
                  <span className="font-mono text-[10px] text-white/40">{row.label}</span>
                  <span className="font-mono text-[10px] text-[#6CE8C2]">{row.trend} {row.val}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
