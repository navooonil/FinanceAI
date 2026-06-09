"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { EASE_OUT_EXPO } from "@/lib/motion";

interface MetricItem {
  key: string;
  val: string;
}

interface AIResponseBlockData {
  type: "header" | "grade" | "metrics" | "alert" | "recommendation";
  text?: string;
  grade?: string;
  score?: number;
  label?: string;
  items?: (string | MetricItem)[];
}

interface Scenario {
  id: string;
  tab: string;
  userMsg: string;
  aiResponse: AIResponseBlockData[];
}

const scenarios: Scenario[] = [
  {
    id: "risk",
    tab: "Risk Analysis",
    userMsg: "Analyze risk profile for Apex Global Logistics and flag any concerns.",
    aiResponse: [
      { type: "header", text: "Risk Analysis — Apex Global Logistics" },
      { type: "grade", grade: "A", score: 12, label: "Low Risk Counterparty" },
      { type: "metrics", items: [
        { key: "Total Spend (TTM)", val: "$345,000" },
        { key: "Invoice Volume", val: "24 invoices" },
        { key: "Checksum Pass Rate", val: "100%" },
        { key: "Duplicate Flags", val: "None" },
        { key: "Weekend Issuance", val: "No anomalies" },
      ]},
      { type: "recommendation", text: "Auto-approve invoices under $50,000. No enhanced monitoring required." },
    ],
  },
  {
    id: "invoice",
    tab: "Invoice Review",
    userMsg: "Review invoice INV-2026-889 from Z-Axis Engineering. Should we approve?",
    aiResponse: [
      { type: "header", text: "Invoice Review — INV-2026-889" },
      { type: "alert", items: [
        "Amount 2.8σ above vendor historical mean",
        "Timestamp: Saturday 11:42 PM (anomalous)",
        "Vendor risk grade: F (Score 82/100)",
      ]},
      { type: "metrics", items: [
        { key: "Amount", val: "$68,500.00" },
        { key: "Vendor", val: "Z-Axis Engineering" },
        { key: "Due Date", val: "2026-07-14" },
        { key: "Status", val: "Flagged" },
      ]},
      { type: "recommendation", text: "Do not auto-approve. Routed to VP Approval queue. ETA: 2 hours." },
    ],
  },
  {
    id: "vendor",
    tab: "Vendor Intelligence",
    userMsg: "Summarize vendor compliance health for Q2 2026 across all counterparties.",
    aiResponse: [
      { type: "header", text: "Q2 2026 Vendor Compliance Summary" },
      { type: "metrics", items: [
        { key: "Vendors Analyzed", val: "47" },
        { key: "High Risk (D–F)", val: "3 vendors" },
        { key: "Compliance Rate", val: "93.6%" },
        { key: "Duplicate Clusters", val: "2 detected" },
        { key: "Anomalous Spend", val: "$127,500" },
      ]},
      { type: "alert", items: [
        "Z-Axis Engineering: Immediate audit required",
        "Sentry Security: Enhanced monitoring recommended",
      ]},
      { type: "recommendation", text: "Schedule vendor audits. Projected risk reduction: 68% within 30 days." },
    ],
  },
];

function useTypewriter(text: string, speed = 18, started = false) {
  const [displayed, setDisplayed] = useState("");
  useEffect(() => {
    if (!started) { setDisplayed(""); return; }
    setDisplayed("");
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) clearInterval(interval);
    }, speed);
    return () => clearInterval(interval);
  }, [text, started, speed]);
  return displayed;
}


