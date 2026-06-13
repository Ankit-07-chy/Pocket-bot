"""
Configuration for personalized support system with free LLM support
"""

import os
from typing import Optional, List
from enum import Enum


class LLMProvider(Enum):
    """Available LLM providers"""
    OLLAMA = "ollama"  # Local, free, private
    GROQ = "groq"  # Free API with rate limits
    HUGGINGFACE = "huggingface"  # Free inference API
    TOGETHER = "together"  # Free tier available
    OPENAI = "openai"  # Paid but included for compatibility


class SupportConfig:
    """Configuration for support system"""

    # LLM Provider Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama").lower()

    # Ollama Configuration (Local, completely free)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral")

    # Groq Configuration (Free API)
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

    # HuggingFace Configuration (Free inference)
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    HUGGINGFACE_MODEL: str = os.getenv("HUGGINGFACE_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")

    # Together.ai Configuration (Free tier)
    TOGETHER_API_KEY: Optional[str] = os.getenv("TOGETHER_API_KEY")
    TOGETHER_MODEL: str = os.getenv("TOGETHER_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")

    # OpenAI Configuration (Paid, for compatibility)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # Common LLM Parameters
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "30"))

    # Chat Configuration
    CONVERSATION_MEMORY_SIZE: int = int(os.getenv("CONVERSATION_MEMORY_SIZE", "10"))
    MAX_CONVERSATION_LENGTH: int = int(os.getenv("MAX_CONVERSATION_LENGTH", "100"))
    CONVERSATION_TIMEOUT: int = int(os.getenv("CONVERSATION_TIMEOUT", "3600"))  # 1 hour

    # Peer Support Configuration
    MAX_PEERS: int = int(os.getenv("MAX_PEERS", "1000"))
    MIN_PEER_REPUTATION: float = float(os.getenv("MIN_PEER_REPUTATION", "3.0"))
    PEER_INACTIVITY_TIMEOUT: int = int(os.getenv("PEER_INACTIVITY_TIMEOUT", "1800"))  # 30 min
    CONNECTION_CLEANUP_DAYS: int = int(os.getenv("CONNECTION_CLEANUP_DAYS", "30"))

    # Rule-Based Configuration
    MIN_RULE_CONFIDENCE: float = float(os.getenv("MIN_RULE_CONFIDENCE", "0.6"))
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))

    # Response Configuration
    AUTO_FALLBACK_TO_AI: bool = os.getenv("AUTO_FALLBACK_TO_AI", "true").lower() == "true"
    RESPONSE_TIMEOUT: int = int(os.getenv("RESPONSE_TIMEOUT", "30"))  # seconds

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")

    # Feature Flags
    ENABLE_AI_SUPPORT: bool = True  # Always enabled - all providers are either free or configured
    ENABLE_RULE_BASED_SUPPORT: bool = os.getenv("ENABLE_RULE_BASED_SUPPORT", "true").lower() == "true"
    ENABLE_PEER_SUPPORT: bool = os.getenv("ENABLE_PEER_SUPPORT", "true").lower() == "true"
    ENABLE_ANALYTICS: bool = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"

    # Language Configuration
    SUPPORTED_LANGUAGES: List[str] = [
        lang.strip()
        for lang in os.getenv("SUPPORTED_LANGUAGES", "en").split(",")
    ]
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")

    # Firebase Configuration (if using)
    FIREBASE_DATABASE_URL: Optional[str] = os.getenv("FIREBASE_DATABASE_URL")
    USE_FIREBASE_STORAGE: bool = bool(FIREBASE_DATABASE_URL)

    # API Configuration
    API_PREFIX: str = os.getenv("API_PREFIX", "/api/support")
    API_RATE_LIMIT: int = int(os.getenv("API_RATE_LIMIT", "100"))  # requests per minute
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))  # seconds

    @classmethod
    def get_config(cls) -> dict:
        """Get full configuration as dictionary"""
        llm_config = {
            "provider": cls.LLM_PROVIDER,
            "temperature": cls.LLM_TEMPERATURE,
            "max_tokens": cls.LLM_MAX_TOKENS,
            "timeout": cls.LLM_TIMEOUT,
        }

        # Add provider-specific config
        if cls.LLM_PROVIDER == "ollama":
            llm_config["ollama"] = {
                "base_url": cls.OLLAMA_BASE_URL,
                "model": cls.OLLAMA_MODEL,
            }
        elif cls.LLM_PROVIDER == "groq":
            llm_config["groq"] = {
                "api_key_set": bool(cls.GROQ_API_KEY),
                "model": cls.GROQ_MODEL,
            }
        elif cls.LLM_PROVIDER == "huggingface":
            llm_config["huggingface"] = {
                "api_key_set": bool(cls.HUGGINGFACE_API_KEY),
                "model": cls.HUGGINGFACE_MODEL,
            }
        elif cls.LLM_PROVIDER == "together":
            llm_config["together"] = {
                "api_key_set": bool(cls.TOGETHER_API_KEY),
                "model": cls.TOGETHER_MODEL,
            }
        elif cls.LLM_PROVIDER == "openai":
            llm_config["openai"] = {
                "api_key_set": bool(cls.OPENAI_API_KEY),
                "model": cls.OPENAI_MODEL,
            }

        return {
            "llm": llm_config,
            "chat": {
                "memory_size": cls.CONVERSATION_MEMORY_SIZE,
                "max_length": cls.MAX_CONVERSATION_LENGTH,
                "timeout": cls.CONVERSATION_TIMEOUT,
            },
            "peer": {
                "max_peers": cls.MAX_PEERS,
                "min_reputation": cls.MIN_PEER_REPUTATION,
                "inactivity_timeout": cls.PEER_INACTIVITY_TIMEOUT,
            },
            "rule_based": {
                "min_confidence": cls.MIN_RULE_CONFIDENCE,
                "max_search_results": cls.MAX_SEARCH_RESULTS,
            },
            "features": {
                "ai_support": cls.ENABLE_AI_SUPPORT,
                "rule_based_support": cls.ENABLE_RULE_BASED_SUPPORT,
                "peer_support": cls.ENABLE_PEER_SUPPORT,
                "analytics": cls.ENABLE_ANALYTICS,
            },
            "languages": {
                "supported": cls.SUPPORTED_LANGUAGES,
                "default": cls.DEFAULT_LANGUAGE,
            }
        }


