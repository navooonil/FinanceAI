"use client";

import { motion } from "framer-motion";
import { EASE_OUT_EXPO } from "@/lib/motion";

const trustBadges = [
  { label: "SOC 2 Type II", sub: "Audited annually", icon: "🛡" },
  { label: "ISO 27001", sub: "Information security", icon: "✓" },
  { label: "GDPR Compliant", sub: "EU data protection", icon: "⚖" },
  { label: "256-bit AES", sub: "End-to-end encryption", icon: "🔒" },
  { label: "Multi-tenant isolation", sub: "Row-level security", icon: "⬜" },
  { label: "99.9% uptime SLA", sub: "Enterprise SLA", icon: "◎" },
];

const securityFeatures = [
  {
    title: "Zero-trust architecture",
    desc: "Every request is authenticated and authorized at the row level. No service has implicit trust.",
  },
  {
    title: "Tenant data isolation",
    desc: "PostgreSQL row-level security ensures company data is never accessible across tenants.",
  },
  {
    title: "Audit log trail",
    desc: "Every workflow execution, approval, and AI query is immutably logged with timestamps and actor IDs.",
  },
  {
    title: "RBAC + JWT",
    desc: "Role-based access control with short-lived JWT tokens and refresh token rotation.",
  },
];

export default function Security() {
  return (
    <section id="security" className="bg-[#F7F8F5] py-32">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
          <div>
            <motion.p
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="font-mono text-[11px] uppercase tracking-widest text-[#6CE8C2] mb-4"
            >
              Security & Compliance
            </motion.p>
            <motion.h2
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, delay: 0.1, ease: EASE_OUT_EXPO }}
              className="font-serif text-[clamp(36px,5vw,56px)] leading-[0.95] font-semibold text-[#18362F] mb-6"
            >
              Enterprise-grade
              <br />
              <span className="text-[#A9B4AE]">from day one.</span>
            </motion.h2>
            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="font-mono text-[13px] text-[#A9B4AE] leading-relaxed mb-10"
            >
              Built for finance teams that require institutional-grade security, compliance, and operational transparency.
            </motion.p>

            {/* Security feature list */}
            <div className="space-y-5">
              {securityFeatures.map((feature, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.2 + i * 0.1, ease: EASE_OUT_EXPO }}
                  className="flex gap-4"
                >
                  <div className="w-1 shrink-0 rounded-full bg-gradient-to-b from-[#6CE8C2] to-[#6CE8C2]/20 mt-1" style={{ height: 44 }} />
                  <div>
                    <h3 className="font-mono text-xs font-semibold text-[#18362F] mb-1">{feature.title}</h3>
                    <p className="font-mono text-[11px] text-[#A9B4AE] leading-relaxed">{feature.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Right: trust badges */}
          <div>
            <div className="grid grid-cols-2 gap-3">
              {trustBadges.map((badge, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20, scale: 0.95 }}
                  whileInView={{ opacity: 1, y: 0, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: 0.1 + i * 0.08, ease: EASE_OUT_EXPO }}
                  whileHover={{ y: -3, boxShadow: "0 8px 32px rgba(24,54,47,0.10)" }}
                  className="bg-white border border-[#18362F]/6 rounded-xl p-5 shadow-[0_2px_12px_rgba(24,54,47,0.04)] transition-all duration-200 cursor-default"
                >
                  <div className="text-2xl mb-3">{badge.icon}</div>
                  <h3 className="font-mono text-xs font-semibold text-[#18362F] mb-1">{badge.label}</h3>
                  <p className="font-mono text-[10px] text-[#A9B4AE]">{badge.sub}</p>
                </motion.div>
              ))}
            </div>

            {/* Compliance note */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.6 }}
              className="mt-4 p-4 bg-[#18362F]/4 border border-[#18362F]/8 rounded-xl"
            >
              <p className="font-mono text-[10px] text-[#18362F]/60 leading-relaxed">
                Security audits available under NDA.
                All data is encrypted at rest and in transit.
                Penetration tests conducted quarterly.
              </p>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
