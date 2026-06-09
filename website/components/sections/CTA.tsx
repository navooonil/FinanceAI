"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { EASE_OUT_EXPO } from "@/lib/motion";

export default function CTA() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) setSubmitted(true);
  };

  return (
    <section id="cta" className="relative bg-[#061412] py-40 overflow-hidden">
      {/* Ambient background */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] rounded-full bg-[#6CE8C2]/4 blur-[100px]" />
        <div
          className="absolute inset-0 opacity-[0.015]"
          style={{
            backgroundImage: `radial-gradient(circle, rgba(108,232,194,0.4) 1px, transparent 1px)`,
            backgroundSize: "40px 40px",
          }}
        />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-6 text-center">
        {/* Eyebrow */}
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="font-mono text-[11px] uppercase tracking-widest text-[#6CE8C2]/60 mb-8"
        >
          The Future of Finance Operations
        </motion.p>

        {/* Editorial headline */}
        <motion.h2
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1, ease: EASE_OUT_EXPO }}
          className="font-serif text-[clamp(40px,7vw,88px)] leading-[0.92] font-semibold text-white mb-8"
        >
          Finance operations
          <br />
          <em className="text-[#6CE8C2]">should run themselves.</em>
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.2, ease: EASE_OUT_EXPO }}
          className="font-mono text-[14px] text-[#A9B4AE]/70 max-w-lg mx-auto leading-relaxed mb-12"
        >
          {"Join the waitlist. We're onboarding a limited number of finance teams in our early access cohort."}
        </motion.p>

        {/* Email form */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.35, ease: EASE_OUT_EXPO }}
        >
          {!submitted ? (
            <form
              onSubmit={handleSubmit}
              className="flex flex-col sm:flex-row items-center gap-3 max-w-md mx-auto"
            >
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                required
                className="flex-1 w-full font-mono text-[13px] bg-white/5 border border-white/10 text-white placeholder-white/25 px-5 py-3.5 rounded-xl outline-none focus:border-[#6CE8C2]/40 focus:bg-white/8 transition-all duration-200"
              />
              <motion.button
                type="submit"
                whileHover={{ scale: 1.03, y: -1 }}
                whileTap={{ scale: 0.97 }}
                className="font-mono text-[13px] bg-[#6CE8C2] text-[#061412] font-semibold px-7 py-3.5 rounded-xl hover:bg-[#6CE8C2]/90 transition-colors whitespace-nowrap shadow-lg shadow-[#6CE8C2]/20"
              >
                Request access
              </motion.button>
            </form>
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, ease: EASE_OUT_EXPO }}
              className="inline-flex items-center gap-3 bg-[#6CE8C2]/10 border border-[#6CE8C2]/20 px-6 py-4 rounded-xl"
            >
              <div className="w-2 h-2 rounded-full bg-[#6CE8C2] animate-pulse" />
              <p className="font-mono text-[13px] text-[#6CE8C2]">
                {"You're on the waitlist — we'll be in touch."}
              </p>
            </motion.div>
          )}

          <p className="font-mono text-[10px] text-[#A9B4AE]/30 mt-4">
            No credit card required. Response within 48 hours.
          </p>
        </motion.div>

        {/* Decorative divider */}
        <motion.div
          initial={{ opacity: 0, scaleX: 0 }}
          whileInView={{ opacity: 1, scaleX: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1.2, delay: 0.5, ease: EASE_OUT_EXPO }}
          className="mt-20 w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent origin-center"
        />

        {/* Metrics row */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="mt-12 flex flex-wrap justify-center gap-x-12 gap-y-6"
        >
          {[
            { value: "50+", label: "Finance teams" },
            { value: "99.2%", label: "Agent accuracy" },
            { value: "2,100+", label: "Hours saved / mo" },
            { value: "< 4s", label: "Processing time" },
          ].map((stat) => (
            <div key={stat.label} className="flex flex-col items-center gap-1">
              <span className="font-serif text-3xl font-semibold text-white">{stat.value}</span>
              <span className="font-mono text-[10px] text-[#A9B4AE]/40 uppercase tracking-widest">{stat.label}</span>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