function AIResponseBlock({ block, index, show }: { block: AIResponseBlockData; index: number; show: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={show ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }}
      transition={{ duration: 0.4, delay: 0.6 + index * 0.15, ease: EASE_OUT_EXPO }}
    >
      {block.type === "header" && (
        <p className="font-mono text-[11px] font-semibold text-[#6CE8C2] mb-3 uppercase tracking-widest">
          {block.text}
        </p>
      )}
      {block.type === "grade" && (
        <div className="flex items-center gap-4 mb-3 p-3 rounded-lg bg-[#6CE8C2]/8 border border-[#6CE8C2]/15">
          <div className="w-10 h-10 rounded-lg bg-[#6CE8C2]/20 border border-[#6CE8C2]/30 flex items-center justify-center font-mono text-lg font-bold text-[#6CE8C2]">
            {block.grade}
          </div>
          <div>
            <p className="font-mono text-xs font-semibold text-white">Risk Score: {block.score}/100</p>
            <p className="font-mono text-[10px] text-[#A9B4AE]">{block.label}</p>
          </div>
        </div>
      )}
      {block.type === "metrics" && (
        <div className="space-y-1.5 mb-3">
          {(block.items as MetricItem[] | undefined)?.map((item: MetricItem, i: number) => (
            <div key={i} className="flex items-center justify-between py-1.5 border-b border-white/5">
              <span className="font-mono text-[10px] text-[#A9B4AE]">{item.key}</span>
              <span className="font-mono text-[10px] font-medium text-white">{item.val}</span>
            </div>
          ))}
        </div>
      )}
      {block.type === "alert" && (
        <div className="mb-3 p-3 rounded-lg bg-amber-500/8 border border-amber-500/15 space-y-1.5">
          {(block.items as string[] | undefined)?.map((item: string, i: number) => (
            <p key={i} className="font-mono text-[10px] text-amber-400 flex items-start gap-2">
              <span className="shrink-0 mt-0.5">⚠</span> {item}
            </p>
          ))}
        </div>
      )}
      {block.type === "recommendation" && (
        <div className="p-3 rounded-lg bg-white/5 border border-white/8">
          <p className="font-mono text-[10px] text-[#A9B4AE] leading-relaxed">
            <span className="text-[#6CE8C2] font-semibold">→ </span>
            {block.text}
          </p>
        </div>
      )}
    </motion.div>
  );
}

