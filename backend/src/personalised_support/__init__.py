"""
Personalised Support Module for POKET-BOT
Provides AI-powered financial advice, chatbot assistance, and peer support.

Module-level singletons are created once here so every import shares the
same in-memory state (conversation history, peer registry, etc.).
"""

# ---------------------------------------------------------------------------
# Module-level singletons — created once, shared by all importers
# ---------------------------------------------------------------------------

from .chat_manager import ChatManager
from .storage import (
    ConversationStorage,
    PeerSupportStorage,
    KnowledgeBaseStorage,
    AnalyticsStorage,
)

# Shared instances
chat_manager: ChatManager = ChatManager()
conversation_storage: ConversationStorage = ConversationStorage()
peer_storage: PeerSupportStorage = PeerSupportStorage()
knowledge_base: KnowledgeBaseStorage = KnowledgeBaseStorage()
analytics: AnalyticsStorage = AnalyticsStorage()

# ---------------------------------------------------------------------------
# Re-exports for convenience
# ---------------------------------------------------------------------------

from .langchain_chatbot import LangChainChatBot
from .rule_based_support import RuleBasedSupport, SupportCategory
from .peer_support import PeerSupportSystem
from .chat_manager import SupportType
from .llm_provider import (
    LLMProviderFactory,
    BaseLLMProvider,
    OllamaProvider,
    GroqProvider,
    HuggingFaceProvider,
    TogetherProvider,
    OpenAIProvider,
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
    SupportAnalysis,
)

__all__ = [
    # Singletons
    "chat_manager",
    "conversation_storage",
    "peer_storage",
    "knowledge_base",
    "analytics",
    # Core classes
    "LangChainChatBot",
    "RuleBasedSupport",
    "PeerSupportSystem",
    "ChatManager",
    # LLM Providers
    "LLMProviderFactory",
    "BaseLLMProvider",
    "OllamaProvider",
    "GroqProvider",
    "HuggingFaceProvider",
    "TogetherProvider",
    "OpenAIProvider",
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
