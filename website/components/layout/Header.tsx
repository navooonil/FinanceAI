"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { EASE_OUT_EXPO } from "@/lib/motion";

const navLinks = [
  { label: "Product", href: "#product" },
  { label: "Agents", href: "#agents" },
  { label: "Intelligence", href: "#intelligence" },
  { label: "Security", href: "#security" },
];

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <motion.header
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: EASE_OUT_EXPO }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled
          ? "bg-[#F7F8F5]/90 backdrop-blur-xl border-b border-[#18362F]/6"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-6 h-6 rounded-md bg-[#18362F] flex items-center justify-center">
            <div className="w-2.5 h-2.5 rounded-sm bg-[#6CE8C2]" />
          </div>
          <span className="font-mono text-sm font-medium text-[#18362F] tracking-tight">
            FinanceAI
          </span>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.label}
              href={link.href}
              className="font-mono text-xs text-[#A9B4AE] hover:text-[#18362F] transition-colors duration-200 tracking-wide"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* CTA */}
        <div className="hidden md:flex items-center gap-4">
          <Link
            href="#"
            className="font-mono text-xs text-[#A9B4AE] hover:text-[#18362F] transition-colors duration-200"
          >
            Sign in
          </Link>
          <motion.a
            href="#cta"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="font-mono text-xs bg-[#18362F] text-[#F7F8F5] px-4 py-2 rounded-lg hover:bg-[#18362F]/90 transition-colors duration-200"
          >
            Request access
          </motion.a>
        </div>

        {/* Mobile menu button */}
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="md:hidden w-8 h-8 flex flex-col items-center justify-center gap-1.5"
          aria-label="Toggle menu"
        >
          <motion.span
            animate={menuOpen ? { rotate: 45, y: 6 } : { rotate: 0, y: 0 }}
            className="w-5 h-px bg-[#18362F] block origin-center transition-all"
          />
          <motion.span
            animate={menuOpen ? { opacity: 0 } : { opacity: 1 }}
            className="w-5 h-px bg-[#18362F] block"
          />
          <motion.span
            animate={menuOpen ? { rotate: -45, y: -6 } : { rotate: 0, y: 0 }}
            className="w-5 h-px bg-[#18362F] block origin-center transition-all"
          />
        </button>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-[#F7F8F5]/95 backdrop-blur-xl border-b border-[#18362F]/6"
          >
            <div className="px-6 py-6 flex flex-col gap-4">
              {navLinks.map((link) => (
                <Link
                  key={link.label}
                  href={link.href}
                  onClick={() => setMenuOpen(false)}
                  className="font-mono text-sm text-[#18362F] hover:text-[#6CE8C2] transition-colors"
                >
                  {link.label}
                </Link>
              ))}
              <a
                href="#cta"
                className="font-mono text-sm bg-[#18362F] text-[#F7F8F5] px-4 py-2.5 rounded-lg text-center mt-2"
              >
                Request access
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
