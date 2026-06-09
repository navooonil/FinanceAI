import { create } from 'zustand';

export interface ChatLine {
  id: string;
  role: 'user' | 'assistant';
  message: string;
  timestamp: string;
  intent?: string;
  citations?: string[];
  structuredData?: any;
}

export interface InvoiceItem {
  id: string;
  invoice_number: string | null;
  vendor_name: string | null;
  total_amount: number | null;
  due_date: string | null;
  status: 'pending_ocr' | 'processing' | 'completed' | 'pending_review' | 'failed';
  issue_date: string | null;
}

export interface WorkflowItem {
  id: string;
  name: string;
  description: string;
  trigger_type: string;
  definition: any;
  is_active: boolean;
}

export interface VendorRiskItem {
  vendor_id: string;
  vendor_name: string;
  risk_score: number;
  risk_grade: 'A' | 'B' | 'C' | 'D' | 'F';
  risk_factors: string[];
  total_spend: number;
  invoice_count: number;
}

export interface ApprovalRunItem {
  id: string;
  workflow_id: string;
  workflow_name: string;
  invoice_id: string;
  invoice_number: string;
  vendor_name: string;
  amount: number;
  status: 'pending' | 'waiting_for_approval' | 'approved' | 'rejected' | 'completed' | 'failed';
  current_step_id: string;
  created_at: string;
}

export interface TelemetryEvent {
  id: string;
  timestamp: string;
  event_name: string;
  value: number;
  dimensions: any;
}

export interface IntegrationStatus {
  netsuite: boolean;
  quickbooks: boolean;
  slack: boolean;
  webhooks: Array<{
    id: string;
    target_url: string;
    event_types: string[];
    secret_key: string;
    is_active: boolean;
  }>;
}

export interface BatchDocument {
  id: string;
  filename: string;
  size: string;
  confidence: number;
  amount: number;
  vendor: string;
  status: 'success' | 'failed' | 'processing';
  failure_reason?: string;
}

export interface BatchItem {
  id: string;
  batch_name: string;
  source: 'upload' | 'gmail' | 'gdrive' | 'outlook' | 'erp';
  file_count: number;
  status: 'uploading' | 'processing' | 'needs_review' | 'completed' | 'failed';
  created_at: string;
  assigned_to?: string;
  documents: BatchDocument[];
}

export interface InboxItem {
  id: string;
  type: 'invoice' | 'approval' | 'risk' | 'workflow' | 'cashflow' | 'vendor';
  title: string;
  priority: 'high' | 'medium' | 'low';
  issue: string;
  impact: string;
  recommendation: string;
  assigned_to?: string;
  is_archived: boolean;
  metadata: any;
  created_at: string;
}

export interface FinanceStoreState {
  companyId: string;
  userId: string;
  sessionId: string;
  invoices: InvoiceItem[];
  workflows: WorkflowItem[];
  vendors: VendorRiskItem[];
  approvalRuns: ApprovalRunItem[];
  eventsLog: TelemetryEvent[];
  integrationStatus: IntegrationStatus;
  chatHistory: ChatLine[];
  isChatLoading: boolean;
  activeTab: string;

  // OS Extended States
  onboardingCompleted: boolean;
  copilotMode: 'ask' | 'analyze' | 'investigate' | 'execute' | 'simulate';
  inboxItems: InboxItem[];
  batches: BatchItem[];
  guidedTourCompleted: boolean;
  
  // Actions
  setCompanyId: (id: string) => void;
  setUserId: (id: string) => void;
  setSessionId: (id: string) => void;
  setInvoices: (invoices: InvoiceItem[]) => void;
  addInvoice: (invoice: InvoiceItem) => void;
  updateInvoiceStatus: (id: string, status: InvoiceItem['status']) => void;
  
  setWorkflows: (workflows: WorkflowItem[]) => void;
  addWorkflow: (workflow: WorkflowItem) => void;
  
  setVendors: (vendors: VendorRiskItem[]) => void;
  
  setApprovalRuns: (runs: ApprovalRunItem[]) => void;
  updateApprovalRunStatus: (id: string, status: ApprovalRunItem['status']) => void;
  
  setEventsLog: (events: TelemetryEvent[]) => void;
  addEventLog: (event: TelemetryEvent) => void;
  
