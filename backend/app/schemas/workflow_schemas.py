from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

from app.schemas.base import APIResponseBase


class WorkflowCreateSchema(BaseModel):
    """
    Schema representing user-defined template parameter constraints for workflows.
    """
    name: str = Field(..., max_length=255, description="Human readable name of the workflow.")
    description: Optional[str] = Field(None, description="Detailed instructions of automation.")
    trigger_type: str = Field(..., max_length=100, description="Trigger event key e.g. 'invoice_analyzed'.")
    definition: Dict[str, Any] = Field(..., description="Trigger, conditions, and action step configuration graph.")
    is_active: bool = Field(True, description="Active status indicator.")


class WorkflowResponseSchema(APIResponseBase):
    """
    Response schema returning stored workflow definitions.
    """
    id: str = Field(..., description="Workflow UUID identifier.")
    company_id: str = Field(..., description="Tenant UUID identifier.")
    name: str
    description: Optional[str] = None
    trigger_type: str
    definition: Dict[str, Any]
    is_active: bool


class ApprovalRequestSchema(BaseModel):
    """
    Manually submitted approval decision. Resumes workflow execution threads.
    """
    decision: str = Field(..., description="Acceptance outcome: 'approved' or 'rejected'.")
    approver_id: Optional[str] = Field(None, description="Identifier of the executing authority.")
    comments: Optional[str] = Field(None, description="Manual audit review comments.")

    @field_validator("decision")
    @classmethod
    def validate_decision_options(cls, value: str) -> str:
        value_lower = value.strip().lower()
        if value_lower not in ["approved", "rejected"]:
            raise ValueError("Decision must be either 'approved' or 'rejected'.")
        return value_lower


class WorkflowTriggerRequestSchema(BaseModel):
    """
    Context parameters for manual event triggers.
    """
    event_type: str = Field(..., description="Fired event key.")
    company_id: str = Field(..., description="Tenant UUID context.")
    entity_id: str = Field(..., description="Target Invoice UUID context.")


class AuditStepSchema(BaseModel):
    """
    Single recorded step iteration metadata.
    """
    timestamp: str
    step_id: str
    status: str
    detail: Optional[str] = None


class WorkflowExecutionStateResponseSchema(APIResponseBase):
    """
    Execution tracing response displaying current orchestrator checkpoints.
    """
    agent_run_id: str = Field(..., description="AgentRun logging UUID.")
    workflow_id: Optional[str] = Field(None, description="Parent workflow definition UUID.")
    status: str = Field(..., description="Current running state.")
    current_step_id: Optional[str] = Field(None, description="Currently active/paused graph step ID.")
    audit_trail: List[AuditStepSchema] = Field(default_factory=list, description="Chronological log history.")
