"use client";

import { motion } from "framer-motion";
import { EASE_OUT_EXPO } from "@/lib/motion";

const integrations = [
  { name: "QuickBooks", category: "Accounting", angle: 0 },
  { name: "NetSuite", category: "ERP", angle: 51.4 },
  { name: "Xero", category: "Accounting", angle: 102.8 },
  { name: "Slack", category: "Notifications", angle: 154.2 },
  { name: "Stripe", category: "Payments", angle: 205.7 },
  { name: "SAP", category: "ERP", angle: 257.1 },
  { name: "Email", category: "Notifications", angle: 308.5 },
];

function polarToXY(angleDeg: number, radius: number) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return {
    x: 220 + radius * Math.cos(rad),
    y: 220 + radius * Math.sin(rad),
  };
}

export default function Integrations() {
  return (
    <section className="bg-[#F7F8F5] py-32">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="font-mono text-[11px] uppercase tracking-widest text-[#6CE8C2] mb-4"
          >
            Integrations
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1, ease: EASE_OUT_EXPO }}
            className="font-serif text-[clamp(36px,5vw,56px)] leading-[0.95] font-semibold text-[#18362F] mb-4"
          >
            Connects to your{" "}
            <span className="text-[#A9B4AE]">existing stack.</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="font-mono text-[13px] text-[#A9B4AE] leading-relaxed"
          >
            Drop into your existing workflows with zero disruption. Native connectors for accounting software, ERPs, and communication platforms.
          </motion.p>
        </div>

        {/* Radial graph */}
        <div className="relative flex justify-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.9, ease: EASE_OUT_EXPO }}
            className="relative w-full max-w-[440px] aspect-square"
          >
            <svg viewBox="0 0 440 440" className="w-full h-full">
              {/* Outer ring */}
              <motion.circle
                cx="220"
                cy="220"
                r="168"
                stroke="#18362F"
                strokeWidth="0.5"
                strokeOpacity="0.08"
                fill="none"
                initial={{ pathLength: 0 }}
                whileInView={{ pathLength: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 1.5, ease: "easeInOut" }}
              />
              {/* Inner ring */}
              <circle cx="220" cy="220" r="100" stroke="#18362F" strokeWidth="0.5" strokeOpacity="0.05" fill="none" />

              {/* Connection lines with animated travel dots */}
              {integrations.map((intg, i) => {
                const { x, y } = polarToXY(intg.angle, 168);
                return (
                  <g key={intg.name}>
                    <motion.line
                      x1="220"
                      y1="220"
                      x2={x}
                      y2={y}
                      stroke="#6CE8C2"
                      strokeWidth="0.8"
                      strokeOpacity="0.25"
                      strokeDasharray="3 4"
                      initial={{ opacity: 0 }}
                      whileInView={{ opacity: 1 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.5, delay: 0.8 + i * 0.1 }}
                    />
                    {/* Traveling dot */}
                    <motion.circle
                      r="2"
                      fill="#6CE8C2"
                      initial={{ cx: 220, cy: 220, opacity: 0 }}
                      animate={{
                        cx: [220, x, 220],
                        cy: [220, y, 220],
                        opacity: [0, 0.8, 0],
                      }}
                      transition={{
                        duration: 2.5,
                        delay: 1.5 + i * 0.35,
                        repeat: Infinity,
                        ease: "easeInOut",
                      }}
                    />
                  </g>
                );
              })}

              {/* Integration nodes */}
              {integrations.map((intg, i) => {
                const { x, y } = polarToXY(intg.angle, 168);
                return (
                  <motion.g
                    key={intg.name}
                    initial={{ opacity: 0, scale: 0 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: 0.9 + i * 0.1, ease: EASE_OUT_EXPO }}
                    style={{ transformOrigin: `${x}px ${y}px` }}
                  >
                    <circle cx={x} cy={y} r="28" fill="white" stroke="#18362F" strokeWidth="0.5" strokeOpacity="0.1" />
                    <circle cx={x} cy={y} r="28" fill="none" stroke="#6CE8C2" strokeWidth="0" />
                    <text x={x} y={y - 3} textAnchor="middle" fontSize="8" fontFamily="monospace" fill="#18362F" fontWeight="600">
                      {intg.name}
                    </text>
                    <text x={x} y={y + 9} textAnchor="middle" fontSize="6.5" fontFamily="monospace" fill="#A9B4AE">
                      {intg.category}
                    </text>
                  </motion.g>
                );
              })}

              {/* Center hub */}
              <motion.g
                initial={{ opacity: 0, scale: 0 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.5, ease: EASE_OUT_EXPO }}
                style={{ transformOrigin: "220px 220px" }}
              >
                <circle cx="220" cy="220" r="44" fill="#18362F" />
                <motion.circle
                  cx="220"
                  cy="220"
                  r="44"
                  fill="none"
                  stroke="#6CE8C2"
                  strokeWidth="1"
                  strokeOpacity="0.3"
                  animate={{ r: [44, 54, 44], opacity: [0.3, 0, 0.3] }}
                  transition={{ duration: 2.5, repeat: Infinity }}
                />
                <text x="220" y="216" textAnchor="middle" fontSize="9" fontFamily="monospace" fill="white" fontWeight="600">
                  FinanceAI
                </text>
                <text x="220" y="228" textAnchor="middle" fontSize="7" fontFamily="monospace" fill="#6CE8C2" fillOpacity="0.7">
                  CORE
                </text>
              </motion.g>
            </svg>
          </motion.div>
        </div>

        {/* Feature callouts below */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-16">
          {[
            { icon: "⚡", title: "Real-time sync", desc: "Changes in QuickBooks or NetSuite reflect in FinanceAI instantly via webhooks." },
            { icon: "🔌", title: "REST + webhooks", desc: "Full public API with OpenAPI spec. Register webhooks for any platform event." },
            { icon: "🔑", title: "OAuth 2.0", desc: "Secure credential handling with encrypted token storage and automatic refresh." },
          ].map((f, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.12 }}
              whileHover={{ y: -2, borderColor: "rgba(108,232,194,0.2)" }}
              className="p-5 bg-white border border-[#18362F]/6 rounded-xl shadow-[0_2px_12px_rgba(24,54,47,0.04)] transition-all duration-200"
            >
              <div className="text-xl mb-3">{f.icon}</div>
              <h3 className="font-mono text-xs font-semibold text-[#18362F] mb-1.5">{f.title}</h3>
              <p className="font-mono text-[11px] text-[#A9B4AE] leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