class SupportPromptConfig:
    """Configuration for prompts"""

    # System prompts
    SYSTEM_PROMPT = """You are a compassionate and knowledgeable personal finance support assistant.
Your role is to help users with budget planning, expense management, savings strategies, and financial wellness.

Communication style:
- Empathetic and non-judgmental
- Clear and easy to understand
- Data-driven when possible
- Practical and actionable
- Encouraging and motivating"""

    # Temperature settings for different scenarios
    TEMPERATURES = {
        "general": 0.7,
        "goal_setting": 0.5,  # More conservative for goals
        "crisis": 0.3,  # Very straightforward for emergencies
        "creative": 0.9,  # More creative for alternative ideas
    }

    # Token limits
    TOKEN_LIMITS = {
        "short": 500,
        "medium": 1500,
        "long": 3000,
    }

    @classmethod
    def get_temperature(cls, scenario: str) -> float:
        """Get temperature for scenario"""
        return cls.TEMPERATURES.get(scenario, 0.7)

    @classmethod
    def get_token_limit(cls, size: str) -> int:
        """Get token limit for response size"""
        return cls.TOKEN_LIMITS.get(size, 1500)


class PeerSupportConfig:
    """Configuration for peer support system"""

    # Reputation thresholds
    RATING_EXCELLENT = 4.5
    RATING_GOOD = 4.0
    RATING_AVERAGE = 3.0
    RATING_POOR = 2.0

    # Scoring system
    INITIAL_REPUTATION = 5.0
    MAX_REPUTATION = 5.0
    MIN_REPUTATION = 1.0

    # Matching criteria
    PREFER_HIGHER_REPUTATION = True
    PREFER_MORE_EXPERIENCE = True
    MATCH_LANGUAGE_PREFERENCE = True
    MATCH_EXPERTISE_EXACTLY = False  # Allow partial matches

    # Connection management
    AUTO_CLOSE_INACTIVE: bool = True
    INACTIVE_THRESHOLD_MINUTES: int = 30
    AUTO_TRANSFER_THRESHOLD: int = 10  # Transfer after 10 failed attempts

    @classmethod
    def get_rating_label(cls, rating: float) -> str:
        """Get label for rating"""
        if rating >= cls.RATING_EXCELLENT:
            return "Excellent"
        elif rating >= cls.RATING_GOOD:
            return "Good"
        elif rating >= cls.RATING_AVERAGE:
            return "Average"
        else:
            return "Needs Improvement"


class AnalyticsConfig:
    """Configuration for analytics"""

    # Events to track
    TRACK_EVENTS = [
        "chat_message_received",
        "chat_response_generated",
        "rule_matched",
        "peer_connection_requested",
        "peer_connection_created",
        "peer_rated",
        "conversation_cleared",
        "ai_fallback",
    ]

    # Metrics to track
    TRACK_METRICS = [
        "total_messages",
        "ai_response_time",
        "rule_match_rate",
        "peer_satisfaction",
        "active_users",
        "peak_hours",
    ]

    # Retention policy
    EVENT_RETENTION_DAYS: int = 90
    METRIC_RETENTION_DAYS: int = 365
    AUTO_CLEANUP: bool = True


class ErrorConfig:
    """Error handling configuration"""

    # Retry settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1  # seconds
    BACKOFF_FACTOR: float = 2.0

    # Error messages
    MESSAGES = {
        "api_key_missing": "OpenAI API key not configured",
        "rate_limit": "Too many requests. Please try again later.",
        "timeout": "Request timed out. Please try again.",
        "invalid_input": "Invalid input. Please check your message.",
        "no_peers": "No peer supporters available at this time.",
        "service_unavailable": "Service temporarily unavailable.",
    }

    @classmethod
    def get_error_message(cls, error_key: str) -> str:
        """Get error message"""
        return cls.MESSAGES.get(error_key, "An error occurred. Please try again.")
