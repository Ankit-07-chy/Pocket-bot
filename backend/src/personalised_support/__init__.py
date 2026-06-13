"""
Personalized Support System
AI chatbot, rule-based guidance, and peer support for financial assistance
"""

from .langchain_chatbot import LangChainChatBot
from .rule_based_support import RuleBasedSupport, SupportCategory
from .peer_support import PeerSupportSystem
from .chat_manager import ChatManager, SupportType
from .storage import (
    ConversationStorage,
    PeerSupportStorage,
    KnowledgeBaseStorage,
    AnalyticsStorage
)
from .schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ConversationHistory,
    RuleBasedResponse,
    PeerSupportRequest,
    PeerProfile,
    PeerSupportConnection,
    SupportAnalysis
)

__all__ = [
    # Core systems
    "LangChainChatBot",
    "RuleBasedSupport",
    "PeerSupportSystem",
    "ChatManager",
    # Enums
    "SupportType",
    "SupportCategory",
    # Storage
    "ConversationStorage",
    "PeerSupportStorage",
    "KnowledgeBaseStorage",
    "AnalyticsStorage",
    # Schemas
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ConversationHistory",
    "RuleBasedResponse",
    "PeerSupportRequest",
    "PeerProfile",
    "PeerSupportConnection",
    "SupportAnalysis",
]

# Initialize default instances
chat_manager = ChatManager()
conversation_storage = ConversationStorage()
peer_storage = PeerSupportStorage()
knowledge_base = KnowledgeBaseStorage()
analytics = AnalyticsStorage()
