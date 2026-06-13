"""
AI chatbot for personalized financial support using Groq (free LLM).

Maintains per-user conversation history and injects the user's financial
context (expense data from Firebase) into every system prompt so the LLM
can give genuinely personalised advice.
"""

import json
import logging
import sys
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

# Support both "python -m" / imported-as-package (relative) and
# "python langchain_chatbot.py" run-directly (absolute) styles.
try:
    from .config import SupportConfig
    from .llm_provider import LLMProviderFactory, BaseLLMProvider
    from .prompts import (
        build_system_prompt,
        SPENDING_ANALYSIS_TEMPLATE,
        GOAL_SETTING_TEMPLATE,
        CONTEXTUAL_ADVICE_TEMPLATE,
        CRISIS_SUPPORT_TEMPLATE,
    )
    from .schemas import ChatMessage, ChatResponse, SupportAnalysis
except ImportError:
    # Running as a standalone script — add the package root to sys.path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from personalised_support.config import SupportConfig
    from personalised_support.llm_provider import LLMProviderFactory, BaseLLMProvider
    from personalised_support.prompts import (
        build_system_prompt,
        SPENDING_ANALYSIS_TEMPLATE,
        GOAL_SETTING_TEMPLATE,
        CONTEXTUAL_ADVICE_TEMPLATE,
        CRISIS_SUPPORT_TEMPLATE,
    )
    from personalised_support.schemas import ChatMessage, ChatResponse, SupportAnalysis

logger = logging.getLogger(__name__)

# How many recent messages to include in the conversation window sent to Groq
CONVERSATION_WINDOW = 10


