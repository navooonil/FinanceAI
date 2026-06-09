"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { EASE_OUT_EXPO } from "@/lib/motion";

const steps = [
  {
    id: "trigger",
    label: "TRIGGER",
    title: "Invoice Received",
    desc: "OCR extraction complete. Invoice data structured and ready for evaluation.",
    code: 'event: "invoice_ingested"\nentity_id: "inv-2026-889"',
    color: "#6CE8C2",
    icon: "↓",
  },
  {
    id: "condition",
    label: "CONDITION",
    title: "IF amount > $50,000",
    desc: "Evaluates the invoice total against the configured threshold for high-value spend.",
    code: 'field: "invoice.total_amount"\noperator: "greater_than"\nvalue: 50000',
    color: "#F59E0B",
    icon: "⇀",
  },
  {
    id: "risk",
    label: "RISK CHECK",
    title: "Vendor risk grade < B",
    desc: "Queries the vendor intelligence engine for current risk score before routing.",
    code: 'field: "vendor.risk_grade"\noperator: "not_in"\nvalue: ["A", "B"]',
    color: "#F43F5E",
    icon: "⊕",
  },
  {
    id: "approval",
    label: "ACTION",
    title: "Route to VP Approval",
    desc: "Workflow pauses, creates an approval request, and notifies via Slack and email.",
    code: 'type: "require_approval"\nrole: "VP_FINANCE"\nnotify: ["slack", "email"]',
    color: "#6CE8C2",
    icon: "✓",
  },
];

export default function WorkflowBuilder() {
  const [hoveredStep, setHoveredStep] = useState<string | null>(null);

  return (
    <section className="bg-[#061412] py-32 overflow-hidden">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row items-start md:items-end justify-between gap-8 mb-16">
          <div className="max-w-lg">
            <motion.p
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="font-mono text-[11px] uppercase tracking-widest text-[#6CE8C2] mb-4"
            >
              Workflow Automation
            </motion.p>
            <motion.h2
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, delay: 0.1, ease: EASE_OUT_EXPO }}
              className="font-serif text-[clamp(36px,5vw,64px)] leading-[0.95] font-semibold text-white"
            >
              Rules that run
              <br />
              <span className="text-[#A9B4AE]">themselves.</span>
            </motion.h2>
          </div>
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="font-mono text-[13px] text-[#A9B4AE]/70 max-w-xs leading-relaxed"
          >
            Build conditional logic pipelines with no code. Trigger, evaluate, act — all in milliseconds.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          {/* Workflow steps */}
          <div className="lg:col-span-2">
            <div className="relative">
              {/* Vertical connection line */}
              <div className="absolute left-6 top-8 bottom-8 w-px bg-white/5" />
              <motion.div
                className="absolute left-6 top-8 w-px bg-gradient-to-b from-[#6CE8C2]/40 to-transparent origin-top"
                initial={{ height: 0 }}
                whileInView={{ height: "calc(100% - 64px)" }}
                viewport={{ once: true }}
                transition={{ duration: 1.5, delay: 0.5, ease: EASE_OUT_EXPO }}
              />

              <div className="space-y-4">
                {steps.map((step, i) => (
                  <motion.div
                    key={step.id}
                    initial={{ opacity: 0, x: -24 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true, margin: "-60px" }}
                    transition={{ duration: 0.7, delay: i * 0.15, ease: EASE_OUT_EXPO }}
                    onMouseEnter={() => setHoveredStep(step.id)}
                    onMouseLeave={() => setHoveredStep(null)}
                    className="relative pl-16 cursor-default"
                  >
                    {/* Node */}
                    <div
                      className="absolute left-0 top-4 w-12 flex items-center justify-center"
                    >
                      <motion.div
                        animate={hoveredStep === step.id ? { scale: 1.2 } : { scale: 1 }}
                        className="w-3 h-3 rounded-full border-2 transition-all"
                        style={{
                          borderColor: step.color,
                          backgroundColor: step.color + "22",
                          boxShadow: hoveredStep === step.id ? `0 0 12px ${step.color}50` : "none",
                        }}
                      />
                    </div>

                    <motion.div
                      animate={hoveredStep === step.id ? {
                        borderColor: step.color + "30",
                        backgroundColor: "rgba(255,255,255,0.04)",
                      } : {
                        borderColor: "rgba(255,255,255,0.06)",
                        backgroundColor: "rgba(255,255,255,0.02)",
                      }}
                      transition={{ duration: 0.2 }}
                      className="rounded-xl border p-5"
                    >
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <div>
                          <span
                            className="font-mono text-[9px] uppercase tracking-widest font-semibold mb-1 block"
                            style={{ color: step.color }}
                          >
                            {step.label}
                          </span>
                          <h3 className="font-mono text-sm font-semibold text-white">{step.title}</h3>
                        </div>
                        <div
                          className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold shrink-0"
                          style={{
                            color: step.color,
                            backgroundColor: step.color + "15",
                            border: `1px solid ${step.color}25`,
                          }}
                        >
                          {step.icon}
                        </div>
                      </div>

                      <p className="font-mono text-[11px] text-[#A9B4AE]/70 leading-relaxed mb-4">
                        {step.desc}
                      </p>

                      <AnimatePresence>
                        {hoveredStep === step.id && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                            className="overflow-hidden"
                          >
                            <div className="bg-[#061412] border border-white/8 rounded-lg p-3">
                              <pre className="font-mono text-[10px] text-[#6CE8C2]/80 whitespace-pre-wrap leading-relaxed">
                                {step.code}
                              </pre>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* Right: system status */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.3, ease: EASE_OUT_EXPO }}
            className="space-y-4"
          >
            <div className="p-5 bg-white/3 border border-white/6 rounded-xl">
              <p className="font-mono text-[10px] uppercase tracking-widest text-[#A9B4AE]/50 mb-4">
                Active Workflows
              </p>
              <div className="space-y-3">
                {[
                  { name: "High-Value Risk Gate", runs: "342 runs", active: true },
                  { name: "Auto-Approve Micro-Spend", runs: "1,204 runs", active: true },
                  { name: "Duplicate Invoice Alert", runs: "89 runs", active: false },
                ].map((wf, i) => (
                  <div key={i} className="flex items-center justify-between py-2 border-b border-white/5">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-1.5 h-1.5 rounded-full ${wf.active ? "bg-[#6CE8C2] animate-pulse" : "bg-white/20"}`}
                      />
                      <span className="font-mono text-[11px] text-white/70">{wf.name}</span>
                    </div>
                    <span className="font-mono text-[10px] text-[#A9B4AE]/40">{wf.runs}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-5 bg-white/3 border border-white/6 rounded-xl">
              <p className="font-mono text-[10px] uppercase tracking-widest text-[#A9B4AE]/50 mb-4">
                Execution Stats
              </p>
              <div className="space-y-3">
                {[
                  { label: "Success rate", value: "98.4%", good: true },
                  { label: "Avg execution", value: "1.2s", good: true },
                  { label: "Pending approvals", value: "3", good: false },
                ].map((stat, i) => (
                  <div key={i} className="flex justify-between items-center">
                    <span className="font-mono text-[11px] text-[#A9B4AE]/60">{stat.label}</span>
                    <span
                      className="font-mono text-xs font-semibold"
                      style={{ color: stat.good ? "#6CE8C2" : "#F59E0B" }}
                    >
                      {stat.value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
