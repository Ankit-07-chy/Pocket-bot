"""
LLM Provider abstraction layer supporting multiple free LLM services
"""
from __future__ import annotations

import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    def chat(self, prompt: str, **kwargs) -> str:
        """Generate response from a single prompt string."""
        pass

    def chat_with_history(self, messages: List[dict], **kwargs) -> str:
        """
        Generate a response from a list of role/content message dicts.
        Default implementation flattens to a plain-text prompt.
        Subclasses should override this for proper multi-turn support.
        """
        plain = "\n\n".join(
            f"{m['role'].capitalize()}: {m['content']}" for m in messages
        )
        return self.chat(plain, **kwargs)

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        pass


class OllamaProvider(BaseLLMProvider):
    """Local Ollama provider (completely free, private)"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url
        self.model = model
        self._client = None
        self._initialize()

    def _initialize(self):
        """Initialize Ollama client"""
        try:
            # Try to import from langchain_community first (newer versions)
            try:
                from langchain_community.llms import Ollama
            except ImportError:
                # Fall back to older langchain versions
                from langchain.llms import Ollama

            self._client = Ollama(base_url=self.base_url, model=self.model)
            logger.info(f"Initialized Ollama provider with model: {self.model}")
        except ImportError as e:
            logger.error(f"Ollama not installed. Install with: pip install ollama langchain-community. Error: {e}")
            raise

    def chat(self, prompt: str, **kwargs) -> str:
        """Generate response using Ollama"""
        if not self._client:
            raise RuntimeError("Ollama client not initialized")

        try:
            response = self._client.invoke(prompt)
            return response
        except Exception as e:
            logger.error(f"Error calling Ollama: {str(e)}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "ollama",
            "model": self.model,
            "base_url": self.base_url,
            "type": "local",
            "cost": "free",
        }


class GroqProvider(BaseLLMProvider):
    """
    Groq API provider (free tier).
    Uses llama-3.3-70b-versatile which is available on the free tier.
    Supports full multi-turn conversation via chat_with_history().
    """

    # Groq free-tier model that supports the chat completions endpoint
    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        self.api_key = api_key
        self.model = model
        self._client = None
        self._initialize()

    def _initialize(self):
        """Initialize Groq client via langchain-groq."""
        try:
            from langchain_groq import ChatGroq
        except ImportError as e:
            logger.error(
                "langchain-groq not installed. Run: pip install langchain-groq"
            )
            raise

        self._client = ChatGroq(
            groq_api_key=self.api_key,
            model_name=self.model,
            temperature=0.7,
        )
        logger.info(f"Initialised Groq provider with model: {self.model}")

    def chat(self, prompt: str, **kwargs) -> str:
        """Send a single-turn prompt and return the text response."""
        if not self._client:
            raise RuntimeError("Groq client not initialised")
        from langchain_core.messages import HumanMessage, SystemMessage
        response = self._client.invoke([HumanMessage(content=prompt)])
        return response.content

    def chat_with_history(self, messages: List[dict], **kwargs) -> str:
        """
        Send a multi-turn conversation to Groq.

        Args:
            messages: list of {"role": "system"|"user"|"assistant", "content": "..."}

        Returns:
            The assistant reply as a string.
        """
        if not self._client:
            raise RuntimeError("Groq client not initialised")

        from langchain_core.messages import (
            HumanMessage, AIMessage, SystemMessage
        )

        lc_messages = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))

        response = self._client.invoke(lc_messages)
        return response.content

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "groq",
            "model": self.model,
            "type": "api",
            "cost": "free_tier",
            "rate_limit": "30 requests/minute on free tier",
        }


class HuggingFaceProvider(BaseLLMProvider):
    """HuggingFace Inference API provider (free tier available)"""

    def __init__(self, api_key: str, model: str = "mistralai/Mistral-7B-Instruct-v0.1"):
        self.api_key = api_key
        self.model = model
        self._client = None
        self._initialize()

    def _initialize(self):
        """Initialize HuggingFace client"""
        try:
            # Try newer version first
            try:
                from langchain_community.llms import HuggingFaceHub
            except ImportError:
                from langchain.llms import HuggingFaceHub

            self._client = HuggingFaceHub(
                repo_id=self.model,
                huggingfacehub_api_token=self.api_key,
                model_kwargs={"temperature": 0.7, "max_length": 2000},
            )
            logger.info(f"Initialized HuggingFace provider with model: {self.model}")
        except ImportError as e:
            logger.error(f"HuggingFace not installed. Install with: pip install huggingface-hub langchain-community. Error: {e}")
            raise

    def chat(self, prompt: str, **kwargs) -> str:
        """Generate response using HuggingFace"""
        if not self._client:
            raise RuntimeError("HuggingFace client not initialized")

        try:
            response = self._client(prompt)
            return response
        except Exception as e:
            logger.error(f"Error calling HuggingFace: {str(e)}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "huggingface",
            "model": self.model,
            "type": "api",
            "cost": "free_tier",
            "rate_limit": "Varies by model",
        }


class TogetherProvider(BaseLLMProvider):
    """Together.ai provider (free tier available)"""

    def __init__(self, api_key: str, model: str = "mistralai/Mistral-7B-Instruct-v0.1"):
        self.api_key = api_key
        self.model = model
        self._client = None
        self._initialize()

    def _initialize(self):
        """Initialize Together.ai client"""
        try:
            # Try newer version first
            try:
                from langchain_community.llms import Together
            except ImportError:
                from langchain.llms import Together

            self._client = Together(
                model=self.model,
                together_api_key=self.api_key,
                temperature=0.7,
                max_tokens=2000,
            )
            logger.info(f"Initialized Together.ai provider with model: {self.model}")
        except ImportError as e:
            logger.error(f"Together not installed. Install with: pip install together langchain-community. Error: {e}")
            raise

    def chat(self, prompt: str, **kwargs) -> str:
        """Generate response using Together.ai"""
        if not self._client:
            raise RuntimeError("Together.ai client not initialized")

        try:
            response = self._client(prompt)
            return response
        except Exception as e:
            logger.error(f"Error calling Together.ai: {str(e)}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "together",
            "model": self.model,
            "type": "api",
            "cost": "free_tier",
        }


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider (kept for compatibility)"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self._client = None
        self._initialize()

    def _initialize(self):
        """Initialize OpenAI client"""
        try:
            # Try newer version first
            try:
                from langchain_openai import ChatOpenAI
            except ImportError:
                from langchain.chat_models import ChatOpenAI

            self._client = ChatOpenAI(
                openai_api_key=self.api_key,
                model_name=self.model,
                temperature=0.7,
            )
            logger.info(f"Initialized OpenAI provider with model: {self.model}")
        except ImportError as e:
            logger.error(f"OpenAI not installed. Install with: pip install openai langchain-openai. Error: {e}")
            raise

    def chat(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI"""
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")

        try:
            from langchain_core.messages import HumanMessage
            message = HumanMessage(content=prompt)
            response = self._client.invoke([message])
            return response.content
        except Exception as e:
            logger.error(f"Error calling OpenAI: {str(e)}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "openai",
            "model": self.model,
            "type": "api",
            "cost": "paid",
        }