class LangChainChatBot:
    """
    Groq-backed chatbot that keeps per-user conversation history and injects
    the user's real expense data into every request.
    """

    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        if provider:
            self.provider = provider
        else:
            try:
                self.provider = LLMProviderFactory.create_from_config(SupportConfig)
                logger.info(f"Chatbot initialised with {SupportConfig.LLM_PROVIDER} provider")
            except Exception as e:
                logger.warning(f"Failed to initialise LLM provider: {e}")
                self.provider = None

        # per-user memory: { user_id: { "messages": [...], "user_context": {...} } }
        self._memory: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def llm(self):
        """Compatibility shim: return provider so callers can check truthiness."""
        return self.provider

    def set_user_context(self, user_id: str, context: Dict[str, Any]) -> None:
        """
        Store the user's financial context so it can be embedded in every prompt.

        Args:
            user_id: Firebase / app user id
            context: dict with expense summary keys (see prompts.build_system_prompt)
        """
        mem = self._get_memory(user_id)
        mem["user_context"] = context
        logger.info(f"Updated financial context for user {user_id}")

    async def chat(
        self,
        user_id: str,
        message: str,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """
        Process a user message and return an AI response.

        Args:
            user_id: user identifier
            message: the user's chat message
            context_data: optional one-off context to merge into the user profile
        """
        if not self.provider:
            return ChatResponse(
                user_id=user_id,
                message=(
                    "Chatbot service is currently unavailable. "
                    "Please set LLM_PROVIDER=groq and GROQ_API_KEY in your .env file."
                ),
                message_type="error",
                timestamp=datetime.now(),
            )

        mem = self._get_memory(user_id)

        # Merge any one-off context coming from the request
        if context_data:
            existing = mem.get("user_context", {})
            mem["user_context"] = {**existing, **context_data}

        # Build the message list for the LLM
        system_prompt = build_system_prompt(mem.get("user_context"))
        messages = self._build_messages(user_id, system_prompt, message)

        try:
            response_text = self.provider.chat_with_history(messages)
        except AttributeError:
            # Fallback for providers that only implement the simple `chat` method
            full_prompt = self._messages_to_plain_text(messages)
            response_text = self.provider.chat(full_prompt)
        except Exception as e:
            logger.error(f"LLM error for user {user_id}: {e}")
            return ChatResponse(
                user_id=user_id,
                message=f"I encountered an error: {e}. Please try again.",
                message_type="error",
                timestamp=datetime.now(),
            )

        # Persist both turns in memory
        mem["messages"].append({"role": "user", "content": message})
        mem["messages"].append({"role": "assistant", "content": response_text})

        return ChatResponse(
            user_id=user_id,
            message=response_text.strip() if response_text else "No response generated.",
            message_type="ai",
            confidence=0.85,
            timestamp=datetime.now(),
        )

    async def analyze_spending(
        self,
        user_id: str,
        current_total: float,
        previous_total: float,
        categories: Dict[str, float],
        budget_status: str,
        trend: str,
    ) -> str:
        if not self.provider:
            return "Analysis service unavailable."

        prompt = SPENDING_ANALYSIS_TEMPLATE.format(
            user_id=user_id,
            current_total=f"{current_total:,.2f}",
            previous_total=f"{previous_total:,.2f}",
            categories=json.dumps(categories, indent=2),
            budget_status=budget_status,
            trend=trend,
        )
        try:
            return (self.provider.chat(prompt) or "").strip()
        except Exception as e:
            logger.error(f"Error in spending analysis: {e}")
            return "Unable to analyse spending at this moment."

    async def suggest_goals(
        self,
        user_id: str,
        monthly_income: float,
        current_spending: float,
        budget: float,
        goal_description: str,
    ) -> str:
        if not self.provider:
            return "Goal setting service unavailable."

        prompt = GOAL_SETTING_TEMPLATE.format(
            monthly_income=f"{monthly_income:,.2f}",
            current_spending=f"{current_spending:,.2f}",
            budget=f"{budget:,.2f}",
            goal_description=goal_description,
        )
        try:
            return (self.provider.chat(prompt) or "").strip()
        except Exception as e:
            logger.error(f"Error in goal suggestion: {e}")
            return "Unable to generate goals at this moment."

    async def get_contextual_advice(
        self,
        user_id: str,
        spending_pattern: str,
        budget: float,
        biggest_expense: str,
        trend: str,
        user_input: str,
    ) -> str:
        if not self.provider:
            return "Advice service unavailable."

        prompt = CONTEXTUAL_ADVICE_TEMPLATE.format(
            spending_pattern=spending_pattern,
            budget=f"{budget:,.2f}",
            biggest_expense=biggest_expense,
            trend=trend,
            user_input=user_input,
        )
        try:
            return (self.provider.chat(prompt) or "").strip()
        except Exception as e:
            logger.error(f"Error in contextual advice: {e}")
            return "Unable to provide advice at this moment."

    async def handle_crisis_support(
        self,
        user_id: str,
        situation: str,
        emotional_state: str,
    ) -> str:
        if not self.provider:
            return "Support service unavailable."

        prompt = CRISIS_SUPPORT_TEMPLATE.format(
            situation=situation,
            emotional_state=emotional_state,
        )
        try:
            return (self.provider.chat(prompt) or "").strip()
        except Exception as e:
            logger.error(f"Error in crisis support: {e}")
            return "I'm here to help. Please reach out to a financial counselor."

    async def analyze_conversation_context(
        self,
        conversation_history: List[ChatMessage],
        latest_message: str,
    ) -> SupportAnalysis:
        if not self.provider:
            return self._default_support_analysis()

        history_str = "\n".join(f"{m.role}: {m.content}" for m in conversation_history)
        prompt = (
            f"Analyse this financial support conversation and respond ONLY with valid JSON.\n\n"
            f"Conversation:\n{history_str}\n\n"
            f"Latest message: {latest_message}\n\n"
            f"JSON keys required: issues (list of strings), support_type "
            f"(one of: ai, rule_based, peer), urgency (one of: low, medium, high), "
            f"confidence (float 0-1), reasoning (string)."
        )
        try:
            raw = self.provider.chat(prompt) or ""
            # Strip markdown fences if the model wraps in ```json ... ```
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            data = json.loads(raw)
            return SupportAnalysis(
                user_id="unknown",
                identified_issues=data.get("issues", []),
                recommended_support_type=data.get("support_type", "ai"),
                urgency_level=data.get("urgency", "medium"),
                confidence_score=float(data.get("confidence", 0.75)),
                reasoning=data.get("reasoning", ""),
            )
        except (json.JSONDecodeError, TypeError, Exception) as e:
            logger.warning(f"Failed to parse context analysis JSON: {e}")
            return self._default_support_analysis()

    def clear_memory(self, user_id: str) -> None:
        """Clear conversation history and stored context for a user."""
        self._memory.pop(user_id, None)
        logger.info(f"Cleared memory for user {user_id}")

    def get_conversation_history(self, user_id: str) -> List[Dict[str, str]]:
        """Return the raw message list for a user."""
        return self._get_memory(user_id).get("messages", [])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_memory(self, user_id: str) -> Dict[str, Any]:
        if user_id not in self._memory:
            self._memory[user_id] = {"messages": [], "user_context": {}}
        return self._memory[user_id]

    def _build_messages(
        self,
        user_id: str,
        system_prompt: str,
        new_message: str,
    ) -> List[Dict[str, str]]:
        """
        Build the messages list: system prompt + recent history + new user turn.
        """
        mem = self._get_memory(user_id)
        history = mem.get("messages", [])[-CONVERSATION_WINDOW:]

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": new_message})
        return messages

    @staticmethod
    def _messages_to_plain_text(messages: List[Dict[str, str]]) -> str:
        """Flatten a messages list into a plain text prompt (fallback)."""
        parts = []
        for m in messages:
            role = m["role"].capitalize()
            parts.append(f"{role}: {m['content']}")
        return "\n\n".join(parts)

    @staticmethod
    def _default_support_analysis() -> SupportAnalysis:
        return SupportAnalysis(
            user_id="unknown",
            identified_issues=["General financial question"],
            recommended_support_type="ai",
            urgency_level="medium",
            confidence_score=0.5,
            reasoning="Unable to perform detailed analysis.",
        )
