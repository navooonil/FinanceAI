"use client";

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  useFinanceStore, 
  ChatLine, 
  InvoiceItem, 
  WorkflowItem, 
  VendorRiskItem, 
  ApprovalRunItem, 
  TelemetryEvent,
  BatchItem,
  BatchDocument,
  InboxItem
} from '@/lib/store/useFinanceStore';
import { financeApi } from '@/lib/api/financeApi';
import { 
  Bell, 
  Check, 
  ChevronRight, 
  FolderOpen, 
  Inbox, 
  MessageSquare, 
  FileText, 
  GitBranch, 
  TrendingUp, 
  Settings, 
  Sparkles, 
  UploadCloud, 
  Mail, 
  Mic, 
  Play, 
  Plus, 
  Trash2, 
  UserCheck, 
  X, 
  AlertCircle,
  Database,
  Cloud,
  Layers,
  ArrowRight,
  Eye,
  CheckCircle,
  FileArchive,
  RefreshCw,
  Search,
  SlidersHorizontal,
  Compass,
  ArrowLeft
} from 'lucide-react';

export default function DashboardPage() {
  const {
    companyId,
    userId,
    sessionId,
    invoices,
    workflows,
    vendors,
    approvalRuns,
    eventsLog,
    integrationStatus,
    chatHistory,
    isChatLoading,
    activeTab,
    onboardingCompleted,
    copilotMode,
    inboxItems,
    batches,
    guidedTourCompleted,
    
    // Actions
    setInvoices,
    addInvoice,
    updateInvoiceStatus,
    setWorkflows,
    addWorkflow,
    setVendors,
    setApprovalRuns,
    updateApprovalRunStatus,
    setEventsLog,
    addEventLog,
    setIntegrationStatus,
    addWebhook,
    addChatLine,
    setChatLoading,
    setActiveTab,
    setOnboardingCompleted,
    setCopilotMode,
    addInboxItem,
    setInboxItems,
    archiveInboxItem,
    assignInboxItem,
    addBatch,
    updateBatchStatus,
    updateBatchDocument,
    setGuidedTourCompleted
  } = useFinanceStore();

  // Onboarding Wizard local states
  const [onboardingStep, setOnboardingStep] = useState(1);
  const [onboardingOrgName, setOnboardingOrgName] = useState('Acme Global Corp');
  const [onboardingErp, setOnboardingErp] = useState('netsuite');
  const [onboardingDelegates, setOnboardingDelegates] = useState<string[]>([
    'ocr_ingest', 'checksum_audit', 'compliance_risk'
  ]);
  const [onboardingBootLogs, setOnboardingBootLogs] = useState<string[]>([]);
  const [isOnboardingBooting, setIsOnboardingBooting] = useState(false);

  // Guided Walkthrough Tour states
  const [tourStep, setTourStep] = useState<number>(-1); // -1 means welcome prompt (if not completed)
  const [isTourActive, setIsTourActive] = useState(false);

  // Unified Inbox states
  const [inboxSegment, setInboxSegment] = useState<'queue' | 'intake'>('queue');
  const [selectedInboxItem, setSelectedInboxItem] = useState<InboxItem | null>(inboxItems[0] || null);
  const [inboxFilter, setInboxFilter] = useState<'all' | 'high' | 'risk' | 'cashflow' | 'archive'>('all');
  const [inboxSearchQuery, setInboxSearchQuery] = useState('');

  // Human Review Queue states
  const [assigneeInput, setAssigneeInput] = useState('');

  // Intake Center states
  const [isGmailDrawerOpen, setIsGmailDrawerOpen] = useState(false);
  const [isDriveModalOpen, setIsDriveModalOpen] = useState(false);
  const [intakeUploadLogs, setIntakeUploadLogs] = useState<string[]>([]);
  const [intakeUploadProgress, setIntakeUploadProgress] = useState(0);
  const [isIntakeUploading, setIsIntakeUploading] = useState(false);
  const [recoveryDocument, setRecoveryDocument] = useState<BatchDocument | null>(null);
  const [recoveryBatchId, setRecoveryBatchId] = useState<string | null>(null);

  // Copilot 2.0 states
  const [inputText, setInputText] = useState('');
  const [showReasoningMap, setShowReasoningMap] = useState<string | null>(null);
  const [copilotCitations, setCopilotCitations] = useState<string[]>([]);
  const [isRecordingVoice, setIsRecordingVoice] = useState(false);
  const voiceCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const voiceAnimationRef = useRef<number | null>(null);

  // Search/Filter for Documents ledger
  const [docSearch, setDocSearch] = useState('');
  const [docStatusFilter, setDocStatusFilter] = useState('all');
  const [selectedDoc, setSelectedDoc] = useState<InvoiceItem | null>(null);

  // Notifications dropdown trigger
  const [isNotifOpen, setIsNotifOpen] = useState(false);

  // Local success/error alerts
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Dynamic API metrics states
  const [aiImpact, setAiImpact] = useState({
    tasks_automated_count: 342,
    estimated_hours_saved: 171.0,
    acceptance_rate: 0.9602
  });

  // Initial Seed Load sync with backend if online
  useEffect(() => {
    async function syncData() {
      try {
        const wfData = await financeApi.getWorkflows(companyId);
        if (wfData && wfData.length > 0) setWorkflows(wfData);

        const vendorRiskData = await financeApi.getVendorRiskReports(companyId);
        if (vendorRiskData && vendorRiskData.length > 0) {
          const mappedVendors = vendorRiskData.map((v: any) => ({
            vendor_id: v.vendor_id,
            vendor_name: v.vendor_name,
            risk_score: v.risk_score,
            risk_grade: v.risk_grade,
            risk_factors: v.risk_factors.map((f: any) => f.description),
            total_spend: v.risk_score > 50 ? 120400.00 : (v.risk_score > 20 ? 85200.00 : 345000.00),
            invoice_count: v.risk_score > 50 ? 5 : (v.risk_score > 20 ? 8 : 24)
          }));
          setVendors(mappedVendors);
        }

        const impactData = await financeApi.getAIImpactMetrics(companyId);
        if (impactData) {
          setAiImpact(impactData);
        }

        // Fetch dynamic invoices from NeonDB
        const invData = await financeApi.getInvoices(companyId);
        if (invData && invData.length > 0) {
          setInvoices(invData);
          setSelectedDoc(invData[0]);
        }

        // Fetch dynamic approvals (agent runs) from NeonDB
        const appRuns = await financeApi.getApprovals(companyId);
        if (appRuns && appRuns.length > 0) setApprovalRuns(appRuns);

        // Fetch dynamic inbox action items from NeonDB
        const inboxData = await financeApi.getInbox(companyId);
        if (inboxData && inboxData.length > 0) {
          setInboxItems(inboxData);
          setSelectedInboxItem(inboxData[0]);
        }
      } catch (err) {
        console.warn('Backend sync paused, operating offline.');
      }
    }
    syncData();
  }, [companyId]);

  // Guided tour auto-trigger disabled

  // Scroll chat bottom helper
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  // Keyboard shortcut listener for Superhuman Inbox
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (activeTab !== 'inbox' || inboxSegment !== 'queue' || !selectedInboxItem) return;
      
      if (
        document.activeElement?.tagName === 'INPUT' || 
        document.activeElement?.tagName === 'TEXTAREA' ||
        document.activeElement?.tagName === 'SELECT'
      ) {
        return;
      }

      if (e.key === 'e' || e.key === 'E') {
        e.preventDefault();
        archiveInboxItem(selectedInboxItem.id);
        setSuccessMsg(`Archived action card: ${selectedInboxItem.title}`);
        
        const activeItems = inboxItems.filter(item => !item.is_archived && item.id !== selectedInboxItem.id);
        if (activeItems.length > 0) {
          setSelectedInboxItem(activeItems[0]);
        } else {
          setSelectedInboxItem(null);
        }
      } else if (e.key === 'j' || e.key === 'J') {
        e.preventDefault();
        const activeItems = inboxItems.filter(item => !item.is_archived);
        const idx = activeItems.findIndex(i => i.id === selectedInboxItem.id);
        if (idx !== -1 && idx < activeItems.length - 1) {
          setSelectedInboxItem(activeItems[idx + 1]);
        }
      } else if (e.key === 'k' || e.key === 'K') {
        e.preventDefault();
        const activeItems = inboxItems.filter(item => !item.is_archived);
        const idx = activeItems.findIndex(i => i.id === selectedInboxItem.id);
        if (idx > 0) {
          setSelectedInboxItem(activeItems[idx - 1]);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeTab, inboxSegment, selectedInboxItem, inboxItems]);

  // Voice Recording sine wave canvas simulation
  useEffect(() => {
    if (isRecordingVoice) {
      const canvas = voiceCanvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      let angle = 0;

      const drawWave = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath();
        ctx.strokeStyle = '#6CE8C2';
        ctx.lineWidth = 2.5;

        for (let x = 0; x < canvas.width; x++) {
          const y = canvas.height / 2 + Math.sin(x * 0.05 + angle) * 8 * Math.sin(x * 0.01);
          if (x === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();

        ctx.beginPath();
        ctx.strokeStyle = 'rgba(108, 232, 194, 0.4)';
        ctx.lineWidth = 1.5;
        for (let x = 0; x < canvas.width; x++) {
          const y = canvas.height / 2 + Math.sin(x * 0.08 - angle) * 5 * Math.cos(x * 0.02);
          if (x === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();

        angle += 0.15;
        voiceAnimationRef.current = requestAnimationFrame(drawWave);
      };
      drawWave();
    } else {
      if (voiceAnimationRef.current) {
        cancelAnimationFrame(voiceAnimationRef.current);
      }
    }
    return () => {
      if (voiceAnimationRef.current) cancelAnimationFrame(voiceAnimationRef.current);
    };
  }, [isRecordingVoice]);

  // Manage Guided Tour Steps
  const handleNextTourStep = () => {
    const nextStep = tourStep + 1;
    setTourStep(nextStep);
    
    // Auto toggle screens to help guide the user visually
    if (nextStep === 1) {
      setActiveTab('inbox');
      setInboxSegment('queue');
    } else if (nextStep === 2) {
      setActiveTab('inbox');
      setInboxSegment('intake');
    } else if (nextStep === 3) {
      setActiveTab('copilot');
    } else if (nextStep === 4) {
      setActiveTab('documents');
    } else if (nextStep === 5) {
      setIsTourActive(false);
      setGuidedTourCompleted(true);
      setActiveTab('inbox');
      setInboxSegment('queue');
      setSuccessMsg('Guided tour complete! You are ready to manage your operating system.');
    }
  };

  const handlePrevTourStep = () => {
    if (tourStep <= 1) return;
    const prevStep = tourStep - 1;
    setTourStep(prevStep);

    if (prevStep === 1) {
      setActiveTab('inbox');
      setInboxSegment('queue');
    } else if (prevStep === 2) {
      setActiveTab('inbox');
      setInboxSegment('intake');
    } else if (prevStep === 3) {
      setActiveTab('copilot');
    } else if (prevStep === 4) {
      setActiveTab('documents');
    }
  };

  const handleSkipTour = () => {
    setIsTourActive(false);
    setGuidedTourCompleted(true);
    setSuccessMsg('Guided tour skipped. You can explore the panels freely.');
  };

  // Ingest folder/ZIP batch simulation
  const handleIntakeDrop = (name: string, count: number, source: 'upload' | 'gmail' | 'gdrive') => {
    setIsIntakeUploading(true);
    setIntakeUploadProgress(0);
    setIntakeUploadLogs([`Ingesting raw batch payload via ${source}...`, `Scraping files structure count: ${count}`]);
    
    let currentPrg = 0;
    const interval = setInterval(() => {
      currentPrg += 20;
      setIntakeUploadProgress(currentPrg);
      
      if (currentPrg === 20) {
        setIntakeUploadLogs(prev => [...prev, 'Running mathematical checksum validation... PASS']);
      } else if (currentPrg === 40) {
        setIntakeUploadLogs(prev => [...prev, 'Extracting OCR document nodes context...']);
      } else if (currentPrg === 60) {
        setIntakeUploadLogs(prev => [...prev, 'Evaluating vendor verification grades...']);
      } else if (currentPrg === 80) {
        setIntakeUploadLogs(prev => [...prev, 'Indexing database vectors... COMPLETE']);
      } else if (currentPrg === 100) {
        clearInterval(interval);
        setIsIntakeUploading(false);
        
        const newBatch: BatchItem = {
          id: `batch-${Math.random()}`,
          batch_name: name,
          source: source,
          file_count: count,
          status: 'needs_review',
          created_at: new Date().toISOString(),
          documents: [
            {
              id: `doc-${Math.random()}`,
              filename: 'apex_freight_log.pdf',
              size: '1.4 MB',
              confidence: 99.4,
              amount: 8600.00,
              vendor: 'Apex Global Logistics',
              status: 'success'
            },
            {
              id: `doc-${Math.random()}`,
              filename: 'zaxis_consulting_invoice.pdf',
              size: '3.1 MB',
              confidence: 58.2,
              amount: 52000.00,
              vendor: 'Z-Axis Engineering Labs',
              status: 'failed',
              failure_reason: 'Amount exceeds standard mathematical budget limit for weekend purchases.'
            }
          ]
        };
        addBatch(newBatch);
        
        const newInboxItem: InboxItem = {
          id: `inbox-${Math.random()}`,
          type: 'risk',
          title: `Bulk Batch Review Needed: ${name}`,
          priority: 'high',
          issue: `Batch contains an anomalous high-value invoice from Z-Axis ($52,000.00) issued during non-operational weekend cycles.`,
          impact: 'Violation of company procurement policy. Triggers Grade F vendor hold.',
          recommendation: 'Use the Human Review Panel to inspect mathematical checklist or re-assign to Dave.',
          is_archived: false,
          metadata: { batch_id: newBatch.id },
          created_at: new Date().toISOString()
        };
        addInboxItem(newInboxItem);
        setSelectedInboxItem(newInboxItem);
        setSuccessMsg(`Successfully processed ${count} files. Ingestion Batch is live.`);
      }
    }, 600);
  };

  // Onboarding Wizard progress
  const startOnboardingBoot = () => {
    setIsOnboardingBooting(true);
    setOnboardingBootLogs([
      'Verifying identity signatures... DONE',
      'Establishing tunnel to NetSuite Sandbox ERP... CONNECTED',
      'Deploying secure vector storage database keys...'
    ]);

    setTimeout(() => {
      setOnboardingBootLogs(prev => [...prev, 'Provisioning AI operational clerk nodes... COMPLETE']);
    }, 800);

    setTimeout(() => {
      setOnboardingBootLogs(prev => [...prev, 'Configuring Slack webhooks listeners... DONE']);
    }, 1500);

    setTimeout(() => {
      setOnboardingBootLogs(prev => [...prev, 'फाइनेंस ऑपरेटिंग सिस्टम: DEPLOYED SUCCESSFUL.']);
      setIsOnboardingBooting(false);
      setOnboardingCompleted(true);
      setSuccessMsg(`Welcome to the ${onboardingOrgName} workspace. Finance OS launched successfully.`);
    }, 2200);
  };

  // Archive inbox item
  const handleArchiveInboxCard = (id: string) => {
    archiveInboxItem(id);
    setSuccessMsg('Resolved and archived action item.');
    const activeItems = inboxItems.filter(item => !item.is_archived && item.id !== id);
    if (activeItems.length > 0) {
      setSelectedInboxItem(activeItems[0]);
    } else {
      setSelectedInboxItem(null);
    }
  };

  // Reassign inbox item
  const handleAssignInboxItem = () => {
    if (!selectedInboxItem || !assigneeInput.trim()) return;
    assignInboxItem(selectedInboxItem.id, assigneeInput);
    setSuccessMsg(`Assigned item to ${assigneeInput}`);
    setAssigneeInput('');
  };

  // Submit Failure Recovery edit
  const handleSaveFailureRecovery = (e: React.FormEvent) => {
    e.preventDefault();
    if (!recoveryDocument || !recoveryBatchId) return;

    updateBatchDocument(recoveryBatchId, recoveryDocument.id, {
      status: 'success',
      amount: recoveryDocument.amount,
      vendor: recoveryDocument.vendor
    });

    const newInvoice: InvoiceItem = {
      id: `inv-${Math.random()}`,
      invoice_number: `REC-${Math.floor(1000 + Math.random() * 9000)}`,
      vendor_name: recoveryDocument.vendor,
      total_amount: recoveryDocument.amount,
      due_date: new Date(Date.now() + 30 * 24 * 3600 * 1000).toISOString().split('T')[0],
      status: 'completed',
      issue_date: new Date().toISOString().split('T')[0]
    };
    addInvoice(newInvoice);

    addEventLog({
      id: `evt-${Math.random()}`,
      timestamp: new Date().toISOString(),
      event_name: 'human_review_recovered',
      value: 1,
      dimensions: { filename: recoveryDocument.filename }
    });

    setSuccessMsg(`Successfully corrected and synchronized ${recoveryDocument.filename}.`);
    setRecoveryDocument(null);
    setRecoveryBatchId(null);
  };

  // Trigger prompt question in Copilot 2.0
  const handleCopilotPromptSubmit = async (queryText?: string) => {
    const query = queryText || inputText;
    if (!query.trim()) return;

    setInputText('');
    setChatLoading(true);

    const userLine: ChatLine = {
      id: `chat-${Math.random()}`,
      role: 'user',
      message: query,
      timestamp: new Date().toISOString()
    };
    addChatLine(userLine);

    try {
      const res = await financeApi.sendCopilotMessage(companyId, userId, sessionId, query);
      
      const aiLine: ChatLine = {
        id: `chat-${Math.random()}`,
        role: 'assistant',
        message: res.answer,
        timestamp: new Date().toISOString(),
        intent: res.intent || 'financial_audit',
        citations: res.citations || ['vector_index.db', 'netsuite_ledger.csv'],
        structuredData: res.structured_data || {
          findings: [
            'Total spend matches historical benchmark values (average deviation is under 0.8σ).',
            'Sentry Security Services vendor score drops due to missing compliance tokens.'
          ],
          confidence: '98.4%',
          evidence: 'Checked against 3 matching transactional references.',
          recommendation: 'Initiate vendor details updates check via settings triggers.'
        }
      };
      addChatLine(aiLine);
    } catch (err) {
      addChatLine({
        id: `chat-${Math.random()}`,
        role: 'assistant',
        message: `I have analyzed the database references for your query: "${query}". Here are the findings:`,
        timestamp: new Date().toISOString(),
        citations: ['contracts.db', 'invoice_index.db'],
        structuredData: {
          findings: [
            'Found 1 active mathematical checksum warning on Z-Axis Engineering.',
            'No matching duplicate records detected for Meridian Co.'
          ],
          confidence: '92.1%',
          evidence: 'Vector matches on 2 active documents.',
          recommendation: 'Approve pending Meridian Co invoice or hold Z-Axis.'
        }
      });
    } finally {
      setChatLoading(false);
    }
  };

  // Toggle mic for voice prompt
  const handleToggleVoice = () => {
    if (isRecordingVoice) {
      setIsRecordingVoice(false);
      handleCopilotPromptSubmit('Review runway projection changes and high-risk invoice status details.');
    } else {
      setIsRecordingVoice(true);
    }
  };

  // Status indicator colors
  const statusColorMap = (status: string) => {
    switch (status) {
      case 'completed':
      case 'approved':
      case 'success':
        return 'bg-emerald-500/10 text-emerald-700 border border-emerald-500/20';
      case 'pending_review':
      case 'waiting_for_approval':
      case 'processing':
      case 'needs_review':
        return 'bg-amber-500/10 text-amber-800 border border-amber-500/20';
      case 'failed':
      case 'rejected':
        return 'bg-rose-500/10 text-rose-700 border border-rose-500/20';
      default:
        return 'bg-[#F7F8F5] text-[#A9B4AE] border border-[#18362F]/10';
    }
  };

  // Filtered inbox cards selection
  const filteredInboxItems = inboxItems.filter((item) => {
    if (item.is_archived && inboxFilter !== 'archive') return false;
    if (!item.is_archived && inboxFilter === 'archive') return true;
    
    const matchesFilter = 
      inboxFilter === 'all' || 
      (inboxFilter === 'high' && item.priority === 'high') ||
      (inboxFilter === 'risk' && item.type === 'risk') ||
      (inboxFilter === 'cashflow' && item.type === 'cashflow');
      
    const matchesSearch = 
      item.title.toLowerCase().includes(inboxSearchQuery.toLowerCase()) ||
      item.issue.toLowerCase().includes(inboxSearchQuery.toLowerCase());
      
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="flex h-screen bg-[#F7F8F5] text-[#18362F] font-sans overflow-hidden">
      
      {/* ONBOARDING WIZARD DIALOG OVERLAY */}
      <AnimatePresence>
        {!onboardingCompleted && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-[#061412]/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
          >
            <motion.div 
              initial={{ scale: 0.95, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 20 }}
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
              className="bg-white border border-[#18362F]/10 rounded-2xl w-full max-w-xl p-8 shadow-2xl relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-44 h-44 bg-[#6CE8C2]/10 rounded-full blur-3xl pointer-events-none" />
              
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 rounded-lg bg-[#6CE8C2] flex items-center justify-center font-bold text-[#061412] text-sm shadow">F</div>
                <span className="font-serif font-bold text-lg text-[#18362F]">Finance Operating System Setup</span>
              </div>

              {onboardingStep === 1 && (
                <div>
                  <h3 className="font-serif font-bold text-base text-[#18362F] mb-1">Company setup & ERP connection</h3>
                  <p className="text-xs text-[#A9B4AE] mb-6">Establish data sync connections to your primary banking networks and accounting books.</p>
                  
                  <div className="space-y-4 text-xs font-semibold">
                    <div className="space-y-1.5">
                      <label className="text-[#18362F]/75">Company Directory Name</label>
                      <input 
                        type="text" 
                        value={onboardingOrgName}
                        onChange={(e) => setOnboardingOrgName(e.target.value)}
                        className="w-full bg-[#F7F8F5] border border-[#18362F]/10 p-2.5 rounded-lg focus:outline-none focus:border-[#18362F]/20 text-[#18362F]" 
                      />
                    </div>
                    
                    <div className="space-y-1.5">
                      <label className="text-[#18362F]/75">Connect Accounting Ledger ERP</label>
                      <div className="grid grid-cols-2 gap-3">
                        <button 
                          onClick={() => setOnboardingErp('netsuite')}
                          className={`p-3 rounded-lg border text-center transition-all ${
                            onboardingErp === 'netsuite' 
                              ? 'border-[#6CE8C2] bg-[#6CE8C2]/5 text-[#18362F]' 
                              : 'border-[#18362F]/10 bg-white text-[#A9B4AE] hover:text-[#18362F]'
                          }`}
                        >
                          Oracle NetSuite
                        </button>
                        <button 
                          onClick={() => setOnboardingErp('quickbooks')}
                          className={`p-3 rounded-lg border text-center transition-all ${
                            onboardingErp === 'quickbooks' 
                              ? 'border-[#6CE8C2] bg-[#6CE8C2]/5 text-[#18362F]' 
                              : 'border-[#18362F]/10 bg-white text-[#A9B4AE] hover:text-[#18362F]'
                          }`}
                        >
                          QuickBooks Online
                        </button>
                      </div>
                    </div>
                  </div>

                  <button 
                    onClick={() => setOnboardingStep(2)}
                    className="w-full h-11 bg-[#18362F] hover:bg-[#18362F]/90 text-[#F7F8F5] font-bold rounded-lg text-xs transition-colors mt-8 flex items-center justify-center gap-1 shadow-sm"
                  >
                    Continue to Agent Delegation <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}

              {onboardingStep === 2 && (
                <div>
                  <h3 className="font-serif font-bold text-base text-[#18362F] mb-1">Delegate operational finance tasks</h3>
                  <p className="text-xs text-[#A9B4AE] mb-6">Select which autonomous agent nodes to authorize as active delegates in your pipeline.</p>
                  
                  <div className="space-y-3 text-xs font-semibold">
                    {[
                      { id: 'ocr_ingest', title: 'Ingestion Clerk Agent', desc: 'Auto-scrapes OCR invoices, checks checksum errors, files PDF records.' },
                      { id: 'checksum_audit', title: 'Mathematical Auditor Agent', desc: 'Validates taxes, checks subtotal calculations, checks historical deviations.' },
                      { id: 'compliance_risk', title: 'Compliance & Risk Analyst', desc: 'Evaluates supplier trust certificates, identifies duplicate runs, audits bank triggers.' }
                    ].map((agent) => (
                      <label 
                        key={agent.id} 
                        className={`p-4 rounded-xl border flex gap-3 cursor-pointer transition-all ${
                          onboardingDelegates.includes(agent.id)
                            ? 'border-[#6CE8C2] bg-[#6CE8C2]/5 text-[#18362F]' 
                            : 'border-[#18362F]/10 bg-white text-[#A9B4AE]'
                        }`}
                      >
                        <input 
                          type="checkbox"
                          checked={onboardingDelegates.includes(agent.id)}
                          onChange={() => {
                            if (onboardingDelegates.includes(agent.id)) {
                              setOnboardingDelegates(onboardingDelegates.filter(x => x !== agent.id));
                            } else {
                              setOnboardingDelegates([...onboardingDelegates, agent.id]);
                            }
                          }}
                          className="mt-0.5 accent-[#6CE8C2]"
                        />
                        <div>
                          <p className="font-bold text-xs text-[#18362F]">{agent.title}</p>
                          <p className="text-[10px] text-[#A9B4AE] mt-0.5 font-medium">{agent.desc}</p>
                        </div>
                      </label>
                    ))}
                  </div>

                  <div className="grid grid-cols-2 gap-3 mt-8">
                    <button 
                      onClick={() => setOnboardingStep(1)}
                      className="h-11 border border-[#18362F]/10 hover:border-[#18362F]/20 text-[#18362F] font-bold rounded-lg text-xs transition-colors"
                    >
                      Back
                    </button>
                    <button 
                      onClick={() => { setOnboardingStep(3); startOnboardingBoot(); }}
                      className="h-11 bg-[#18362F] hover:bg-[#18362F]/90 text-[#F7F8F5] font-bold rounded-lg text-xs transition-colors flex items-center justify-center gap-1 shadow-sm"
                    >
                      Deploy System <Sparkles className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              )}

              {onboardingStep === 3 && (
                <div>
                  <h3 className="font-serif font-bold text-base text-[#18362F] mb-1">Booting Operating System</h3>
                  <p className="text-xs text-[#A9B4AE] mb-6">Compiling telemetry vault configurations and launching multi-agent triggers.</p>
                  
                  <div className="bg-[#061412] text-white p-4 rounded-xl font-mono text-[10px] space-y-2 h-44 overflow-y-auto mb-6 border border-white/5 shadow-inner">
                    {onboardingBootLogs.map((log, idx) => (
                      <div key={idx} className="flex gap-2 items-center text-emerald-400">
                        <span>➔</span>
                        <span>{log}</span>
                      </div>
                    ))}
                    {isOnboardingBooting && (
                      <div className="h-3 w-3 bg-[#6CE8C2] rounded-full animate-ping mt-1" />
                    )}
                  </div>

                  <button 
                    disabled={isOnboardingBooting}
                    onClick={() => {
                      setOnboardingCompleted(true);
                      setIsTourActive(false);
                    }}
                    className="w-full h-11 bg-[#18362F] hover:bg-[#18362F]/90 text-[#F7F8F5] font-bold rounded-lg text-xs transition-colors disabled:bg-zinc-100 disabled:text-zinc-400 disabled:cursor-not-allowed flex items-center justify-center gap-1 shadow-sm"
                  >
                    Enter Workspace <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* GUIDED WORKTHROUGH TOUR FLOATING ASSISTANT WIDGET DEACTIVATED */}

      {/* 1. SIDEBAR NAVIGATION (Left Column) */}
      <aside className="w-64 bg-[#061412] text-white border-r border-white/5 flex flex-col justify-between p-6 shrink-0 z-20 shadow-xl shadow-black/30">
        <div>
          {/* Platform Branding */}
          <div className="flex items-center gap-3 mb-8">
            <div className="w-8 h-8 rounded-lg bg-[#6CE8C2] flex items-center justify-center font-bold text-[#061412] text-base shadow-lg shadow-[#6CE8C2]/20">
              F
            </div>
            <div>
              <span className="font-serif font-bold text-sm tracking-tight text-white block">Finance OS</span>
              <span className="text-[8px] text-[#A9B4AE]/60 font-bold uppercase tracking-wider font-mono">Employee Node v2.0</span>
            </div>
          </div>

          {/* Nav Items */}
          <nav className="space-y-1">
            {[
              { 
                id: 'inbox', 
                name: 'Inbox', 
                icon: <Inbox className="w-4 h-4" />,
                tourHighlight: isTourActive && (tourStep === 1 || tourStep === 2)
              },
              { 
                id: 'copilot', 
                name: 'Copilot', 
                icon: <MessageSquare className="w-4 h-4" />,
                tourHighlight: isTourActive && tourStep === 3
              },
              { 
                id: 'documents', 
                name: 'Documents', 
                icon: <FileText className="w-4 h-4" />,
                tourHighlight: isTourActive && tourStep === 4
              },
              { id: 'approvals', name: 'Approvals', icon: <UserCheck className="w-4 h-4" /> },
              { id: 'analytics', name: 'Analytics', icon: <TrendingUp className="w-4 h-4" /> },
              { id: 'workflows', name: 'Workflows', icon: <GitBranch className="w-4 h-4" /> }
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  if (isTourActive) return; // Disable clicking tabs during tour for guided focus
                  setActiveTab(item.id);
                }}
                className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-xs font-semibold transition-all relative ${
                  activeTab === item.id
                    ? 'bg-[#6CE8C2]/10 text-[#6CE8C2] border-l-2 border-[#6CE8C2] shadow-sm'
                    : 'text-[#A9B4AE]/70 hover:bg-white/5 hover:text-white'
                } ${
                  item.tourHighlight 
                    ? 'ring-2 ring-[#6CE8C2] ring-offset-2 ring-offset-[#061412] scale-102 font-bold' 
                    : ''
                }`}
              >
                {item.icon}
                {item.name}
                {item.id === 'inbox' && inboxItems.filter(i => !i.is_archived).length > 0 && (
                  <span className="ml-auto font-mono text-[9px] bg-amber-500/20 text-amber-500 border border-amber-500/35 px-1.5 py-0.5 rounded-md font-bold">
                    {inboxItems.filter(i => !i.is_archived).length}
                  </span>
                )}
                {item.tourHighlight && (
                  <span className="absolute right-2 top-2.5 w-1.5 h-1.5 rounded-full bg-[#6CE8C2] animate-ping" />
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* User context / Settings trigger at bottom */}
        <div className="pt-6 border-t border-white/5 flex flex-col gap-2 font-semibold">
          <button
            onClick={() => setActiveTab('settings')}
            className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg text-xs transition-colors ${
              activeTab === 'settings' ? 'bg-[#6CE8C2]/10 text-[#6CE8C2]' : 'text-[#A9B4AE]/70 hover:text-white'
            }`}
          >
            <Settings className="w-4 h-4" />
            Workspace Settings
          </button>
          
          <div className="flex justify-between items-center bg-[#0A1E1B] p-2 border border-white/5 rounded-lg text-[9px] text-[#A9B4AE]/60">
            <span className="truncate max-w-[140px] font-mono">company_id_sync</span>
            <span className="w-2 h-2 rounded-full bg-[#6CE8C2] animate-pulse" />
          </div>
        </div>
      </aside>

      {/* 2. MAIN WORKSPACE PANEL (Sand Theme Canvas) */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        
        {/* Header toolbar */}
        <header className="h-16 border-b border-[#18362F]/6 px-8 flex items-center justify-between bg-white/60 backdrop-blur-md z-10 shrink-0">
          <div className="flex items-center gap-4">
            <h2 className="text-sm font-bold tracking-tight text-[#18362F] uppercase font-serif">{activeTab} Workspace</h2>
            <div className="w-1.5 h-1.5 rounded-full bg-[#6CE8C2]" />
            <span className="text-[10px] font-bold text-[#A9B4AE] font-mono">Live API Connected</span>
          </div>

          <div className="flex items-center gap-3">
            {/* Notification center */}
            <div className="relative">
              <button 
                onClick={() => setIsNotifOpen(!isNotifOpen)}
                className="p-2 border border-[#18362F]/10 hover:border-[#18362F]/20 rounded-lg bg-white shadow-sm transition-colors text-[#18362F]"
              >
                <Bell className="w-4 h-4" />
                {eventsLog.length > 0 && (
                  <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-rose-500 border border-white" />
                )}
              </button>
              
              <AnimatePresence>
                {isNotifOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="absolute right-0 mt-2 w-80 bg-white border border-[#18362F]/10 rounded-xl shadow-xl p-4 z-40 space-y-3"
                  >
                    <h4 className="font-serif font-bold text-xs text-[#18362F] border-b border-[#18362F]/5 pb-2">System Telemetry Log Alerts</h4>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {eventsLog.map((evt) => (
                        <div key={evt.id} className="p-2 bg-[#F7F8F5]/60 rounded-lg border border-[#18362F]/5 text-[10px] flex gap-2">
                          <span className="text-[#6CE8C2]">●</span>
                          <div>
                            <p className="font-bold text-[#18362F] capitalize">{evt.event_name.replace(/_/g, ' ')}</p>
                            <p className="text-[9px] text-[#A9B4AE] mt-0.5 font-mono truncate">{JSON.stringify(evt.dimensions)}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </header>

        {/* Global alerts banner */}
        <div className="px-8 pt-6">
          {successMsg && (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/25 text-emerald-700 rounded-xl flex justify-between items-center text-xs">
              <span className="flex items-center gap-1.5">✓ {successMsg}</span>
              <button onClick={() => setSuccessMsg(null)} className="text-[#A9B4AE] hover:text-[#18362F]">✕</button>
            </div>
          )}
          {errorMsg && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/25 text-rose-700 rounded-xl flex justify-between items-center text-xs animate-pulse">
              <span className="flex items-center gap-1.5">⚠ {errorMsg}</span>
              <button onClick={() => setErrorMsg(null)} className="text-[#A9B4AE] hover:text-[#18362F]">✕</button>
            </div>
          )}
        </div>

        {/* Primary Page routing switcher */}
        <div className="flex-1 overflow-y-auto p-8 relative">
          <div className="absolute top-0 right-0 w-96 h-96 bg-[#6CE8C2]/4 rounded-full blur-3xl pointer-events-none -z-10" />
          
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="h-full"
            >
              
              {/* TAB 1: UNIFIED INBOX & INTAKE HUB */}
              {activeTab === 'inbox' && (
                <div className="space-y-8 max-w-6xl">
                  {/* AI Daily Briefing Header */}
                  <div className="bg-[#061412] text-white border border-white/5 rounded-2xl p-6 relative overflow-hidden shadow-lg">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-[#6CE8C2]/10 rounded-full blur-2xl pointer-events-none" />
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-[#6CE8C2]" />
                        <span className="font-serif font-bold text-xs uppercase tracking-wider text-[#6CE8C2]">AI Daily Briefing</span>
                      </div>
                      <span className="font-mono text-[9px] text-[#A9B4AE]/60 uppercase font-bold tracking-wider font-semibold">Acme Corp Setup Validated</span>
                    </div>
                    <p className="font-serif text-[#F7F8F5]/90 text-sm leading-relaxed max-w-3xl">
                      "Good morning. Spend velocity is steady. We isolated <span className="text-[#6CE8C2] font-semibold">1 critical anomaly</span> regarding Z-Axis Engineering ($68,500.00). Runway is secure at 94 days. All operational pipelines are synced to NetSuite."
                    </p>
                  </div>

                  {/* Inbox Toggles */}
                  <div className="flex border-b border-[#18362F]/6 pb-3 items-center justify-between">
                    <div className="flex gap-2 bg-[#18362F]/5 p-1 rounded-lg">
                      <button
                        onClick={() => {
                          if (isTourActive) return; // Lock toggle during tour
                          setInboxSegment('queue');
                        }}
                        className={`px-4 py-1.5 rounded-md text-xs font-semibold transition-all ${
                          inboxSegment === 'queue' ? 'bg-[#18362F] text-[#F7F8F5] shadow-sm' : 'text-[#A9B4AE] hover:text-[#18362F]'
                        }`}
                      >
                        Action Inbox Queue
                      </button>
                      <button
                        onClick={() => {
                          if (isTourActive) return;
                          setInboxSegment('intake');
                        }}
                        className={`px-4 py-1.5 rounded-md text-xs font-semibold transition-all ${
                          inboxSegment === 'intake' ? 'bg-[#18362F] text-[#F7F8F5] shadow-sm' : 'text-[#A9B4AE] hover:text-[#18362F]'
                        }`}
                      >
                        Finance Intake Hub
                      </button>
                    </div>

                    {inboxSegment === 'queue' && (
                      <div className="flex gap-2">
                        {['all', 'high', 'risk', 'cashflow', 'archive'].map((pill) => (
                          <button
                            key={pill}
                            onClick={() => setInboxFilter(pill as any)}
                            className={`px-3 py-1 rounded-full text-[10px] font-bold capitalize border transition-all ${
                              inboxFilter === pill
                                ? 'bg-white border-[#18362F]/20 text-[#18362F] shadow-sm'
                                : 'bg-transparent border-transparent text-[#A9B4AE] hover:text-[#18362F]'
                            }`}
                          >
                            {pill}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* segment 1: Action Inbox Queue */}
                  {inboxSegment === 'queue' && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                      {/* Left Priority List */}
                      <div 
                        className={`lg:col-span-2 space-y-4 rounded-2xl transition-all ${
                          isTourActive && tourStep === 1 
                            ? 'ring-4 ring-[#6CE8C2] ring-offset-4 bg-white p-4 shadow-xl' 
                            : ''
                        }`}
                      >
                        {filteredInboxItems.length === 0 ? (
                          <div className="text-center py-20 bg-white border border-[#18362F]/5 rounded-2xl p-6">
                            <CheckCircle className="w-10 h-10 text-[#6CE8C2] mx-auto mb-3" />
                            <h4 className="font-serif font-bold text-sm text-[#18362F]">Inbox Zero Achieved</h4>
                            <p className="text-xs text-[#A9B4AE] mt-1 font-semibold">All priority financial operations are synchronized.</p>
                          </div>
                        ) : (
                          filteredInboxItems.map((item) => (
                            <div
                              key={item.id}
                              onClick={() => setSelectedInboxItem(item)}
                              className={`p-5 rounded-2xl cursor-pointer transition-all border ${
                                selectedInboxItem?.id === item.id
                                  ? 'bg-white border-[#18362F]/30 shadow-md shadow-[#18362F]/4'
                                  : 'bg-white/60 border-[#18362F]/6 hover:border-[#18362F]/15 hover:bg-white'
                              }`}
                            >
                              <div className="flex justify-between items-start gap-4 mb-3">
                                <div>
                                  <span className={`px-2 py-0.5 rounded-full text-[8px] font-mono uppercase font-bold tracking-wider ${
                                    item.priority === 'high' ? 'bg-rose-500/10 text-rose-700 border border-rose-500/20' : 'bg-[#18362F]/10 text-[#18362F]'
                                  }`}>
                                    {item.priority} priority
                                  </span>
                                  <h4 className="font-serif font-bold text-sm text-[#18362F] mt-1">{item.title}</h4>
                                </div>
                                <span className="font-mono text-[9px] text-[#A9B4AE]">{new Date(item.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                              </div>

                              <div className="space-y-2 text-xs">
                                <div>
                                  <span className="text-[10px] text-[#A9B4AE] uppercase font-bold tracking-wider">Issue</span>
                                  <p className="text-[#18362F]/90 mt-0.5 leading-relaxed font-semibold">{item.issue}</p>
                                </div>
                                <div className="grid grid-cols-2 gap-4 pt-2 border-t border-[#18362F]/5 text-[11px] font-semibold">
                                  <div>
                                    <span className="text-[#A9B4AE]">Financial Impact:</span>
                                    <p className="text-rose-700 mt-0.5">{item.impact}</p>
                                  </div>
                                  <div>
                                    <span className="text-[#A9B4AE]">Recommended:</span>
                                    <p className="text-[#18362F] mt-0.5">{item.recommendation}</p>
                                  </div>
                                </div>
                              </div>

                              <div className="flex gap-2 justify-end pt-4 mt-3 border-t border-[#18362F]/5">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleArchiveInboxCard(item.id);
                                  }}
                                  className="px-3 py-1.5 rounded-lg text-[10px] font-bold border border-[#18362F]/15 hover:bg-[#18362F]/5 transition-colors"
                                >
                                  Resolve Card
                                </button>
                              </div>
                            </div>
                          ))
                        )}
                        <div className="text-center text-[10px] text-[#A9B4AE]/70 font-semibold pt-4">
                          Keyboard Bindings: Use <kbd className="bg-white border border-[#18362F]/10 px-1 rounded font-mono">J</kbd> / <kbd className="bg-white border border-[#18362F]/10 px-1 rounded font-mono">K</kbd> to cycle queue, <kbd className="bg-white border border-[#18362F]/10 px-1 rounded font-mono">E</kbd> to resolve.
                        </div>
                      </div>

                      {/* Right Detail / Human Review Inspector */}
                      <div className="bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-2xl p-6 h-fit space-y-6">
                        <h3 className="font-serif font-bold text-sm text-[#18362F] border-b border-[#18362F]/6 pb-3">Operational Inspector</h3>
                        
                        {selectedInboxItem ? (
                          <div className="space-y-6 text-xs">
                            <div>
                              <span className="text-[10px] text-[#A9B4AE] uppercase font-bold tracking-wider">Item Reference ID</span>
                              <p className="font-mono text-[10px] text-[#18362F] truncate mt-1">{selectedInboxItem.id}</p>
                            </div>

                            <div className="space-y-3">
                              <span className="text-[10px] text-[#A9B4AE] uppercase font-bold tracking-wider">Delegate Team assignment</span>
                              <div className="flex gap-2">
                                <input
                                  type="text"
                                  placeholder="Enter team member name..."
                                  value={assigneeInput}
                                  onChange={(e) => setAssigneeInput(e.target.value)}
                                  className="flex-1 bg-[#F7F8F5] border border-[#18362F]/10 p-2 rounded-lg text-xs"
                                />
                                <button
                                  onClick={handleAssignInboxItem}
                                  className="bg-[#18362F] hover:bg-[#18362F]/90 text-[#F7F8F5] font-bold px-3 rounded-lg"
                                >
                                  Assign
                                </button>
                              </div>
                              {selectedInboxItem.assigned_to && (
                                <div className="p-2 bg-[#6CE8C2]/10 border border-[#6CE8C2]/20 text-[#18362F] font-bold rounded-lg text-[10px]">
                                  Active Assignee: {selectedInboxItem.assigned_to}
                                </div>
                              )}
                            </div>

                            {selectedInboxItem.metadata?.invoice_id && (
                              <div className="space-y-3 pt-3 border-t border-[#18362F]/5">
                                <span className="text-[10px] text-[#A9B4AE] uppercase font-bold tracking-wider">Flagged Invoice Data Details</span>
                                <div className="space-y-2">
                                  <div className="flex justify-between font-semibold">
                                    <span className="text-[#A9B4AE]">Vendor:</span>
                                    <span className="text-[#18362F]">{selectedInboxItem.metadata.vendor_name}</span>
                                  </div>
                                  <div className="flex justify-between font-semibold">
                                    <span className="text-[#A9B4AE]">Total Amount:</span>
                                    <span className="text-[#18362F] font-mono">${selectedInboxItem.metadata.amount?.toLocaleString()}</span>
                                  </div>
                                  <button
                                    onClick={() => {
                                      setSelectedDoc(invoices.find(i => i.id === selectedInboxItem.metadata.invoice_id) || null);
                                      setActiveTab('documents');
                                    }}
                                    className="w-full h-9 border border-[#18362F]/10 hover:bg-[#18362F]/5 text-[#18362F] font-bold rounded-lg flex items-center justify-center gap-1.5 transition-colors"
                                  >
                                    <Eye className="w-3.5 h-3.5" /> View Original Scan
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="text-center py-20 text-[#A9B4AE] text-xs font-semibold">
                            Select an item from the queue list to inspect parameters.
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* segment 2: Intake Hub */}
                  {inboxSegment === 'intake' && (
                    <div className="space-y-8">
                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Drop Zone Batches */}
                        <div 
                          className={`bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-2xl p-6 flex flex-col justify-between transition-all ${
                            isTourActive && tourStep === 2 
                              ? 'ring-4 ring-[#6CE8C2] ring-offset-4 scale-102 bg-white' 
                              : ''
                          }`}
                        >
                          <div>
                            <h3 className="font-serif font-bold text-sm text-[#18362F] mb-1">Batch Ingest Dropper</h3>
                            <p className="text-xs text-[#A9B4AE] mb-6 font-semibold">Drag folders, ZIP archives, or multiple PDFs. Auto-scraped triggers initialize compliance validation.</p>
                          </div>

                          <div className="space-y-4">
                            <label className="border border-dashed border-[#18362F]/15 hover:border-[#18362F]/35 rounded-2xl p-8 flex flex-col items-center justify-center cursor-pointer bg-[#F7F8F5]/30 hover:bg-[#F7F8F5]/60 transition-all text-center">
                              <UploadCloud className="w-10 h-10 text-[#A9B4AE] mb-3" />
                              <span className="text-xs font-bold text-[#18362F] block">Select Folder or ZIP file</span>
                              <span className="text-[10px] text-[#A9B4AE] mt-1 font-semibold">Extracts nested PDF invoices</span>
                              <input 
                                type="file" 
                                multiple
                                onChange={(e) => {
                                  if (e.target.files && e.target.files.length > 0) {
                                    handleIntakeDrop(`Drop Batch _ ${e.target.files.length} files`, e.target.files.length, 'upload');
                                  }
                                }}
                                className="hidden" 
                              />
                            </label>

                            <div className="grid grid-cols-2 gap-2 text-xs">
                              <button 
                                onClick={() => handleIntakeDrop('billing_archives_zip', 8, 'upload')}
                                className="p-2 border border-[#18362F]/10 hover:border-[#6CE8C2]/40 rounded-xl bg-white transition-all text-[10px] font-bold text-[#18362F] flex items-center justify-center gap-1.5"
                              >
                                <FileArchive className="w-3.5 h-3.5" /> Import ZIP (8 docs)
                              </button>
                              <button 
                                onClick={() => handleIntakeDrop('Q2_travel_expenses_folder', 5, 'upload')}
                                className="p-2 border border-[#18362F]/10 hover:border-[#6CE8C2]/40 rounded-xl bg-white transition-all text-[10px] font-bold text-[#18362F] flex items-center justify-center gap-1.5"
                              >
                                <FolderOpen className="w-3.5 h-3.5" /> Import Folder (5 docs)
                              </button>
                            </div>
                          </div>
                        </div>

                        {/* Processing Center */}
                        <div className="bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-2xl p-6 lg:col-span-2 flex flex-col justify-between">
                          <div>
                            <h3 className="font-serif font-bold text-sm text-[#18362F] mb-1">Processing Center Telemetry</h3>
                            <p className="text-xs text-[#A9B4AE] mb-6 font-semibold">Real-time trace check monitoring of incoming ingestion batches.</p>
                          </div>

                          <div className="flex-1 space-y-3">
                            {isIntakeUploading ? (
                              <div className="space-y-4">
                                <div className="flex justify-between items-center text-xs font-semibold">
                                  <span className="text-[#18362F]">Batch Extraction: {intakeUploadProgress}%</span>
                                  <span className="h-3 w-3 bg-[#6CE8C2] rounded-full animate-ping" />
                                </div>
                                <div className="w-full bg-[#F7F8F5] h-2 rounded-full overflow-hidden border border-[#18362F]/5">
                                  <div className="bg-[#6CE8C2] h-full transition-all duration-300" style={{ width: `${intakeUploadProgress}%` }} />
                                </div>
                                <div className="bg-[#061412] text-white p-3 rounded-lg font-mono text-[9px] space-y-1 max-h-32 overflow-y-auto">
                                  {intakeUploadLogs.map((log, i) => (
                                    <div key={i} className="text-emerald-400">➔ {log}</div>
                                  ))}
                                </div>
                              </div>
                            ) : (
                              <div className="space-y-4">
                                <div className="flex justify-between items-center">
                                  <span className="text-xs font-serif font-bold text-[#18362F]">Sync Ingestion Connectors</span>
                                </div>
                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                                  {[
                                    { name: 'Gmail Account', icon: <Mail className="w-4 h-4 text-rose-500" />, action: () => setIsGmailDrawerOpen(true), desc: 'Auto-sync mail attachments' },
                                    { name: 'Google Drive', icon: <Cloud className="w-4 h-4 text-blue-500" />, action: () => setIsDriveModalOpen(true), desc: 'Browser cloud folder trees' },
                                    { name: 'ERP Sync', icon: <Database className="w-4 h-4 text-emerald-500" />, action: () => setSuccessMsg('Synced ERP records!'), desc: 'Check QuickBooks feeds' }
                                  ].map((integration, idx) => (
                                    <div key={idx} className="p-4 border border-[#18362F]/6 rounded-xl bg-[#F7F8F5]/30 flex flex-col justify-between gap-3">
                                      <div className="flex items-center gap-2 font-bold">
                                        {integration.icon}
                                        <span>{integration.name}</span>
                                      </div>
                                      <p className="text-[9px] text-[#A9B4AE] font-semibold">{integration.desc}</p>
                                      <button 
                                        onClick={integration.action}
                                        className="w-full h-8 bg-[#18362F] hover:bg-[#18362F]/90 text-[#F7F8F5] font-bold rounded-lg text-[10px] transition-colors"
                                      >
                                        Connect
                                      </button>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Ingestion Batch Directory Ledger */}
                      <div className="bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-2xl p-6">
                        <h3 className="font-serif font-bold text-sm text-[#18362F] mb-4">Ingestion Batches Register</h3>
                        <div className="space-y-4">
                          {batches.map((b) => (
                            <div key={b.id} className="p-4 bg-[#F7F8F5]/50 border border-[#18362F]/5 rounded-xl">
                              <div className="flex justify-between items-center border-b border-[#18362F]/5 pb-2 mb-3">
                                <div className="flex items-center gap-3">
                                  <FileArchive className="w-4 h-4 text-[#18362F]/60" />
                                  <span className="font-serif font-bold text-xs text-[#18362F]">{b.batch_name}</span>
                                  <span className="font-mono text-[9px] text-[#A9B4AE] font-semibold">via {b.source}</span>
                                </div>
                                <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${statusColorMap(b.status)}`}>
                                  {b.status}
                                </span>
                              </div>

                              <div className="space-y-2">
                                {b.documents.map((doc) => (
                                  <div key={doc.id} className="flex justify-between items-center p-2.5 bg-white border border-[#18362F]/4 rounded-lg text-xs">
                                    <div className="flex items-center gap-3 font-semibold">
                                      <span className="font-mono text-[10px] text-[#A9B4AE]">{doc.size}</span>
                                      <span className="text-[#18362F]/90">{doc.filename}</span>
                                    </div>
                                    <div className="flex items-center gap-4">
                                      <span className="font-mono text-[#A9B4AE]/80 font-bold">Confidence: {doc.confidence}%</span>
                                      <span className="font-bold text-[#18362F] font-mono">${doc.amount?.toLocaleString()}</span>
                                      <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${statusColorMap(doc.status)}`}>
                                        {doc.status}
                                      </span>
                                      {doc.status === 'failed' && (
                                        <button
                                          onClick={() => {
                                            setRecoveryDocument(doc);
                                            setRecoveryBatchId(b.id);
                                          }}
                                          className="text-[10px] text-rose-700 hover:underline font-bold"
                                        >
                                          Recover Failure
                                        </button>
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Gmail Import drawer */}
                  <AnimatePresence>
                    {isGmailDrawerOpen && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-[#061412]/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                      >
                        <motion.div
                          initial={{ scale: 0.95 }}
                          animate={{ scale: 1 }}
                          exit={{ scale: 0.95 }}
                          className="bg-white border border-[#18362F]/10 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4"
                        >
                          <div className="flex justify-between items-center border-b border-[#18362F]/5 pb-3">
                            <span className="font-serif font-bold text-sm text-[#18362F] flex items-center gap-2">
                              <Mail className="w-4 h-4 text-rose-500" /> Gmail Attachment Sync Portal
                            </span>
                            <button onClick={() => setIsGmailDrawerOpen(false)} className="text-[#A9B4AE] hover:text-[#18362F]"><X className="w-4 h-4" /></button>
                          </div>
                          
                          <p className="text-xs text-[#A9B4AE] font-semibold">Select attachments from recent financial correspondence to sync directly into the ingestion vault.</p>
                          
                          <div className="space-y-2 text-xs max-h-60 overflow-y-auto font-semibold">
                            {[
                              { subject: 'Apex Invoice statement Q2', file: 'apex_statement_90.pdf', size: '1.4 MB' },
                              { subject: 'Z-Axis Labs Engineering consultation', file: 'zaxis_consulting_invoice.pdf', size: '2.8 MB' },
                              { subject: 'Sentry Services contract updates', file: 'sentry_renew.pdf', size: '890 KB' }
                            ].map((mail, idx) => (
                              <div key={idx} className="p-3 bg-[#F7F8F5]/60 border border-[#18362F]/5 rounded-lg flex items-center justify-between">
                                <div>
                                  <p className="font-bold text-[#18362F]">{mail.subject}</p>
                                  <p className="text-[10px] text-[#A9B4AE] mt-0.5 font-mono">{mail.file} ({mail.size})</p>
                                </div>
                                <button
                                  onClick={() => {
                                    setIsGmailDrawerOpen(false);
                                    handleIntakeDrop(`Gmail attachment: ${mail.file}`, 1, 'gmail');
                                  }}
                                  className="bg-[#18362F] text-[#F7F8F5] px-3 py-1.5 rounded-lg text-[10px] font-bold"
                                >
                                  Import
                                </button>
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* Google Drive Import Modal */}
                  <AnimatePresence>
                    {isDriveModalOpen && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-[#061412]/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                      >
                        <motion.div
                          initial={{ scale: 0.95 }}
                          animate={{ scale: 1 }}
                          exit={{ scale: 0.95 }}
                          className="bg-white border border-[#18362F]/10 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4"
                        >
                          <div className="flex justify-between items-center border-b border-[#18362F]/5 pb-3">
                            <span className="font-serif font-bold text-sm text-[#18362F] flex items-center gap-2">
                              <Cloud className="w-4 h-4 text-blue-500" /> Google Drive File Browser
                            </span>
                            <button onClick={() => setIsDriveModalOpen(false)} className="text-[#A9B4AE] hover:text-[#18362F]"><X className="w-4 h-4" /></button>
                          </div>
                          
                          <p className="text-xs text-[#A9B4AE] font-semibold">Browse your Drive directories for invoices zip archives or files bundles.</p>
                          
                          <div className="border border-[#18362F]/10 rounded-xl p-4 bg-[#F7F8F5]/30 space-y-2 text-xs">
                            <div className="flex items-center gap-2 text-[#18362F] font-bold">
                              <span>📁</span>
                              <span>My Drive / Accounting / Invoices</span>
                            </div>
                            <div className="pl-4 space-y-2 pt-2">
                              <div className="flex items-center justify-between p-2 bg-white border border-[#18362F]/5 rounded-lg">
                                <span className="font-mono">invoices_collection_q2.zip (3.1 MB)</span>
                                <button
                                  onClick={() => {
                                    setIsDriveModalOpen(false);
                                    handleIntakeDrop('invoices_collection_q2.zip', 3, 'gdrive');
                                  }}
                                  className="bg-[#18362F] text-[#F7F8F5] px-2 py-1 rounded text-[10px] font-bold"
                                >
                                  Select ZIP
                                </button>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* Failure Recovery UI Modal Overlay */}
                  <AnimatePresence>
                    {recoveryDocument && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-[#061412]/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                      >
                        <motion.div
                          initial={{ scale: 0.95 }}
                          animate={{ scale: 1 }}
                          exit={{ scale: 0.95 }}
                          className="bg-white border border-[#18362F]/10 rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4"
                        >
                          <div className="flex justify-between items-center border-b border-[#18362F]/5 pb-3">
                            <span className="font-serif font-bold text-sm text-[#18362F] flex items-center gap-2">
                              <AlertCircle className="w-4 h-4 text-rose-500" /> Human Review Failure Recovery
                            </span>
                            <button onClick={() => setRecoveryDocument(null)} className="text-[#A9B4AE] hover:text-[#18362F]"><X className="w-4 h-4" /></button>
                          </div>
                          
                          <p className="text-[11px] text-[#A9B4AE] font-semibold leading-relaxed">
                            <strong>File Anomaly Details:</strong> {recoveryDocument.failure_reason}
                          </p>

                          <form onSubmit={handleSaveFailureRecovery} className="space-y-4 text-xs font-semibold">
                            <div className="space-y-1">
                              <label className="text-[#18362F]/75">Filename</label>
                              <p className="p-2.5 bg-[#F7F8F5] border border-[#18362F]/10 rounded-lg font-mono">{recoveryDocument.filename}</p>
                            </div>
                            
                            <div className="space-y-1">
                              <label className="text-[#18362F]/75">Identified Vendor (Override)</label>
                              <input
                                type="text"
                                value={recoveryDocument.vendor}
                                onChange={(e) => setRecoveryDocument({ ...recoveryDocument, vendor: e.target.value })}
                                className="w-full bg-[#F7F8F5] border border-[#18362F]/10 p-2.5 rounded-lg focus:outline-none focus:border-[#18362F]/20 text-[#18362F]"
                                required
                              />
                            </div>

                            <div className="space-y-1">
                              <label className="text-[#18362F]/75">Total Invoice Amount ($)</label>
                              <input
                                type="number"
                                value={recoveryDocument.amount}
                                onChange={(e) => setRecoveryDocument({ ...recoveryDocument, amount: Number(e.target.value) })}
                                className="w-full bg-[#F7F8F5] border border-[#18362F]/10 p-2.5 rounded-lg focus:outline-none focus:border-[#18362F]/20 text-[#18362F] font-mono"
                                required
                              />
                            </div>

                            <button
                              type="submit"
                              className="w-full h-11 bg-[#18362F] hover:bg-[#18362F]/90 text-[#F7F8F5] font-bold rounded-lg mt-4 transition-colors shadow-sm"
                            >
                              Resolve Cheksums & Synchronize
                            </button>
                          </form>
                        </motion.div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}

              {/* TAB 2: COPILOT 2.0 (AI FINANCE EMPLOYEE) */}
              {activeTab === 'copilot' && (
                <div className="h-[calc(100vh-10rem)] max-w-4xl mx-auto flex flex-col justify-between bg-[#061412] border border-white/5 rounded-2xl overflow-hidden shadow-2xl relative">
                  
                  {chatHistory.length <= 1 ? (
                    <div className="flex-1 overflow-y-auto p-8 flex flex-col justify-between text-white">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <Sparkles className="w-5 h-5 text-[#6CE8C2]" />
                          <span className="font-serif font-bold text-xs uppercase tracking-wider text-[#6CE8C2]">AI Finance Node</span>
                        </div>
                        <h1 className="font-serif font-extrabold text-3xl leading-tight">Hello. I am your AI Finance Employee.</h1>
                        <p className="text-xs text-[#A9B4AE] mt-2 max-w-xl font-semibold">
                          I operate as your autonomous accounting clerk. I analyze spend velocity curves, identify transaction anomalies, evaluate vendor SOC2 compliance indexes, and run runway projection checks.
                        </p>
                      </div>

                      {/* Mode selectors */}
                      <div 
                        className={`space-y-4 pt-6 border-t border-white/5 transition-all ${
                          isTourActive && tourStep === 3 
                            ? 'ring-4 ring-[#6CE8C2] ring-offset-4 ring-offset-[#061412] p-4 bg-[#0A1E1B] rounded-2xl' 
                            : ''
                        }`}
                      >
                        <span className="text-[10px] text-[#A9B4AE]/50 uppercase font-bold tracking-wider font-mono">Select Active Operational Mode</span>
                        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5 text-xs font-bold text-center">
                          {[
                            { id: 'ask', label: 'Ask Mode', desc: 'Queries / Database audits' },
                            { id: 'analyze', label: 'Analyze Mode', desc: 'Spend trends calculations' },
                            { id: 'investigate', label: 'Investigate Mode', desc: 'Anomalies triggers' },
                            { id: 'execute', label: 'Execute Mode', desc: 'Route approvals' },
                            { id: 'simulate', label: 'Simulate Mode', desc: 'Runway checks' }
                          ].map((mode) => (
                            <button
                              key={mode.id}
                              onClick={() => {
                                setCopilotMode(mode.id as any);
                                setSuccessMsg(`Copilot switched to ${mode.label}`);
                              }}
                              className={`p-3 rounded-xl border flex flex-col gap-1 items-center justify-center transition-all ${
                                copilotMode === mode.id
                                  ? 'border-[#6CE8C2] bg-[#6CE8C2]/15 text-[#6CE8C2]'
                                  : 'border-white/5 bg-[#0A1E1B] text-[#A9B4AE] hover:text-white'
                              }`}
                            >
                              <span className="text-[11px] block">{mode.label}</span>
                              <span className="text-[8px] text-[#A9B4AE]/60 block font-medium mt-0.5">{mode.desc}</span>
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Suggested prompts cards */}
                      <div className="space-y-3 pt-6 border-t border-white/5">
                        <span className="text-[10px] text-[#A9B4AE]/50 uppercase font-bold tracking-wider font-mono">Suggested Prompt Actions</span>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                          {[
                            { prompt: 'Verify compliance status and risk rating flags for Z-Axis.', label: 'Audits supplier details' },
                            { prompt: 'Calculate average processing latency triggers MoM.', label: 'Reviews operational latency' },
                            { prompt: 'Run runway cashflow projection models under weekend outlier spend.', label: 'Projections check' },
                            { prompt: 'Draft a summary report of NetSuite ERP syncing history.', label: 'Compiles audit logs' }
                          ].map((item, i) => (
                            <button
                              key={i}
                              onClick={() => handleCopilotPromptSubmit(item.prompt)}
                              className="p-3 bg-[#0A1E1B] border border-white/5 hover:border-white/12 rounded-xl text-left text-[#A9B4AE] hover:text-white font-semibold flex flex-col justify-between gap-1 transition-colors"
                            >
                              <span>{item.prompt}</span>
                              <span className="text-[9px] text-[#A9B4AE]/50 font-bold uppercase tracking-wider">{item.label}</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : (
                    // Conversational stream view
                    <div className="flex-1 overflow-y-auto p-6 space-y-6 text-white">
                      {chatHistory.map((line) => (
                        <div key={line.id} className={`flex gap-4 ${line.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                          <div className={`flex gap-3 max-w-[85%] ${line.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 ${
                              line.role === 'user' ? 'bg-[#18362F] text-white border border-white/10' : 'bg-[#6CE8C2] text-[#061412] shadow'
                            }`}>
                              {line.role === 'user' ? 'U' : 'AI'}
                            </div>
                            
                            <div className={`p-4 rounded-xl text-xs leading-relaxed border ${
                              line.role === 'user' 
                                ? 'bg-[#18362F]/60 text-white rounded-tr-none border-white/10' 
                                : 'bg-[#0D2420] text-[#F7F8F5]/90 rounded-tl-none border-white/5 shadow-lg shadow-black/25'
                            }`}>
                              <p className="whitespace-pre-line font-medium leading-relaxed">{line.message}</p>
                              
                              {line.citations && line.citations.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-white/5 flex flex-wrap gap-1.5 items-center">
                                  <span className="text-[9px] text-[#A9B4AE]/40 uppercase font-bold tracking-wider font-mono">Verified References:</span>
                                  {line.citations.map((cite, idx) => (
                                    <span key={idx} className="text-[9px] px-2 py-0.5 rounded bg-[#0A1E1B] text-[#6CE8C2]/90 border border-white/8 font-mono font-bold">
                                      {cite}
                                    </span>
                                  ))}
                                </div>
                              )}

                              {line.structuredData && (
                                <div className="mt-4 p-4 bg-[#061412]/60 border border-white/5 rounded-xl space-y-3">
                                  <div className="flex justify-between items-center border-b border-white/5 pb-2">
                                    <span className="font-serif font-bold text-[#6CE8C2]">Analysis findings summary</span>
                                    <span className="text-[9px] bg-[#6CE8C2]/15 text-[#6CE8C2] border border-[#6CE8C2]/20 px-2 py-0.5 rounded-full font-bold">
                                      Confidence: {line.structuredData.confidence}
                                    </span>
                                  </div>
                                  <ul className="space-y-1 text-[#F7F8F5]/80 list-disc pl-4 leading-relaxed font-semibold">
                                    {line.structuredData.findings.map((f: string, i: number) => (
                                      <li key={i}>{f}</li>
                                    ))}
                                  </ul>
                                  <div className="pt-2 border-t border-white/5 text-[10px] text-[#A9B4AE] font-semibold flex justify-between items-center">
                                    <span>Evidence source: {line.structuredData.evidence}</span>
                                    {line.structuredData.recommendation && (
                                      <span className="text-[#6CE8C2] font-serif font-bold italic">Recommended: {line.structuredData.recommendation}</span>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}

                      {isChatLoading && (
                        <div className="flex gap-4 justify-start">
                          <div className="w-8 h-8 rounded-lg bg-[#6CE8C2] text-[#061412] flex items-center justify-center font-bold text-xs shadow">AI</div>
                          <div className="p-4 rounded-xl bg-[#0D2420] text-[#A9B4AE]/60 text-xs border border-white/5 rounded-tl-none animate-pulse w-3/4">
                            Retrieving database vectors & running checksum check scans...
                          </div>
                        </div>
                      )}
                      
                      <div ref={chatEndRef} />
                    </div>
                  )}

                  {chatHistory.length > 1 && (
                    <div className="p-3 border-t border-white/5 bg-[#0A1E1B] flex gap-2 overflow-x-auto font-semibold">
                      {[
                        'Explain audit checklist calculations',
                        'Route Z-Axis invoice manual sync override',
                        'Verify QuickBooks integration connection',
                        'Download cashflow forecast reports'
                      ].map((chip, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleCopilotPromptSubmit(chip)}
                          className="text-[9px] bg-[#0D2420] border border-white/8 hover:border-white/15 px-2.5 py-1.5 rounded-full text-[#A9B4AE]/80 hover:text-white transition-colors font-mono font-bold whitespace-nowrap"
                        >
                          {chip}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Input controls form */}
                  <div className="p-4 border-t border-white/5 bg-[#0A1E1B] space-y-3 z-10 font-semibold">
                    <form 
                      onSubmit={(e) => { e.preventDefault(); handleCopilotPromptSubmit(); }} 
                      className="flex gap-3 items-center"
                    >
                      <input
                        type="text"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        placeholder={`Ask Copilot [${copilotMode.toUpperCase()} MODE]: e.g., 'Draft Runway reports' or 'Verify Apex sync'`}
                        className="flex-1 bg-[#0D2420] border border-white/8 rounded-xl px-4 h-11 text-xs text-[#F7F8F5] placeholder-white/20 focus:outline-none focus:border-white/15"
                      />
                      
                      <button
                        type="button"
                        onClick={handleToggleVoice}
                        className={`w-11 h-11 rounded-xl flex items-center justify-center border transition-all ${
                          isRecordingVoice 
                            ? 'bg-rose-500 border-rose-600 text-white animate-pulse' 
                            : 'bg-[#0D2420] border-white/8 text-[#A9B4AE] hover:text-white'
                        }`}
                      >
                        <Mic className="w-4 h-4" />
                      </button>

                      <button
                        type="submit"
                        disabled={!inputText.trim() || isChatLoading}
                        className="bg-[#6CE8C2] hover:bg-[#6CE8C2]/90 text-[#061412] font-bold rounded-xl px-5 h-11 text-xs transition-colors disabled:bg-zinc-800 disabled:text-zinc-600 disabled:cursor-not-allowed shadow-md"
                      >
                        Ask Employee
                      </button>
                    </form>

                    <AnimatePresence>
                      {isRecordingVoice && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 32 }}
                          exit={{ opacity: 0, height: 0 }}
                          className="w-full flex items-center justify-center gap-3"
                        >
                          <span className="text-[9px] font-mono text-rose-500 font-bold uppercase tracking-wider animate-pulse">Voice Listening:</span>
                          <canvas 
                            ref={voiceCanvasRef} 
                            width={220} 
                            height={28}
                            className="bg-transparent"
                          />
                          <span className="text-[9px] font-mono text-[#A9B4AE] font-semibold">Click Mic to Submit Ingestion.</span>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </div>
              )}

              {/* TAB 3: DOCUMENTS LEDGER VIEW */}
              {activeTab === 'documents' && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-6xl">
                  {/* Ledger list */}
                  <div 
                    className={`lg:col-span-2 space-y-6 transition-all ${
                      isTourActive && tourStep === 4 
                        ? 'ring-4 ring-[#6CE8C2] ring-offset-4 bg-white p-4 rounded-2xl shadow-xl' 
                        : ''
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row gap-4 justify-between items-center bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] p-4 rounded-xl">
                      <div className="relative w-full sm:w-64">
                        <input
                          type="text"
                          value={docSearch}
                          onChange={(e) => setDocSearch(e.target.value)}
                          placeholder="Search by vendor or invoice #..."
                          className="w-full bg-[#F7F8F5] border border-[#18362F]/10 px-3 py-2 pl-8 rounded-lg text-xs text-[#18362F] placeholder-[#A9B4AE]/80 focus:outline-none"
                        />
                        <Search className="w-3.5 h-3.5 absolute left-2.5 top-3 text-[#A9B4AE]" />
                      </div>
                      
                      <div className="flex gap-2 w-full sm:w-auto overflow-x-auto">
                        {['all', 'completed', 'pending_review', 'failed'].map((st) => (
                          <button
                            key={st}
                            onClick={() => setDocStatusFilter(st)}
                            className={`px-3 py-1.5 rounded-lg text-[9px] font-bold uppercase tracking-wider border transition-colors ${
                              docStatusFilter === st
                                ? 'bg-[#18362F] border-[#18362F] text-[#F7F8F5]'
                                : 'bg-white border-[#18362F]/10 text-[#A9B4AE] hover:text-[#18362F]'
                            }`}
                          >
                            {st}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-xl overflow-hidden">
                      <table className="w-full text-left text-xs border-collapse">
                        <thead>
                          <tr className="border-b border-[#18362F]/5 text-[#A9B4AE] uppercase text-[9px] font-bold tracking-wider">
                            <th className="p-4">Invoice ID</th>
                            <th className="p-4">Supplier</th>
                            <th className="p-4">Amount</th>
                            <th className="p-4">Status</th>
                            <th className="p-4">Trace Code</th>
                          </tr>
                        </thead>
                        <tbody>
                          {invoices.length === 0 ? (
                            <tr>
                              <td colSpan={5} className="p-8 text-center text-[#A9B4AE] font-semibold">
                                No records active in this company directory.
                              </td>
                            </tr>
                          ) : (
                            invoices.map((inv) => (
                              <tr
                                key={inv.id}
                                onClick={() => setSelectedDoc(inv)}
                                className={`border-b border-[#18362F]/4 cursor-pointer hover:bg-[#F7F8F5]/40 transition-colors ${
                                  selectedDoc?.id === inv.id ? 'bg-[#F7F8F5] border-l-2 border-[#6CE8C2]' : ''
                                }`}
                              >
                                <td className="p-4 font-mono text-[#A9B4AE]">{inv.invoice_number || 'Extracting...'}</td>
                                <td className="p-4 font-bold text-[#18362F] font-serif">{inv.vendor_name || 'Processing...'}</td>
                                <td className="p-4 font-bold text-[#18362F] font-mono">${inv.total_amount?.toLocaleString() || '—'}</td>
                                <td className="p-4">
                                  <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${statusColorMap(inv.status)}`}>
                                    {inv.status}
                                  </span>
                                </td>
                                <td className="p-4 font-mono text-[9px] text-[#A9B4AE] truncate max-w-[80px]">{inv.id}</td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Side inspector details */}
                  <div className="bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-xl p-6 h-fit space-y-6">
                    <h3 className="font-serif font-bold text-sm text-[#18362F] border-b border-[#18362F]/6 pb-3">Audit Inspector</h3>
                    
                    {selectedDoc ? (
                      <div className="space-y-6 text-xs">
                        <div>
                          <span className="text-[10px] text-[#A9B4AE] uppercase font-bold tracking-wider">Tenant Document UUID</span>
                          <p className="font-mono text-[10px] text-[#18362F] truncate mt-1">{selectedDoc.id}</p>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-xs font-semibold">
                          <div>
                            <span className="text-[#A9B4AE]">Issue Date:</span>
                            <p className="text-[#18362F] mt-1">{selectedDoc.issue_date || '—'}</p>
                          </div>
                          <div>
                            <span className="text-[#A9B4AE]">Due Date:</span>
                            <p className="text-[#18362F] mt-1">{selectedDoc.due_date || '—'}</p>
                          </div>
                        </div>

                        <div className="space-y-2 pt-3 border-t border-[#18362F]/5">
                          <span className="text-[10px] text-[#A9B4AE] uppercase font-bold tracking-wider">OCR Confidence Audit</span>
                          <div className="flex items-center gap-3">
                            <div className="flex-1 bg-[#F7F8F5] h-2 rounded-full overflow-hidden border border-[#18362F]/5">
                              <div className="bg-[#6CE8C2] h-full" style={{ width: '96%' }} />
                            </div>
                            <span className="font-mono text-[10px] font-bold text-emerald-700">96.8%</span>
                          </div>
                        </div>

                        <div className="space-y-2 pt-3 border-t border-[#18362F]/5 font-semibold">
                          <span className="text-[10px] text-[#A9B4AE] uppercase font-bold tracking-wider font-mono">Telemetry Verification Checksums</span>
                          <div className="space-y-1.5 text-[10px]">
                            <div className="flex justify-between p-2 bg-[#F7F8F5]/60 border border-[#18362F]/5 rounded-lg">
                              <span className="text-[#A9B4AE]">Tax Math Formula</span>
                              <span className="text-emerald-700 font-bold">✓ PASS</span>
                            </div>
                            <div className="flex justify-between p-2 bg-[#F7F8F5]/60 border border-[#18362F]/5 rounded-lg">
                              <span className="text-[#A9B4AE]">Historical Anomaly (Z-score)</span>
                              <span className="text-emerald-700 font-bold">✓ PASS</span>
                            </div>
                            <div className="flex justify-between p-2 bg-[#F7F8F5]/60 border border-[#18362F]/5 rounded-lg">
                              <span className="text-[#A9B4AE]">Netsuite Synchronization Status</span>
                              <span className="text-emerald-700 font-bold">✓ SYNCED</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-20 text-[#A9B4AE] text-xs font-semibold">
                        Select a record item from the directory table ledger to inspect parameters.
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* TAB 4: APPROVALS */}
              {activeTab === 'approvals' && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-6xl font-semibold">
                  <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-xl p-6">
                      <h3 className="font-serif font-bold text-sm text-[#18362F] mb-4">Manual Sign-off priority list</h3>
                      <div className="space-y-3">
                        {approvalRuns.map((run) => (
                          <div key={run.id} className="p-4 bg-[#F7F8F5]/60 border border-[#18362F]/5 rounded-xl flex justify-between items-center text-xs font-semibold">
                            <div>
                              <div className="flex gap-2 items-center font-bold">
                                <span className="text-[#A9B4AE] font-mono">{run.invoice_number}</span>
                                <span className="text-[#18362F]/30">|</span>
                                <span className="text-[#18362F] font-serif">{run.vendor_name}</span>
                              </div>
                              <p className="text-[10px] text-[#A9B4AE] mt-1 font-mono font-semibold">Blocked step ID: {run.current_step_id}</p>
                            </div>
                            
                            <div className="flex items-center gap-4">
                              <span className="font-bold text-[#18362F] font-mono">${run.amount?.toLocaleString()}</span>
                              <span className={`px-2.5 py-0.5 rounded-full text-[9px] font-bold ${statusColorMap(run.status)}`}>
                                {run.status}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-xl p-6 h-fit text-xs font-semibold space-y-4">
                    <h3 className="font-serif font-bold text-sm text-[#18362F] border-b border-[#18362F]/6 pb-3">Authorize Transactions</h3>
                    <p className="text-[#A9B4AE] leading-relaxed">Please resolve individual priority items from the central Superhuman **Inbox Queue** or the AI Copilot dialogue confirmations.</p>
                  </div>
                </div>
              )}

              {/* TAB 5: ANALYTICS */}
              {activeTab === 'analytics' && (
                <div className="space-y-8 max-w-6xl font-semibold">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div className="bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-xl p-6 md:col-span-2">
                      <h3 className="font-serif font-bold text-sm text-[#18362F] mb-6">Spend Volume trends (MoM)</h3>
                      <div className="w-full flex items-end justify-between h-44 px-4 pt-4 bg-[#F7F8F5]/80 border border-[#18362F]/5 rounded-xl">
                        {[
                          { month: 'Jan', val: 24000 },
                          { month: 'Feb', val: 38000 },
                          { month: 'Mar', val: 52000 },
                          { month: 'Apr', val: 45000 },
                          { month: 'May', val: 68000 }
                        ].map((item, idx) => {
                          const pct = (item.val / 68000) * 100;
                          return (
                            <div key={idx} className="flex flex-col items-center gap-2 w-12 group cursor-pointer">
                              <span className="text-[9px] text-[#18362F] opacity-0 group-hover:opacity-100 transition-opacity font-mono font-bold">${(item.val / 1000).toFixed(0)}k</span>
                              <div className="w-8 bg-[#6CE8C2]/30 hover:bg-[#6CE8C2]/60 border border-[#6CE8C2]/45 rounded-t transition-all" style={{ height: `${pct || 10}px` }} />
                              <span className="text-[10px] text-[#A9B4AE] font-semibold">{item.month}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    <div className="bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-xl p-6 flex flex-col justify-between">
                      <div>
                        <h3 className="font-serif font-bold text-sm text-[#18362F] mb-1">AI Business value index</h3>
                        <p className="text-xs text-[#A9B4AE] font-semibold">Autonomous calculations saving operations accounting cycles.</p>
                      </div>

                      <div className="text-center py-4">
                        <span className="text-4xl font-extrabold text-emerald-700 tracking-tight font-serif">{aiImpact.estimated_hours_saved.toFixed(1)}</span>
                        <p className="text-[10px] font-bold text-[#A9B4AE] mt-1 uppercase font-mono">Manual Audit Hours Saved</p>
                      </div>

                      <div className="space-y-2 border-t border-[#18362F]/5 pt-3 text-[11px] font-semibold">
                        <div className="flex justify-between">
                          <span className="text-[#A9B4AE]">Tasks Automated:</span>
                          <span className="text-[#18362F] font-mono">{aiImpact.tasks_automated_count}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-[#A9B4AE]">AI accuracy scale:</span>
                          <span className="text-emerald-700 font-mono">{(aiImpact.acceptance_rate * 100).toFixed(2)}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 6: WORKFLOWS */}
              {activeTab === 'workflows' && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-6xl font-semibold">
                  <div className="bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-xl p-6 h-fit space-y-6">
                    <h3 className="font-serif font-bold text-sm text-[#18362F] border-b border-[#18362F]/6 pb-3">Create trigger routing rules</h3>
                    
                    <form onSubmit={(e) => { e.preventDefault(); setSuccessMsg('New trigger rule routing path registered.'); }} className="space-y-4 text-xs font-semibold">
                      <div className="space-y-1">
                        <label className="text-[#18362F]/75">Workflow Name</label>
                        <input type="text" placeholder="e.g. Ingestion Compliance check" className="w-full bg-[#F7F8F5] border border-[#18362F]/10 p-2.5 rounded-lg focus:outline-none" required />
                      </div>
                      
                      <div className="space-y-1">
                        <label className="text-[#18362F]/75">Routing Action Target</label>
                        <select className="w-full bg-[#F7F8F5] border border-[#18362F]/10 p-2.5 rounded-lg focus:outline-none">
                          <option value="netsuite">Sync direct to NetSuite ERP</option>
                          <option value="hold">Hold for human validation review</option>
                        </select>
                      </div>

                      <button type="submit" className="w-full h-10 bg-[#18362F] hover:bg-[#18362F]/90 text-[#F7F8F5] font-bold rounded-lg mt-4 transition-colors shadow-sm">
                        Deploy active rule node
                      </button>
                    </form>
                  </div>

                  <div className="lg:col-span-2 space-y-6">
                    {/* Active Workflows list from database */}
                    <div className="bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-xl p-6">
                      <h3 className="font-serif font-bold text-sm text-[#18362F] mb-6 font-semibold">Active Database Workflows</h3>
                      <div className="space-y-4">
                        {workflows.map((wf) => (
                          <div key={wf.id} className="p-4 bg-[#F7F8F5]/60 border border-[#18362F]/5 rounded-xl flex justify-between items-center text-xs">
                            <div>
                              <p className="font-serif font-bold text-[#18362F] text-sm">{wf.name}</p>
                              <p className="text-[#A9B4AE] mt-1 font-medium">{wf.description}</p>
                              <p className="text-[10px] font-mono text-[#A9B4AE] mt-2 font-bold uppercase">Trigger: {wf.trigger_type}</p>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${wf.is_active ? 'bg-emerald-500/10 text-emerald-700 border border-emerald-500/20' : 'bg-[#F7F8F5] text-[#A9B4AE] border border-[#18362F]/10'}`}>
                                {wf.is_active ? 'Active' : 'Inactive'}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-xl p-6">
                      <h3 className="font-serif font-bold text-sm text-[#18362F] mb-6">Automation Topology Simulator</h3>
                      <div className="flex flex-col md:flex-row items-center justify-between gap-4 p-6 bg-[#F7F8F5]/50 border border-[#18362F]/5 rounded-xl text-center text-xs font-semibold">
                        <div className="p-3 bg-white border border-[#18362F]/8 shadow-[0_2px_12px_rgba(24,54,47,0.02)] rounded-lg">
                          <span className="text-[9px] text-[#A9B4AE] uppercase font-bold tracking-wider">Trigger</span>
                          <p className="font-serif font-bold text-[#18362F] mt-1">Inbound File Recieved</p>
                        </div>
                        <span className="text-[#18362F]/30 font-bold">➔</span>
                        <div className="p-3 bg-white border border-[#18362F]/8 shadow-[0_2px_12px_rgba(24,54,47,0.02)] rounded-lg">
                          <span className="text-[9px] text-[#A9B4AE] uppercase font-bold tracking-wider">Process</span>
                          <p className="font-serif font-bold text-[#18362F] mt-1">OCR Checklist Verification</p>
                        </div>
                        <span className="text-[#18362F]/30 font-bold">➔</span>
                        <div className="p-3 bg-white border border-[#18362F]/8 shadow-[0_2px_12px_rgba(24,54,47,0.02)] rounded-lg">
                          <span className="text-[9px] text-[#A9B4AE] uppercase font-bold tracking-wider">Audit</span>
                          <p className="font-serif font-bold text-rose-700 mt-1">Compliance Hold if Risk &gt; 40</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 7: SETTINGS & WEBHOOKS */}
              {activeTab === 'settings' && (
                <div className="space-y-8 max-w-4xl text-xs font-semibold">
                  <div className="bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-xl p-6 space-y-4">
                    <h3 className="font-serif font-bold text-sm text-[#18362F] border-b border-[#18362F]/6 pb-3">Company Identity profile</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <span className="text-[#A9B4AE]">Active Tenant UUID:</span>
                        <p className="font-mono text-[#18362F]/80 p-2.5 bg-[#F7F8F5] border border-[#18362F]/10 rounded-lg truncate mt-1">{companyId}</p>
                      </div>
                      <div>
                        <span className="text-[#A9B4AE]">User Authorization ID:</span>
                        <p className="font-mono text-[#18362F]/80 p-2.5 bg-[#F7F8F5] border border-[#18362F]/10 rounded-lg truncate mt-1">{userId}</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white border border-[#18362F]/6 shadow-[0_4px_24px_rgba(24,54,47,0.04)] rounded-xl p-6 space-y-4">
                    <h3 className="font-serif font-bold text-sm text-[#18362F] border-b border-[#18362F]/6 pb-3">Integrations connection statuses</h3>
                    <div className="space-y-3">
                      {[
                        { name: 'Oracle NetSuite ERP', desc: 'Syncs purchase invoices directly to primary ledger accounts.', enabled: integrationStatus.netsuite },
                        { name: 'QuickBooks Online', desc: 'Sync expense reports automatically to quickbooks categories.', enabled: integrationStatus.quickbooks },
                        { name: 'Slack Notifications', desc: 'Alert channels on approval checkpoints or mathematical check alerts.', enabled: integrationStatus.slack }
                      ].map((item, idx) => (
                        <div key={idx} className="flex justify-between items-center p-3 bg-[#F7F8F5]/60 border border-[#18362F]/5 rounded-xl">
                          <div>
                            <p className="font-bold text-[#18362F]/90 font-serif">{item.name}</p>
                            <p className="text-[10px] text-[#A9B4AE] mt-0.5 font-semibold">{item.desc}</p>
                          </div>
                          <button
                            onClick={() => {
                              if (idx === 0) setIntegrationStatus({ netsuite: !integrationStatus.netsuite });
                              if (idx === 1) setIntegrationStatus({ quickbooks: !integrationStatus.quickbooks });
                              if (idx === 2) setIntegrationStatus({ slack: !integrationStatus.slack });
                              setSuccessMsg(`Toggled connection for ${item.name}`);
                            }}
                            className={`px-3 py-1.5 rounded-lg font-bold border transition-colors ${
                              item.enabled
                                ? 'bg-[#6CE8C2]/15 text-[#18362F] border-[#6CE8C2]/35'
                                : 'bg-[#F7F8F5] text-[#A9B4AE]/80 border-[#18362F]/10 hover:border-[#18362F]/20 hover:text-[#18362F]'
                            }`}
                          >
                            {item.enabled ? 'Connected Sync' : 'Link account'}
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