export default function CopilotShowcase() {
  const [activeTab, setActiveTab] = useState(0);
  const [phase, setPhase] = useState<"idle" | "typing" | "thinking" | "response">("idle");
  const scenario = scenarios[activeTab];

  const typedMsg = useTypewriter(scenario.userMsg, 22, phase === "typing");

  // Auto-sequence the animation
  useEffect(() => {
    setPhase("idle");
    const t1 = setTimeout(() => setPhase("typing"), 400);
    return () => clearTimeout(t1);
  }, [activeTab]);

  useEffect(() => {
    if (phase === "typing" && typedMsg === scenario.userMsg) {
      const t = setTimeout(() => setPhase("thinking"), 300);
      return () => clearTimeout(t);
    }
  }, [phase, typedMsg, scenario.userMsg]);

  useEffect(() => {
    if (phase === "thinking") {
      const t = setTimeout(() => setPhase("response"), 1200);
      return () => clearTimeout(t);
    }
  }, [phase]);

  return (
    <section id="product" className="bg-[#061412] py-32">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section header */}
        <div className="flex flex-col md:flex-row items-start md:items-end justify-between gap-8 mb-16">
          <div>
            <motion.p
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="font-mono text-[11px] uppercase tracking-widest text-[#6CE8C2] mb-4"
            >
              AI Finance Copilot
            </motion.p>
            <motion.h2
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, delay: 0.1, ease: EASE_OUT_EXPO }}
              className="font-serif text-[clamp(36px,5vw,64px)] leading-[0.95] font-semibold text-white"
            >
              Ask anything.<br />
              <span className="text-[#A9B4AE]">Get the full picture.</span>
            </motion.h2>
          </div>
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="font-mono text-[13px] text-[#A9B4AE]/70 max-w-xs leading-relaxed"
          >
            Natural language queries over your entire financial dataset. Grounded in your documents.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Left panel — conversation */}
          <motion.div
            initial={{ opacity: 0, x: -24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, ease: EASE_OUT_EXPO }}
            className="lg:col-span-3 bg-[#0A1E1B] rounded-2xl border border-white/5 overflow-hidden flex flex-col"
          >
            {/* Terminal bar */}
            <div className="flex items-center gap-2 px-5 py-3.5 border-b border-white/5">
              <div className="w-2.5 h-2.5 rounded-full bg-rose-500/60" />
              <div className="w-2.5 h-2.5 rounded-full bg-amber-500/60" />
              <div className="w-2.5 h-2.5 rounded-full bg-[#6CE8C2]/60" />
              <span className="font-mono text-[10px] text-[#A9B4AE]/40 ml-3 tracking-wide">finance-copilot — session</span>
            </div>

            {/* Scenario tabs */}
            <div className="flex gap-1 p-3 border-b border-white/5">
              {scenarios.map((s, i) => (
                <button
                  key={s.id}
                  onClick={() => setActiveTab(i)}
                  className={`flex-1 font-mono text-[10px] py-2 rounded-lg transition-all duration-200 ${
                    activeTab === i
                      ? "bg-[#6CE8C2]/10 text-[#6CE8C2] border border-[#6CE8C2]/20"
                      : "text-[#A9B4AE]/50 hover:text-[#A9B4AE]"
                  }`}
                >
                  {s.tab}
                </button>
              ))}
            </div>

            {/* Chat viewport */}
            <div className="flex-1 p-6 space-y-6 min-h-[420px] overflow-y-auto">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="space-y-6"
                >
                  {/* User message */}
                  {phase !== "idle" && (
                    <div className="flex justify-end">
                      <div className="max-w-[80%] bg-[#18362F]/60 border border-[#6CE8C2]/10 rounded-xl rounded-tr-sm px-4 py-3">
                        <p className="font-mono text-[11px] text-white/80 leading-relaxed">
                          {typedMsg}
                          {phase === "typing" && typedMsg !== scenario.userMsg && (
                            <span className="inline-block w-0.5 h-3 bg-[#6CE8C2] ml-0.5 animate-pulse" />
                          )}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Thinking indicator */}
                  {phase === "thinking" && (
                    <motion.div
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-center gap-3"
                    >
                      <div className="w-6 h-6 rounded-full bg-[#6CE8C2]/15 border border-[#6CE8C2]/20 flex items-center justify-center">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#6CE8C2]" />
                      </div>
                      <div className="flex gap-1">
                        {[0, 1, 2].map((i) => (
                          <motion.div
                            key={i}
                            animate={{ opacity: [0.3, 1, 0.3] }}
                            transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.2 }}
                            className="w-1.5 h-1.5 rounded-full bg-[#6CE8C2]/60"
                          />
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {/* AI Response */}
                  {phase === "response" && (
                    <div className="flex gap-3">
                      <div className="w-6 h-6 rounded-full bg-[#6CE8C2]/15 border border-[#6CE8C2]/20 flex items-center justify-center shrink-0 mt-0.5">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#6CE8C2]" />
                      </div>
                      <div className="flex-1 bg-[#0D2420] rounded-xl rounded-tl-sm px-4 py-3 border border-white/5 space-y-3">
                        {scenario.aiResponse.map((block, i) => (
                          <AIResponseBlock key={i} block={block} index={i} show={phase === "response"} />
                        ))}
                        <p className="font-mono text-[9px] text-[#A9B4AE]/30 pt-2 border-t border-white/5">
                          Sources: invoices.db · vendor_risk.db · analytics.db
                        </p>
                      </div>
                    </div>
                  )}
                </motion.div>
              </AnimatePresence>
            </div>

            {/* Input bar */}
            <div className="p-4 border-t border-white/5">
              <div className="flex items-center gap-3 bg-[#0D2420] border border-white/8 rounded-xl px-4 py-3">
                <input
                  className="flex-1 bg-transparent font-mono text-[11px] text-white/60 placeholder-white/20 outline-none"
                  placeholder="Ask about invoices, vendors, cashflow..."
                  readOnly
                />
                <div className="w-6 h-6 rounded-lg bg-[#6CE8C2]/20 flex items-center justify-center">
                  <span className="text-[#6CE8C2] text-xs">↑</span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Right panel — feature callouts */}
          <motion.div
            initial={{ opacity: 0, x: 24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.2, ease: EASE_OUT_EXPO }}
            className="lg:col-span-2 flex flex-col gap-4"
          >
            {[
              {
                icon: "⚡",
                title: "Intent-aware routing",
                desc: "Classifies your query and routes it to the right data source — invoices, vendors, trends, or documents.",
              },
              {
                icon: "🔒",
                title: "Tenant-isolated answers",
                desc: "Every response is scoped strictly to your company's data. No cross-tenant leakage, ever.",
              },
              {
                icon: "📎",
                title: "Source citations",
                desc: "Every insight cites the exact database table, document, or calculation it was derived from.",
              },
              {
                icon: "💬",
                title: "Conversational memory",
                desc: "Maintains context across multi-turn conversations within a session — no need to repeat yourself.",
              },
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.3 + i * 0.1, ease: EASE_OUT_EXPO }}
                whileHover={{ y: -2, borderColor: "rgba(108,232,194,0.2)" }}
                className="p-5 bg-[#0A1E1B] border border-white/5 rounded-xl transition-all duration-200 cursor-default"
              >
                <div className="text-xl mb-3">{feature.icon}</div>
                <h3 className="font-mono text-xs font-semibold text-white mb-1.5">{feature.title}</h3>
                <p className="font-mono text-[11px] text-[#A9B4AE]/70 leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
