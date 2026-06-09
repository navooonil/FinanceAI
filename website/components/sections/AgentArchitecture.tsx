"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { EASE_OUT_EXPO } from "@/lib/motion";

const agents = [
  {
    id: "planner",
    name: "Planner Agent",
    role: "Orchestration",
    desc: "Decomposes the invoice into a processing sequence, assigns tasks to downstream agents, and monitors overall pipeline health.",
    color: "#6CE8C2",
    pulse: true,
  },
  {
    id: "research",
    name: "Research Agent",
    role: "Context Retrieval",
    desc: "Runs vector similarity search across your document corpus to retrieve relevant vendor history, contracts, and precedents.",
    color: "#A9B4AE",
    pulse: false,
  },
  {
    id: "finance",
    name: "Finance Agent",
    role: "Calculation Engine",
    desc: "Validates mathematical checksums — subtotals, tax formulas, and line-item totals — against OCR-extracted values.",
    color: "#6CE8C2",
    pulse: false,
  },
  {
    id: "risk",
    name: "Risk Assessment Agent",
    role: "Compliance & Fraud",
    desc: "Scores vendor risk using Z-score anomaly detection, Levenshtein duplicate matching, and IQR statistical bounds.",
    color: "#F59E0B",
    pulse: false,
  },
  {
    id: "report",
    name: "Report Agent",
    role: "Output Compilation",
    desc: "Compiles a structured audit report with citations, structured JSON, and actionable recommendations for the finance team.",
    color: "#6CE8C2",
    pulse: false,
  },
];

