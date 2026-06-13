"""
Schemas for personalized support chatbot
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = None
    message_type: Optional[str] = None  # "ai", "rule_based", "peer"


class ChatRequest(BaseModel):
    """Chat request from user"""
    user_id: str
    message: str
    conversation_context: Optional[List[ChatMessage]] = None
    support_type: Optional[str] = None  # "auto", "ai", "rule_based", "peer"


class ChatResponse(BaseModel):
    """Chat response"""
    user_id: str
    message: str
    message_type: str  # "ai", "rule_based", "peer"
    confidence: Optional[float] = None
    suggested_actions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None


class ConversationHistory(BaseModel):
    """Store conversation history"""
    user_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
    context_data: Optional[Dict[str, Any]] = None


class RuleBasedResponse(BaseModel):
    """Response from rule-based system"""
    matched_rule: str
    response: str
    category: str
    suggested_next_steps: Optional[List[str]] = None


class PeerSupportRequest(BaseModel):
    """Request for peer support connection"""
    user_id: str
    issue_category: str
    description: str
    preferred_language: Optional[str] = "en"


class PeerProfile(BaseModel):
    """Peer support user profile"""
    peer_id: str
    expertise_areas: List[str]
    reputation_score: float
    total_helpings: int
    availability: bool
    languages: List[str]


class PeerSupportConnection(BaseModel):
    """Active peer support connection"""
    connection_id: str
    user_id: str
    peer_id: str
    issue_category: str
    status: str  # "active", "closed", "transferred"
    created_at: datetime
    closed_at: Optional[datetime] = None
    rating: Optional[float] = None


class SupportAnalysis(BaseModel):
    """Analysis of support needs"""
    user_id: str
    identified_issues: List[str]
    recommended_support_type: str  # "ai", "rule_based", "peer"
    urgency_level: str  # "low", "medium", "high"
    confidence_score: float
    reasoning: str