  setIntegrationStatus: (status: Partial<IntegrationStatus>) => void;
  addWebhook: (webhook: IntegrationStatus['webhooks'][0]) => void;
  
  addChatLine: (line: ChatLine) => void;
  setChatHistory: (history: ChatLine[]) => void;
  setChatLoading: (loading: boolean) => void;
  setActiveTab: (tab: string) => void;

  // OS Extended Actions
  setOnboardingCompleted: (completed: boolean) => void;
  setCopilotMode: (mode: FinanceStoreState['copilotMode']) => void;
  addInboxItem: (item: InboxItem) => void;
  setInboxItems: (items: InboxItem[]) => void;
  archiveInboxItem: (id: string) => void;
  assignInboxItem: (id: string, name: string | undefined) => void;
  addBatch: (batch: BatchItem) => void;
  updateBatchStatus: (id: string, status: BatchItem['status']) => void;
  updateBatchDocument: (batchId: string, docId: string, updates: Partial<BatchDocument>) => void;
  setGuidedTourCompleted: (completed: boolean) => void;
}

export const useFinanceStore = create<FinanceStoreState>((set) => ({
  companyId: '4b6f12d5-e2bb-41a4-b0e6-5778a87b415a',
  userId: 'a9a3b68f-bfd2-430b-9dfb-cb784f18a211',
  sessionId: '7d9b32c6-302a-436f-b2bb-b072c49925e0',
  invoices: [
    {
      id: 'inv-high-1',
      invoice_number: 'INV-2026-889',
      vendor_name: 'Z-Axis Engineering Labs',
      total_amount: 68500.00,
      due_date: '2026-07-06',
      status: 'pending_review',
      issue_date: '2026-06-06'
    }
  ],
  workflows: [
    {
      id: 'wf-1',
      name: 'High-Value Risk Gate',
      description: 'Require VP authorization for invoices exceeding $50,000.',
      trigger_type: 'invoice_ingested',
      definition: {
        trigger: {
          conditions: [
            { field: 'invoice.total_amount', operator: 'greater_than', value: 50000 }
          ]
        },
        steps: [
          { type: 'approval', role: 'VP_FINANCE', label: 'VP Spend Review' }
        ]
      },
      is_active: true
    },
    {
      id: 'wf-2',
      name: 'Auto-Approve Micro-Spend',
      description: 'Instantly approve general bills under $1,000 with low-risk vendors.',
      trigger_type: 'invoice_ingested',
      definition: {
        trigger: {
          conditions: [
            { field: 'invoice.total_amount', operator: 'less_than', value: 1000 },
            { field: 'vendor.risk_score', operator: 'less_than', value: 30 }
          ]
        },
        steps: [
          { type: 'update_status', status: 'completed', label: 'Mark Approved' }
        ]
      },
      is_active: true
    }
  ],
  vendors: [
    {
      vendor_id: 'v-1',
      vendor_name: 'Apex Global Logistics',
      risk_score: 12,
      risk_grade: 'A',
      risk_factors: [],
      total_spend: 345000.00,
      invoice_count: 24
    },
    {
      vendor_id: 'v-2',
      vendor_name: 'Sentry Security Services',
      risk_score: 45,
      risk_grade: 'C',
      risk_factors: ['Outlier transaction amount detected', 'Weekend issuance anomaly'],
      total_spend: 85200.00,
      invoice_count: 8
    },
    {
      vendor_id: 'v-3',
      vendor_name: 'Z-Axis Engineering Labs',
      risk_score: 82,
      risk_grade: 'F',
      risk_factors: ['High mathematical checksum failures', 'Duplicate invoice flags resolved previously'],
      total_spend: 120400.00,
      invoice_count: 5
    }
  ],
  approvalRuns: [
    {
      id: 'run-1',
      workflow_id: 'wf-1',
      workflow_name: 'High-Value Risk Gate',
      invoice_id: 'inv-high-1',
      invoice_number: 'INV-2026-889',
      vendor_name: 'Z-Axis Engineering Labs',
      amount: 68500.00,
      status: 'waiting_for_approval',
      current_step_id: 'vp-approval-step',
      created_at: new Date(Date.now() - 3600000 * 2).toISOString()
    }
  ],
  eventsLog: [
    {
      id: 'evt-1',
      timestamp: new Date(Date.now() - 60000).toISOString(),
      event_name: 'invoice_uploaded',
      value: 1,
      dimensions: { file_name: 'logistics_invoice.pdf', file_size: 145200 }
    },
    {
      id: 'evt-2',
      timestamp: new Date(Date.now() - 50000).toISOString(),
      event_name: 'ocr_completed',
      value: 1,
      dimensions: { invoice_id: 'inv-high-1', confidence: 0.94 }
    },
    {
      id: 'evt-3',
      timestamp: new Date(Date.now() - 40000).toISOString(),
      event_name: 'invoice_anomaly',
      value: 0,
      dimensions: { invoice_id: 'inv-high-1', is_anomaly: false }
    }
  ],
  integrationStatus: {
    netsuite: true,
    quickbooks: false,
    slack: true,
    webhooks: [
      {
        id: 'wh-1',
        target_url: 'https://api.acme-corp.com/hooks/finance',
        event_types: ['invoice.completed', 'workflow.paused'],
        secret_key: 'sec_hmac_xxxxxxxxxxxxxx',
        is_active: true
      }
    ]
  },
  chatHistory: [
    {
      id: 'welcome-message',
      role: 'assistant',
      message: 'Hello! I am your AI Finance Operations Employee. I can scan your invoices, evaluate supplier risk grades, audit checksum formulas, trace approvals, and help configure automation pathways. What would you like to explore today?',
      timestamp: new Date().toISOString()
    }
  ],
  isChatLoading: false,
  activeTab: 'inbox',

  // OS Extended Initial Values
  onboardingCompleted: false,
  copilotMode: 'ask',
  guidedTourCompleted: true,
  inboxItems: [
    {
      id: 'inbox-1',
      type: 'risk',
      title: 'Anomalous Z-Axis Invoice Flagged',
      priority: 'high',
      issue: 'Z-Axis Engineering Labs invoice INV-2026-889 ($68,500.00) was issued on a Saturday.',
      impact: 'This transaction is 2.8σ above the historical mean for this supplier, triggering risk profile degradation to Grade F.',
      recommendation: 'Verify weekend procurement logs or reject the invoice in the manual approval gateway.',
      is_archived: false,
      metadata: { invoice_id: 'inv-high-1', vendor_name: 'Z-Axis Engineering Labs', amount: 68500.00 },
      created_at: new Date(Date.now() - 3600000 * 2).toISOString()
    },
    {
      id: 'inbox-2',
      type: 'cashflow',
      title: 'TTM Spend Velocity Surge',
      priority: 'medium',
      issue: 'Spend velocity increased by 12.4% MoM, largely driven by Q2 engineering equipment procurement.',
      impact: 'Expected cash runway will decrease from 110 days to 94 days if the pace continues through June.',
      recommendation: 'Run cashflow projections checks in Copilot or review department budgets.',
      is_archived: false,
      metadata: { growth_rate: 0.124, target_runway_days: 94 },
      created_at: new Date(Date.now() - 3600000 * 4).toISOString()
    },
    {
      id: 'inbox-3',
      type: 'vendor',
      title: 'Compliance Certificate Expiry Alert',
      priority: 'high',
      issue: 'Sentry Security Services security compliance certification has expired.',
      impact: 'Violation of company supplier vendor procurement criteria. Risk score index increased to 45.',
      recommendation: 'Trigger a request command to supplier contact to update SOC-2 credentials.',
      is_archived: false,
      metadata: { vendor_id: 'v-2', vendor_name: 'Sentry Security Services' },
      created_at: new Date(Date.now() - 3600000 * 6).toISOString(),
      assigned_to: 'Sarah (Analyst)'
    }
  ],
  batches: [
    {
      id: 'batch-1',
      batch_name: 'Gmail Ingestion _ 2026-06-09',
      source: 'gmail',
      file_count: 2,
      status: 'needs_review',
      created_at: new Date(Date.now() - 60000 * 15).toISOString(),
      documents: [
        {
          id: 'doc-1',
          filename: 'sentry_security_inv8.pdf',
          size: '1.2 MB',
          confidence: 96.2,
          amount: 12800,
          vendor: 'Sentry Security Services',
          status: 'success'
        },
        {
          id: 'doc-2',
          filename: 'zaxis_weekly_lab.pdf',
          size: '2.4 MB',
          confidence: 62.4,
          amount: 68500,
          vendor: 'Z-Axis Engineering Labs',
          status: 'failed',
          failure_reason: 'Anomalous Saturday issuance flagged. Risk grade degraded.'
        }
      ]
    },
    {
      id: 'batch-2',
      batch_name: 'Supplier Invoices (Bulk ZIP)',
      source: 'upload',
      file_count: 3,
      status: 'completed',
      created_at: new Date(Date.now() - 3600000 * 1).toISOString(),
      documents: [
        {
          id: 'doc-3',
          filename: 'apex_logistics_invoice_24.pdf',
          size: '840 KB',
          confidence: 99.1,
          amount: 14500,
          vendor: 'Apex Global Logistics',
          status: 'success'
        },
        {
          id: 'doc-4',
          filename: 'apex_logistics_invoice_25.pdf',
          size: '890 KB',
          confidence: 98.7,
          amount: 16200,
          vendor: 'Apex Global Logistics',
          status: 'success'
        },
        {
          id: 'doc-5',
          filename: 'meridian_couriers_90a.pdf',
          size: '1.1 MB',
          confidence: 95.5,
          amount: 4200,
          vendor: 'Meridian Co.',
          status: 'success'
        }
      ]
    }
  ],

  setCompanyId: (id) => set({ companyId: id }),
  setUserId: (id) => set({ userId: id }),
  setSessionId: (id) => set({ sessionId: id }),
  setInvoices: (invoices) => set({ invoices }),
  addInvoice: (invoice) => set((state) => ({ invoices: [invoice, ...state.invoices] })),
  updateInvoiceStatus: (id, status) => set((state) => ({
    invoices: state.invoices.map((inv) => inv.id === id ? { ...inv, status } : inv)
  })),

  setWorkflows: (workflows) => set({ workflows }),
  addWorkflow: (workflow) => set((state) => ({ workflows: [...state.workflows, workflow] })),

  setVendors: (vendors) => set({ vendors }),

  setApprovalRuns: (runs) => set({ approvalRuns: runs }),
  updateApprovalRunStatus: (id, status) => set((state) => ({
    approvalRuns: state.approvalRuns.map((run) => run.id === id ? { ...run, status } : run)
  })),

  setEventsLog: (events) => set({ eventsLog: events }),
  addEventLog: (event) => set((state) => ({ eventsLog: [event, ...state.eventsLog] })),

  setIntegrationStatus: (status) => set((state) => ({
    integrationStatus: { ...state.integrationStatus, ...status }
  })),
  addWebhook: (webhook) => set((state) => ({
    integrationStatus: {
      ...state.integrationStatus,
      webhooks: [...state.integrationStatus.webhooks, webhook]
    }
  })),

  addChatLine: (line) => set((state) => ({ chatHistory: [...state.chatHistory, line] })),
  setChatHistory: (history) => set({ chatHistory: history }),
  setChatLoading: (loading) => set({ isChatLoading: loading }),
  setActiveTab: (tab) => set({ activeTab: tab }),

  // OS Extended Actions
  setOnboardingCompleted: (completed) => set({ onboardingCompleted: completed }),
  setCopilotMode: (mode) => set({ copilotMode: mode }),
  addInboxItem: (item) => set((state) => ({ inboxItems: [item, ...state.inboxItems] })),
  setInboxItems: (items) => set({ inboxItems: items }),
  archiveInboxItem: (id) => set((state) => ({
    inboxItems: state.inboxItems.map(item => item.id === id ? { ...item, is_archived: true } : item)
  })),
  assignInboxItem: (id, name) => set((state) => ({
    inboxItems: state.inboxItems.map(item => item.id === id ? { ...item, assigned_to: name } : item)
  })),
  addBatch: (batch) => set((state) => ({ batches: [batch, ...state.batches] })),
  updateBatchStatus: (id, status) => set((state) => ({
    batches: state.batches.map(b => b.id === id ? { ...b, status } : b)
  })),
  updateBatchDocument: (batchId, docId, updates) => set((state) => ({
    batches: state.batches.map(b => b.id === batchId ? {
      ...b,
      documents: b.documents.map(d => d.id === docId ? { ...d, ...updates } : d)
    } : b)
  })),
  setGuidedTourCompleted: (completed) => set({ guidedTourCompleted: completed })
}));
