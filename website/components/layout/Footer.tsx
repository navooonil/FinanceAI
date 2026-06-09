import Link from "next/link";


const footerLinks = {
  Product: ["OCR Intelligence", "AI Copilot", "Agent Workflows", "Vendor Risk", "Cashflow AI"],
  Company: ["About", "Blog", "Careers", "Press"],
  Developers: ["Documentation", "API Reference", "Status", "Changelog"],
  Legal: ["Privacy", "Terms", "Security", "GDPR"],
};

export default function Footer() {
  return (
    <footer className="bg-[#061412] text-[#A9B4AE] pt-20 pb-10">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-12 pb-16 border-b border-white/6">
          {/* Brand */}
          <div className="md:col-span-1">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-6 h-6 rounded-md bg-[#6CE8C2]/20 flex items-center justify-center">
                <div className="w-2.5 h-2.5 rounded-sm bg-[#6CE8C2]" />
              </div>
              <span className="font-mono text-sm font-medium text-white tracking-tight">
                FinanceAI
              </span>
            </div>
            <p className="font-mono text-xs text-[#A9B4AE]/70 leading-relaxed max-w-[180px]">
              Autonomous finance operations for modern enterprises.
            </p>
          </div>

          {/* Links */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h4 className="font-mono text-[10px] uppercase tracking-widest text-[#A9B4AE]/50 mb-4">
                {category}
              </h4>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link}>
                    <Link
                      href="#"
                      className="font-mono text-xs text-[#A9B4AE]/70 hover:text-[#6CE8C2] transition-colors duration-200"
                    >
                      {link}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="font-mono text-[10px] text-[#A9B4AE]/40 tracking-wide">
            © {new Date().getFullYear()} FinanceAI Inc. All rights reserved.
          </p>
          <div className="flex items-center gap-6">
            {["Twitter", "LinkedIn", "GitHub"].map((social) => (
              <Link
                key={social}
                href="#"
                className="font-mono text-[10px] text-[#A9B4AE]/40 hover:text-[#6CE8C2] transition-colors duration-200"
              >
                {social}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
