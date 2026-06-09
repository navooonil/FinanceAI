const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const financeApi = {
  /**
   * Upload an invoice document file.
   */
  async uploadInvoice(companyId: string, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('company_id', companyId);
    formData.append('file', file);

    const response = await fetch(`${BASE_URL}/v1/invoices/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Failed to upload document.' }));
      throw new Error(err.detail || 'Upload failed.');
    }

    return response.json();
  },

  /**
   * Run the multi-agent LangGraph workflow validation checks.
   */
  async triggerAgentProcess(companyId: string, invoiceId: string): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/agents/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_id: companyId,
        invoice_id: invoiceId,
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Failed to execute agent process.' }));
      throw new Error(err.detail || 'Workflow execution failed.');
    }

    return response.json();
  },

  /**
   * Send a conversational query message to the AI Finance Copilot.
   */
  async sendCopilotMessage(
    companyId: string,
    userId: string,
    sessionId: string,
    message: string
  ): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/copilot/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_id: companyId,
        user_id: userId,
        session_id: sessionId,
        message: message,
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Copilot query failed.' }));
      throw new Error(err.detail || 'Copilot communication failed.');
    }

    return response.json();
  },

  /**
   * Retrieve platform telemetry aggregates and KPIs.
   */
  async getBusinessKPIs(companyId: string): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/analytics-reporting/kpis/${companyId}`);
    if (!response.ok) {
      throw new Error('Failed to retrieve business metrics.');
    }
    return response.json();
  },

  /**
   * Retrieve spending trend analysis.
   */
  async getSpendTrends(companyId: string): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/analytics/trends/${companyId}`);
    if (!response.ok) {
      throw new Error('Failed to retrieve monthly spend patterns.');
    }
    return response.json();
  },

  /**
   * Retrieve prioritized payment priorities queue.
   */
  async getPaymentPriorities(companyId: string): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/analytics/prioritize-payments/${companyId}`);
    if (!response.ok) {
      throw new Error('Failed to retrieve prioritized payment queues.');
    }
    return response.json();
  },

  /**
   * Retrieve all active registered workflows.
   */
  async getWorkflows(companyId: string): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/workflows/${companyId}`);
    if (!response.ok) {
      throw new Error('Failed to load registered workflows.');
    }
    return response.json();
  },

  /**
   * Register a new workflow definition.
   */
  async createWorkflow(
    companyId: string,
    payload: { name: string; description: string; trigger_type: string; definition: any; is_active: boolean }
  ): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/workflows?company_id=${companyId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Failed to create workflow.' }));
      throw new Error(err.detail || 'Workflow creation failed.');
    }

    return response.json();
  },

  /**
   * Manually trigger a workflow event.
   */
  async triggerWorkflow(companyId: string, entityId: string, eventType: string): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/workflows/trigger`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_id: companyId,
        entity_id: entityId,
        event_type: eventType,
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Failed to trigger workflow.' }));
      throw new Error(err.detail || 'Workflow trigger failed.');
    }

    return response.json();
  },

  /**
   * Resume a paused workflow approval stage decision.
   */
  async submitApprovalDecision(
    agentRunId: string,
    decision: 'approved' | 'rejected',
    approverId: string,
    comments: string
  ): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/workflows/approval/${agentRunId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        decision,
        approver_id: approverId,
        comments,
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Failed to submit approval.' }));
      throw new Error(err.detail || 'Approval submission failed.');
    }

    return response.json();
  },

  /**
   * Retrieve vendor operational risk analysis indexes.
   */
  async getVendorRiskReports(companyId: string): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/analytics/vendor-risk/${companyId}`);
    if (!response.ok) {
      throw new Error('Failed to retrieve vendor risk indices.');
    }
    return response.json();
  },

  /**
   * Retrieve dynamic conversion funnel stages.
   */
  async getAnalyticsFunnel(companyId: string): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/analytics-reporting/funnel/${companyId}`);
    if (!response.ok) {
      throw new Error('Failed to retrieve analytics funnel stage details.');
    }
    return response.json();
  },

  /**
   * Retrieve AI business impact (hours saved, automated counts).
   */
  async getAIImpactMetrics(companyId: string): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/analytics-reporting/ai-impact/${companyId}`);
    if (!response.ok) {
      throw new Error('Failed to retrieve AI operations impact aggregates.');
    }
    return response.json();
  },

  /**
   * Retrieve growth aggregates (DAU, stickiness, retention).
   */
  async getGrowthMetrics(companyId: string): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/analytics-reporting/growth/${companyId}`);
    if (!response.ok) {
      throw new Error('Failed to retrieve platform engagement telemetry.');
    }
    return response.json();
  },

  /**
   * Ingest a custom analytics tracking event.
   */
  async trackAnalyticsEvent(
    companyId: string,
    eventName: string,
    value: number,
    dimensions: any
  ): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/analytics-reporting/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_id: companyId,
        event_name: eventName,
        value,
        dimensions,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to record telemetry log event.');
    }

    return response.json();
  },

  /**
   * Register a new webhook endpoint.
   */
  async registerWebhook(companyId: string, targetUrl: string, eventScopes: string[]): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/integrations/webhooks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_id: companyId,
        target_url: targetUrl,
        event_scopes: eventScopes,
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Failed to configure webhook.' }));
      throw new Error(err.detail || 'Webhook configuration failed.');
    }

    return response.json();
  },

  /**
   * Configure external connector.
   */
  async configureConnector(companyId: string, systemName: string, credentials: any): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/integrations/configs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_id: companyId,
        system_name: systemName,
        credentials,
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Failed to configure connector.' }));
      throw new Error(err.detail || 'Connector configuration failed.');
    }

    return response.json();
  },

  /**
   * Fetch list of invoices for a company.
   */
  async getInvoices(companyId: string): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/invoices/${companyId}`);
    if (!response.ok) {
      throw new Error('Failed to retrieve invoices.');
    }
    return response.json();
  },

  /**
   * Fetch list of workflow approvals (agent runs) for a company.
   */
  async getApprovals(companyId: string): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/workflows/approvals/${companyId}`);
    if (!response.ok) {
      throw new Error('Failed to retrieve workflow approvals.');
    }
    return response.json();
  },

  /**
   * Fetch dynamic inbox action items for a company.
   */
  async getInbox(companyId: string): Promise<any> {
    const response = await fetch(`${BASE_URL}/v1/inbox/${companyId}`);
    if (!response.ok) {
      throw new Error('Failed to retrieve inbox action items.');
    }
    return response.json();
  }
};