class LLMProviderFactory:
    """Factory for creating LLM provider instances"""

    _providers = {
        "ollama": OllamaProvider,
        "groq": GroqProvider,
        "huggingface": HuggingFaceProvider,
        "together": TogetherProvider,
        "openai": OpenAIProvider,
    }

    @classmethod
    def create_provider(cls, provider_name: str, **kwargs) -> BaseLLMProvider:
        """
        Create an LLM provider instance

        Args:
            provider_name: Name of the provider (ollama, groq, huggingface, together, openai)
            **kwargs: Provider-specific configuration

        Returns:
            BaseLLMProvider instance
        """
        provider_name = provider_name.lower()

        if provider_name not in cls._providers:
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available: {', '.join(cls._providers.keys())}"
            )

        provider_class = cls._providers[provider_name]
        try:
            return provider_class(**kwargs)
        except Exception as e:
            logger.error(f"Failed to create {provider_name} provider: {str(e)}")
            raise

    @classmethod
    def get_available_providers(cls) -> Dict[str, str]:
        """Get list of available providers with descriptions"""
        return {
            "ollama": "Local, completely free and private",
            "groq": "Free API tier available, very fast",
            "huggingface": "Free inference API",
            "together": "Free tier available",
            "openai": "Paid API (kept for compatibility)",
        }

    @classmethod
    def create_from_config(cls, config) -> BaseLLMProvider:
        """
        Create provider from configuration object

        Args:
            config: Configuration object with provider settings

        Returns:
            BaseLLMProvider instance
        """
        provider = config.LLM_PROVIDER.lower()

        if provider == "ollama":
            return cls.create_provider(
                "ollama",
                base_url=config.OLLAMA_BASE_URL,
                model=config.OLLAMA_MODEL,
            )
        elif provider == "groq":
            if not config.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not configured")
            return cls.create_provider(
                "groq",
                api_key=config.GROQ_API_KEY,
                model=config.GROQ_MODEL,
            )
        elif provider == "huggingface":
            if not config.HUGGINGFACE_API_KEY:
                raise ValueError("HUGGINGFACE_API_KEY not configured")
            return cls.create_provider(
                "huggingface",
                api_key=config.HUGGINGFACE_API_KEY,
                model=config.HUGGINGFACE_MODEL,
            )
        elif provider == "together":
            if not config.TOGETHER_API_KEY:
                raise ValueError("TOGETHER_API_KEY not configured")
            return cls.create_provider(
                "together",
                api_key=config.TOGETHER_API_KEY,
                model=config.TOGETHER_MODEL,
            )
        elif provider == "openai":
            if not config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            return cls.create_provider(
                "openai",
                api_key=config.OPENAI_API_KEY,
                model=config.OPENAI_MODEL,
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
