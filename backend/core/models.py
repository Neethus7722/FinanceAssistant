# NextGen Revenue Insights Assistant - Complete Schema Definitions
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Basic API schemas
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: Optional[str] = None

class ChatHistoryRequest(BaseModel):
    session_id: str
    user_id: str

class RAGQueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None

class ExcelIngestRequest(BaseModel):
    container_name: str
    blob_name: str

class AdvancedRAGRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    user_role: Optional[str] = 'user'

# Agent Response Schemas
class AgentResponse(BaseModel):
    """Base response schema for all agents."""
    agent_name: str
    status: str = "success"
    execution_time: datetime
    errors: List[str] = Field(default_factory=list)

class ForecastResult(BaseModel):
    """Schema for Advanced Forecast Agent results using Prophet + XGBoost."""
    quarterly_forecast: Dict[str, float]
    monthly_forecast: Dict[str, float]
    total_pipeline_value: float
    weighted_forecast: float
    confidence_level: float
    key_opportunities: List[Dict[str, Any]]
    ai_insights: str
    
    # Advanced forecasting fields
    model_performance: Optional[Dict[str, float]] = None
    forecast_dates: Optional[List[Any]] = None
    confidence_bounds: Optional[Dict[str, List[float]]] = None
    feature_importance: Optional[Dict[str, float]] = None
    model_weights: Optional[Dict[str, float]] = None
    
    generated_at: datetime

class RiskAssessment(BaseModel):
    """Schema for Risk Agent results."""
    high_risk_deals: List[Dict[str, Any]]
    medium_risk_deals: List[Dict[str, Any]]
    risk_factors: Dict[str, Any]
    overall_risk_score: float
    mitigation_recommendations: str
    assessed_at: datetime

class CXOSummary(BaseModel):
    """Schema for CXO Agent results."""
    executive_summary: str
    key_metrics: Dict[str, Any]
    strategic_recommendations: List[str]
    risk_alerts: List[str]
    generated_at: datetime

# CRM Integration Schemas
class OpportunityData(BaseModel):
    """Schema for CRM opportunity data."""
    opportunity_id: str
    name: str
    estimated_value: float
    close_probability: float
    estimated_close_date: Optional[datetime]
    sales_stage: str
    account_name: str
    owner: str

class CRMDataResponse(BaseModel):
    """Schema for CRM data response."""
    opportunities: List[OpportunityData]
    accounts: List[Dict[str, Any]]
    total_pipeline_value: float
    retrieved_at: datetime

# Workflow Response Schemas
class WorkflowResponse(BaseModel):
    """Complete workflow response schema."""
    status: str
    query: str
    query_type: Optional[str]
    agents_executed: List[str]
    execution_time: str
    errors: List[str]
    reasoning_steps: List[str]
    
    # Agent results (optional)
    rag_result: Optional[Dict[str, Any]] = None
    forecast: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    executive_summary: Optional[Dict[str, Any]] = None
    
    # Evidence panel
    evidence: Dict[str, Any]

# Authentication Schemas
class UserProfile(BaseModel):
    """User profile schema for Azure AD integration."""
    user_id: str
    email: str
    name: str
    role: str
    department: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)

class TokenData(BaseModel):
    """JWT token data schema."""
    user_id: Optional[str] = None
    role: Optional[str] = None
    scopes: List[str] = Field(default_factory=list)
