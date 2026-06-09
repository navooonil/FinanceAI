"use client";

import { useEffect, useRef } from "react";
import { motion, useScroll, useTransform, type Variants } from "framer-motion";
import { gsap } from "gsap";
import { EASE_OUT_EXPO } from "@/lib/motion";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

const floatingCards = [
  {
    id: "ocr",
    tag: "OCR Intelligence",
    status: "Processed",
    statusColor: "#6CE8C2",
    vendor: "Apex Global Logistics",
    invoice: "INV-2026-009",
    amount: "$48,250.00",
    meta: "Confidence 94.2% · Checksums passed",
    delay: 0,
    top: "8%",
    left: "3%",
    floatRange: 10,
  },
  {
    id: "risk",
    tag: "Risk Detection",
    status: "⚠ Flagged",
    statusColor: "#F59E0B",
    vendor: "Z-Axis Engineering Labs",
    invoice: "INV-2026-889",
    amount: "$68,500.00",
    meta: "Risk Grade F · Score 82/100",
    delay: 0.35,
    top: "10%",
    right: "3%",
    floatRange: 14,
  },
  {
    id: "cashflow",
    tag: "Cashflow AI",
    status: "On Track",
    statusColor: "#6CE8C2",
    vendor: "Q3 2026 Projection",
    invoice: "30-day runway",
    amount: "+12.4%",
    meta: "MoM growth · Auto-updated",
    delay: 0.65,
    bottom: "14%",
    left: "6%",
    floatRange: 8,
  },
  {
    id: "workflow",
    tag: "Agent Workflow",
    status: "Completed",
    statusColor: "#6CE8C2",
    vendor: "Planner → Risk → Report",
    invoice: "5 nodes · 3.2s",
    amount: "100%",
    meta: "All agents succeeded",
    delay: 0.9,
    bottom: "12%",
    right: "6%",
    floatRange: 12,
  },
];

const stagger: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12, delayChildren: 0.2 } },
};

const word: Variants = {
  hidden: { opacity: 0, y: 48, filter: "blur(6px)" },
  show: {
    opacity: 1,
    y: 0,
    filter: "blur(0px)",
    transition: { duration: 0.9, ease: EASE_OUT_EXPO },
  },
};