export default function AgentArchitecture() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: sectionRef, offset: ["start end", "end start"] });
  const lineHeight = useTransform(scrollYProgress, [0.1, 0.8], ["0%", "100%"]);

  return (
    <section id="agents" ref={sectionRef} className="bg-[#F7F8F5] py-32 overflow-hidden">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="max-w-xl mb-20">
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="font-mono text-[11px] uppercase tracking-widest text-[#6CE8C2] mb-4"
          >
            Multi-Agent Architecture
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1, ease: EASE_OUT_EXPO }}
            className="font-serif text-[clamp(36px,5vw,64px)] leading-[0.95] font-semibold text-[#18362F] mb-6"
          >
            Five agents.<br />
            <em className="not-italic text-[#A9B4AE]">One outcome.</em>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="font-mono text-[13px] text-[#A9B4AE] leading-relaxed"
          >
            Every invoice runs through a coordinated LangGraph pipeline where specialized agents handle research, validation, risk scoring, and reporting in sequence.
          </motion.p>
        </div>

        {/* Agent flow */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
          {/* Left: animated node graph */}
          <div className="relative">
            {/* Vertical spine line — grows on scroll */}
            <div className="absolute left-6 top-8 bottom-8 w-px bg-[#18362F]/8 overflow-hidden">
              <motion.div
                style={{ height: lineHeight }}
                className="w-full bg-gradient-to-b from-[#6CE8C2] to-[#6CE8C2]/20 origin-top"
              />
            </div>

            <div className="space-y-0">
              {agents.map((agent, i) => (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, x: -24 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: "-60px" }}
                  transition={{ duration: 0.7, delay: i * 0.12, ease: EASE_OUT_EXPO }}
                  className="relative pl-16 pb-8"
                >
                  {/* Node dot */}
                  <div className="absolute left-0 top-1 flex items-center justify-center w-12">
                    <motion.div
                      animate={agent.pulse ? {
                        boxShadow: [
                          "0 0 0 0 rgba(108,232,194,0.4)",
                          "0 0 0 12px rgba(108,232,194,0)",
                        ],
                      } : {}}
                      transition={{ duration: 1.8, repeat: Infinity }}
                      className="w-3 h-3 rounded-full border-2"
                      style={{
                        backgroundColor: agent.color + "22",
                        borderColor: agent.color,
                      }}
                    />
                  </div>

                  {/* Step number */}
                  <span className="font-mono text-[9px] text-[#A9B4AE]/50 uppercase tracking-widest mb-1 block">
                    Node {String(i + 1).padStart(2, "0")}
                  </span>

                  {/* Agent card */}
                  <motion.div
                    whileHover={{ x: 4, borderColor: "rgba(108,232,194,0.2)" }}
                    transition={{ duration: 0.2 }}
                    className="p-5 bg-white border border-[#18362F]/6 rounded-xl shadow-[0_2px_12px_rgba(24,54,47,0.04)] transition-all duration-200 cursor-default"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-mono text-sm font-semibold text-[#18362F]">
                          {agent.name}
                        </h3>
                        <span
                          className="font-mono text-[9px] uppercase tracking-widest"
                          style={{ color: agent.color }}
                        >
                          {agent.role}
                        </span>
                      </div>
                      {agent.id === "planner" && (
                        <div className="flex items-center gap-1.5 bg-[#6CE8C2]/10 px-2.5 py-1 rounded-full">
                          <div className="w-1.5 h-1.5 rounded-full bg-[#6CE8C2] animate-pulse" />
                          <span className="font-mono text-[9px] text-[#6CE8C2]">Active</span>
                        </div>
                      )}
                    </div>
                    <p className="font-mono text-[11px] text-[#A9B4AE] leading-relaxed">{agent.desc}</p>
                  </motion.div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Right: technical stats */}
          <div className="lg:pt-4 space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, delay: 0.2, ease: EASE_OUT_EXPO }}
              className="p-6 bg-white border border-[#18362F]/6 rounded-2xl shadow-[0_4px_24px_rgba(24,54,47,0.05)]"
            >
              <p className="font-mono text-[10px] uppercase tracking-widest text-[#A9B4AE] mb-5">
                Pipeline Execution Trace
              </p>
              <div className="space-y-3">
                {[
                  { agent: "Planner", ms: 120, status: "complete" },
                  { agent: "Research", ms: 380, status: "complete" },
                  { agent: "Finance", ms: 210, status: "complete" },
                  { agent: "Risk", ms: 295, status: "complete" },
                  { agent: "Report", ms: 150, status: "complete" },
                ].map((row, i) => (
                  <div key={i} className="flex items-center gap-4">
                    <span className="font-mono text-[11px] text-[#18362F] w-20">{row.agent}</span>
                    <div className="flex-1 h-1.5 bg-[#F7F8F5] rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        whileInView={{ width: `${(row.ms / 400) * 100}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8, delay: 0.4 + i * 0.1, ease: EASE_OUT_EXPO }}
                        className="h-full bg-[#6CE8C2] rounded-full"
                      />
                    </div>
                    <span className="font-mono text-[10px] text-[#A9B4AE] w-12 text-right">{row.ms}ms</span>
                    <div className="w-1.5 h-1.5 rounded-full bg-[#6CE8C2]" />
                  </div>
                ))}
              </div>
              <div className="mt-5 pt-4 border-t border-[#18362F]/5 flex justify-between">
                <span className="font-mono text-[10px] text-[#A9B4AE]">Total pipeline</span>
                <span className="font-mono text-xs font-semibold text-[#18362F]">1,155ms</span>
              </div>
            </motion.div>

            <div className="grid grid-cols-2 gap-4">
              {[
                { label: "Avg pipeline time", value: "3.2s" },
                { label: "Pipeline accuracy", value: "99.2%" },
                { label: "Concurrent pipelines", value: "Unlimited" },
                { label: "LangGraph nodes", value: "5 agents" },
              ].map((stat, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 16 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: 0.3 + i * 0.08 }}
                  className="p-4 bg-white border border-[#18362F]/6 rounded-xl"
                >
                  <p className="font-mono text-xs font-bold text-[#18362F] mb-1">{stat.value}</p>
                  <p className="font-mono text-[10px] text-[#A9B4AE]">{stat.label}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
