from fastapi import APIRouter

from app.api.v1.endpoints import router as v1_router
from app.api.v1.rag_endpoints import router as rag_router
from app.api.v1.agent_endpoints import router as agent_router
from app.api.v1.analytics_endpoints import router as analytics_router
from app.api.v1.workflow_endpoints import router as workflow_router
from app.api.v1.copilot_endpoints import router as copilot_router
from app.api.v1.analytics_reporting_endpoints import router as analytics_reporting_router
from app.api.v1.integration_endpoints import router as integration_router

api_router = APIRouter()

# Include version 1 routers
api_router.include_router(v1_router, prefix="/v1", tags=["Infrastructure"])
api_router.include_router(rag_router, prefix="/v1/rag", tags=["RAG System"])
api_router.include_router(agent_router, prefix="/v1/agents", tags=["LangGraph Multi-Agent"])
api_router.include_router(analytics_router, prefix="/v1/analytics", tags=["Financial Intelligence Engine"])
api_router.include_router(workflow_router, prefix="/v1/workflows", tags=["Workflow Automation Engine"])
api_router.include_router(copilot_router, prefix="/v1/copilot", tags=["AI Finance Copilot"])
api_router.include_router(analytics_reporting_router, prefix="/v1/analytics-reporting", tags=["Product Analytics & BI Layer"])
api_router.include_router(integration_router, prefix="/v1/integrations", tags=["Developer Platform & Integration Layer"])