export default function Hero() {
  const containerRef = useRef<HTMLDivElement>(null);
  const vizRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: containerRef });
  const vizY = useTransform(scrollYProgress, [0, 1], [0, -80]);
  const vizScale = useTransform(scrollYProgress, [0, 0.6], [1, 0.96]);
  const textY = useTransform(scrollYProgress, [0, 0.6], [0, -40]);

  // GSAP parallax for the grid dots
  useEffect(() => {
    if (!vizRef.current) return;
    const ctx = gsap.context(() => {
      gsap.to(".hero-grid", {
        yPercent: -20,
        ease: "none",
        scrollTrigger: {
          trigger: containerRef.current,
          start: "top top",
          end: "bottom top",
          scrub: true,
        },
      });
    }, vizRef);
    return () => ctx.revert();
  }, []);

  const headlineWords = ["Your", "AI", "Finance", "Team."];

  return (
    <section
      ref={containerRef}
      className="relative min-h-screen bg-[#F7F8F5] flex flex-col items-center justify-center overflow-hidden pt-24"
    >
      {/* Text content */}
      <motion.div
        style={{ y: textY }}
        className="relative z-10 flex flex-col items-center text-center px-6 max-w-5xl mx-auto"
      >
        {/* Announcement badge */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1, ease: EASE_OUT_EXPO }}
          className="inline-flex items-center gap-2.5 bg-[#18362F]/5 border border-[#18362F]/8 rounded-full px-4 py-1.5 mb-10"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-[#6CE8C2] animate-pulse" />
          <span className="font-mono text-[11px] text-[#18362F]/60 tracking-wide">
            Announcing Multi-Agent Finance Automation v2
          </span>
          <span className="font-mono text-[11px] text-[#6CE8C2]">→</span>
        </motion.div>

        {/* Main headline */}
        <motion.h1
          variants={stagger}
          initial="hidden"
          animate="show"
          className="font-serif text-[clamp(52px,8vw,104px)] leading-[0.92] font-semibold text-[#18362F] tracking-tight mb-8 flex flex-wrap justify-center gap-x-5"
        >
          {headlineWords.map((w, i) => (
            <motion.span key={i} variants={word} className={i === 1 ? "italic text-[#6CE8C2]" : ""}>
              {w}
            </motion.span>
          ))}
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.75, ease: EASE_OUT_EXPO }}
          className="font-mono text-[15px] text-[#A9B4AE] max-w-xl leading-relaxed mb-10"
        >
          Replace repetitive finance operations with intelligent autonomous workflows.
          <br />
          OCR · Risk Analysis · Approvals · Forecasting — all automated.
        </motion.p>

        {/* CTA buttons */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.9, ease: EASE_OUT_EXPO }}
          className="flex flex-col sm:flex-row items-center gap-4"
        >
          <motion.a
            href="#cta"
            whileHover={{ scale: 1.03, y: -1 }}
            whileTap={{ scale: 0.97 }}
            className="font-mono text-[13px] bg-[#18362F] text-[#F7F8F5] px-7 py-3.5 rounded-xl hover:bg-[#18362F]/90 transition-all shadow-lg shadow-[#18362F]/15"
          >
            Request early access
          </motion.a>
          <motion.a
            href="#agents"
            whileHover={{ x: 3 }}
            className="font-mono text-[13px] text-[#18362F]/60 hover:text-[#18362F] flex items-center gap-2 transition-colors"
          >
            See how agents work
            <span className="text-[#6CE8C2]">→</span>
          </motion.a>
        </motion.div>

        {/* Social proof */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1.2 }}
          className="mt-12 flex items-center gap-3 font-mono text-[11px] text-[#A9B4AE]/60"
        >
          <div className="flex -space-x-2">
            {["#18362F", "#2A5247", "#3D7060"].map((c, i) => (
              <div
                key={i}
                className="w-6 h-6 rounded-full border-2 border-[#F7F8F5]"
                style={{ backgroundColor: c }}
              />
            ))}
          </div>
          <span>Trusted by finance teams at 50+ companies</span>
        </motion.div>
      </motion.div>

      {/* Visualization panel */}
      <motion.div
        ref={vizRef}
        style={{ y: vizY, scale: vizScale }}
        initial={{ opacity: 0, y: 60 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1.1, delay: 0.5, ease: EASE_OUT_EXPO }}
        className="relative z-10 w-full max-w-5xl mx-auto px-6 mt-16 pb-24"
      >
        <div className="relative w-full h-[500px] md:h-[560px] bg-white rounded-2xl border border-[#18362F]/5 shadow-[0_8px_64px_rgba(24,54,47,0.07),0_1px_2px_rgba(24,54,47,0.04)] overflow-hidden">
          
          {/* Grid dots background */}
          <div
            className="hero-grid absolute inset-0"
            style={{
              backgroundImage: `radial-gradient(circle, rgba(24,54,47,0.06) 1px, transparent 1px)`,
              backgroundSize: "28px 28px",
            }}
          />

          {/* Center ambient glow */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="w-[400px] h-[300px] rounded-full bg-[#6CE8C2]/8 blur-[80px]" />
          </div>

          {/* SVG connecting lines */}
          <svg
            className="absolute inset-0 w-full h-full pointer-events-none"
            viewBox="0 0 900 560"
            preserveAspectRatio="xMidYMid slice"
          >
            <defs>
              <marker id="dot" viewBox="0 0 4 4" refX="2" refY="2" markerWidth="4" markerHeight="4">
                <circle cx="2" cy="2" r="2" fill="#6CE8C2" />
              </marker>
            </defs>
            {/* OCR → Workflow line */}
            <motion.path
              d="M 240 100 C 380 100 460 480 620 490"
              stroke="#6CE8C2"
              strokeWidth="1"
              strokeDasharray="4 5"
              fill="none"
              opacity={0.5}
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 0.5 }}
              transition={{ duration: 2.5, delay: 1.2, ease: "easeInOut" }}
            />
            {/* Risk → Cashflow line */}
            <motion.path
              d="M 680 120 C 580 260 320 360 180 460"
              stroke="#6CE8C2"
              strokeWidth="1"
              strokeDasharray="4 5"
              fill="none"
              opacity={0.4}
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 0.4 }}
              transition={{ duration: 2.5, delay: 1.6, ease: "easeInOut" }}
            />
            {/* Center hub circle */}
            <motion.circle
              cx="450"
              cy="280"
              r="32"
              stroke="#6CE8C2"
              strokeWidth="1"
              fill="rgba(108,232,194,0.06)"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.8, delay: 1.4 }}
            />
            <motion.text
              x="450"
              y="276"
              textAnchor="middle"
              fontSize="9"
              fontFamily="monospace"
              fill="#18362F"
              opacity={0.5}
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              transition={{ delay: 2 }}
            >
              AI CORE
            </motion.text>
            <motion.text
              x="450"
              y="290"
              textAnchor="middle"
              fontSize="9"
              fontFamily="monospace"
              fill="#18362F"
              opacity={0.5}
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              transition={{ delay: 2 }}
            >
              ACTIVE
            </motion.text>
          </svg>

          {/* Floating Activity Cards */}
          {floatingCards.map((card) => (
            <motion.div
              key={card.id}
              className="absolute w-56 bg-[#F7F8F5]/95 backdrop-blur-sm rounded-xl border border-[#18362F]/6 p-4 shadow-[0_4px_24px_rgba(24,54,47,0.08)]"
              style={{
                top: card.top,
                bottom: card.bottom,
                left: card.left,
                right: card.right,
              }}
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{
                opacity: 1,
                scale: 1,
                y: [0, -card.floatRange, 0],
              }}
              transition={{
                opacity: { duration: 0.6, delay: 1.0 + card.delay },
                scale: { duration: 0.6, delay: 1.0 + card.delay },
                y: {
                  duration: 4 + card.delay * 0.5,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 1.5 + card.delay,
                },
              }}
            >
              {/* Tag row */}
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-[9px] uppercase tracking-widest text-[#A9B4AE]">
                  {card.tag}
                </span>
                <span
                  className="font-mono text-[9px] font-medium"
                  style={{ color: card.statusColor }}
                >
                  {card.status}
                </span>
              </div>

              {/* Vendor / title */}
              <p className="font-mono text-[11px] font-medium text-[#18362F] truncate mb-0.5">
                {card.vendor}
              </p>
              <p className="font-mono text-[10px] text-[#A9B4AE] mb-3">{card.invoice}</p>

              {/* Divider */}
              <div className="border-t border-[#18362F]/5 pt-2.5 flex items-center justify-between">
                <span className="font-mono text-[13px] font-semibold text-[#18362F]">
                  {card.amount}
                </span>
                <span className="font-mono text-[9px] text-[#A9B4AE]/70 text-right max-w-[90px] leading-tight">
                  {card.meta}
                </span>
              </div>
            </motion.div>
          ))}

          {/* Central status indicator */}
          <motion.div
            className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 2 }}
          >
            <motion.div
              animate={{
                boxShadow: [
                  "0 0 0 0 rgba(108,232,194,0.3)",
                  "0 0 0 20px rgba(108,232,194,0)",
                ],
              }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-8 h-8 rounded-full bg-[#6CE8C2]/15 border border-[#6CE8C2]/30 flex items-center justify-center"
            >
              <div className="w-2 h-2 rounded-full bg-[#6CE8C2]" />
            </motion.div>
          </motion.div>

          {/* Bottom stats bar */}
          <div className="absolute bottom-0 left-0 right-0 border-t border-[#18362F]/5 bg-white/60 backdrop-blur-sm flex items-center px-6 py-3 gap-8">
            {[
              { label: "Invoices Processed", value: "12,847" },
              { label: "Anomalies Caught", value: "340" },
              { label: "Hours Saved / mo", value: "2,100+" },
              { label: "Workflow Accuracy", value: "99.2%" },
            ].map((stat) => (
              <div key={stat.label} className="flex items-center gap-3">
                <span className="font-mono text-xs font-semibold text-[#18362F]">{stat.value}</span>
                <span className="font-mono text-[10px] text-[#A9B4AE]">{stat.label}</span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </section>
  );
}

