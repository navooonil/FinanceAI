import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import Hero from "@/components/sections/Hero";
import CopilotShowcase from "@/components/sections/CopilotShowcase";
import AgentArchitecture from "@/components/sections/AgentArchitecture";
import WorkflowBuilder from "@/components/sections/WorkflowBuilder";
import FinanceIntelligence from "@/components/sections/FinanceIntelligence";
import Integrations from "@/components/sections/Integrations";
import Security from "@/components/sections/Security";
import CTA from "@/components/sections/CTA";

export default function Home() {
  return (
    <div className="landing-page-root">
      <Header />
      <Hero />
      <CopilotShowcase />
      <AgentArchitecture />
      <WorkflowBuilder />
      <FinanceIntelligence />
      <Integrations />
      <Security />
      <CTA />
      <Footer />
    </div>
  );
}
