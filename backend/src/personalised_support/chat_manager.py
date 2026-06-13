"""
Unified chat manager — orchestrates AI, rule-based, and peer support.

Key addition: before sending any AI request the manager loads the user's
expense summary from Firebase and injects it into the chatbot's system
prompt so every reply is grounded in the user's real financial situation.
"""

import logging
import sys
import os
from typing import Optional, List, Dict, Any
from enum import Enum

try:
    from .schemas import ChatRequest, ChatResponse, ChatMessage, SupportAnalysis
    from .langchain_chatbot import LangChainChatBot
    from .rule_based_support import RuleBasedSupport
    from .peer_support import PeerSupportSystem
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from personalised_support.schemas import ChatRequest, ChatResponse, ChatMessage, SupportAnalysis
    from personalised_support.langchain_chatbot import LangChainChatBot
    from personalised_support.rule_based_support import RuleBasedSupport
    from personalised_support.peer_support import PeerSupportSystem

logger = logging.getLogger(__name__)


class SupportType(Enum):
    AI = "ai"
    RULE_BASED = "rule_based"
    PEER = "peer"
    AUTO = "auto"


class ChatManager:
    """Unified manager for all support types."""

    def __init__(self):
        self.ai_chatbot = LangChainChatBot()
        self.rule_based = RuleBasedSupport()
        self.peer_support = PeerSupportSystem()
        # In-memory conversation mirror (schema-level objects for API responses)
        self.conversation_history: Dict[str, List[ChatMessage]] = {}

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a user message and return the best response."""
        user_id = request.user_id

        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        # Record the incoming message
        self.conversation_history[user_id].append(
            ChatMessage(role="user", content=request.message, message_type="user_input")
        )

        # Refresh the user's financial context before every AI turn
        await self._refresh_user_context(user_id)

        support_type = request.support_type or "auto"
        if support_type == "auto":
            support_type = await self._determine_support_type(
                request.message, self.conversation_history[user_id]
            )

        response: Optional[ChatResponse] = None
        if support_type == "rule_based":
            response = await self._process_rule_based(request)
            if response is None:
                # Rule-based had no match — fall through to AI
                response = await self._process_ai(request)
        elif support_type == "peer":
            response = await self._process_peer_support(request)
        else:
            response = await self._process_ai(request)

        if response:
            self.conversation_history[user_id].append(
                ChatMessage(
                    role="assistant",
                    content=response.message,
                    message_type=response.message_type,
                )
            )

        return response or self._error_response(user_id)

    # ------------------------------------------------------------------
    # User context loading
    # ------------------------------------------------------------------

    async def _refresh_user_context(self, user_id: str) -> None:
        """
        Fetch the latest expense data from Firebase and push it into the
        chatbot's system prompt for this user.

        Fails silently — if Firebase is unavailable the chatbot still works,
        just without personalised numbers.
        """
        try:
            context = self._load_expense_context(user_id)
            if context:
                self.ai_chatbot.set_user_context(user_id, context)
        except Exception as e:
            logger.warning(f"Could not load expense context for {user_id}: {e}")

    @staticmethod
    def _load_expense_context(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Pull current-month, previous-month and budget data from Firebase and
        return a flat dict ready for the system prompt.
        """
        try:
            import firebase_admin
            from firebase_admin import db as firebase_db

            if not firebase_admin._apps:
                return None

            # Budget plan
            budget_ref = firebase_db.reference(f"users/{user_id}/budget_plan")
            budget_data = budget_ref.get()

            # Current month expenses
            from datetime import datetime
            today = datetime.now()
            first_day = today.replace(day=1)

            expenses_ref = firebase_db.reference(f"users/{user_id}/expenses")
            all_expenses = expenses_ref.get() or {}

            current_expenses = {
                k: v for k, v in all_expenses.items()
                if _parse_date(v.get("date", "")) >= first_day
            }

            # Previous month
            from datetime import timedelta
            last_day_prev = first_day - timedelta(days=1)
            first_day_prev = last_day_prev.replace(day=1)

            prev_expenses = {
                k: v for k, v in all_expenses.items()
                if first_day_prev <= _parse_date(v.get("date", "")) <= last_day_prev
            }

            current_total = sum(
                float(v.get("amount", 0)) for v in current_expenses.values()
            )
            prev_total = sum(
                float(v.get("amount", 0)) for v in prev_expenses.values()
            )

            # Category breakdown (current month)
            category_spending: Dict[str, float] = {}
            for v in current_expenses.values():
                cat = v.get("category", "other")
                category_spending[cat] = (
                    category_spending.get(cat, 0.0) + float(v.get("amount", 0))
                )

            biggest_category = (
                max(category_spending, key=lambda c: category_spending[c])
                if category_spending
                else None
            )

            # Trend
            if prev_total > 0:
                change_pct = (current_total - prev_total) / prev_total * 100
                if change_pct > 10:
                    trend = f"increasing ({change_pct:+.1f}% vs last month)"
                elif change_pct < -10:
                    trend = f"decreasing ({change_pct:+.1f}% vs last month)"
                else:
                    trend = f"stable ({change_pct:+.1f}% vs last month)"
            else:
                trend = "not enough history"

            # Budget status
            budget = None
            budget_status = "no budget set"
            if budget_data and isinstance(budget_data, dict):
                plan = budget_data.get("plan", budget_data)
                budget = float(plan.get("total_budget", 0) or 0)
                if budget > 0:
                    pct = current_total / budget * 100
                    if pct >= 100:
                        budget_status = f"over budget ({pct:.0f}% used)"
                    elif pct >= 80:
                        budget_status = f"near limit ({pct:.0f}% used)"
                    else:
                        budget_status = f"within budget ({pct:.0f}% used)"

            return {
                "current_month_total": current_total,
                "previous_month_total": prev_total,
                "budget": budget,
                "budget_status": budget_status,
                "category_spending": category_spending,
                "biggest_category": biggest_category,
                "trend": trend,
            }

        except Exception as e:
            logger.debug(f"_load_expense_context failed: {e}")
            return None

    # ------------------------------------------------------------------
    # Support routing
    # ------------------------------------------------------------------

    async def _determine_support_type(
        self,
        message: str,
        conversation: List[ChatMessage],
    ) -> str:
        rule_response = self.rule_based.process_query(message)
        if rule_response:
            return "rule_based"
        return "ai"

    async def _process_rule_based(self, request: ChatRequest) -> Optional[ChatResponse]:
        try:
            rule_response = self.rule_based.process_query(request.message)
            if not rule_response:
                return None
            return ChatResponse(
                user_id=request.user_id,
                message=rule_response.response,
                message_type="rule_based",
                suggested_actions=rule_response.suggested_next_steps,
                metadata={
                    "matched_rule": rule_response.matched_rule,
                    "category": rule_response.category,
                },
            )
        except Exception as e:
            logger.error(f"Rule-based processing error: {e}")
            return None

    async def _process_ai(self, request: ChatRequest) -> Optional[ChatResponse]:
        try:
            context_data = self._extract_extra_context(request)
            response = await self.ai_chatbot.chat(
                user_id=request.user_id,
                message=request.message,
                context_data=context_data if context_data else None,
            )
            return response
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return None

    async def _process_peer_support(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            user_id=request.user_id,
            message=(
                "Connecting you with a financial peer supporter. "
                "They'll be with you shortly!"
            ),
            message_type="peer",
            metadata={"status": "connecting"},
        )

    # ------------------------------------------------------------------
    # Conversation management
    # ------------------------------------------------------------------

    def get_conversation_history(self, user_id: str) -> List[ChatMessage]:
        return self.conversation_history.get(user_id, [])

    def clear_conversation(self, user_id: str) -> None:
        self.conversation_history.pop(user_id, None)
        self.ai_chatbot.clear_memory(user_id)
        logger.info(f"Cleared conversation for user {user_id}")

    # ------------------------------------------------------------------
    # Analysis & recommendations
    # ------------------------------------------------------------------

    async def analyze_user_needs(
        self,
        user_id: str,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> SupportAnalysis:
        history = self.conversation_history.get(user_id, [])
        if not history:
            return SupportAnalysis(
                user_id=user_id,
                identified_issues=["New user — no conversation history yet"],
                recommended_support_type="ai",
                urgency_level="medium",
                confidence_score=0.5,
                reasoning="Insufficient conversation history for detailed analysis.",
            )

        analysis = await self.ai_chatbot.analyze_conversation_context(
            history, history[-1].content
        )
        analysis.user_id = user_id
        return analysis

    async def get_personalized_recommendations(
        self,
        user_id: str,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # Always try to load live context first
        live_context = self._load_expense_context(user_id) or {}
        merged = {**live_context, **(context_data or {})}

        analysis = await self.analyze_user_needs(user_id, merged)
        recommendations = []

        if merged.get("biggest_category") or merged.get("trend"):
            advice = await self.ai_chatbot.get_contextual_advice(
                user_id=user_id,
                spending_pattern=merged.get("trend", "moderate"),
                budget=merged.get("budget") or 0,
                biggest_expense=merged.get("biggest_category", "unknown"),
                trend=merged.get("trend", "stable"),
                user_input="What should I focus on to improve my finances?",
            )
            recommendations.append({"type": "personalized", "content": advice})

        rule_hits = self.rule_based.search_knowledge_base(
            merged.get("biggest_category", "finances")
        )
        if rule_hits:
            recommendations.append({
                "type": "rule_based",
                "content": rule_hits[0].get("responses", [""])[0],
            })

        return {
            "user_id": user_id,
            "analysis": {
                "identified_issues": analysis.identified_issues,
                "urgency_level": analysis.urgency_level,
                "recommended_support_type": analysis.recommended_support_type,
            },
            "recommendations": recommendations,
            "expense_context": {
                "current_month_total": merged.get("current_month_total"),
                "budget": merged.get("budget"),
                "budget_status": merged.get("budget_status"),
                "trend": merged.get("trend"),
            },
        }

    # ------------------------------------------------------------------
    # Peer support helpers
    # ------------------------------------------------------------------

    def create_peer_connection(
        self,
        user_id: str,
        issue_category: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            from .schemas import PeerSupportRequest
            req = PeerSupportRequest(
                user_id=user_id,
                issue_category=issue_category,
                description="",
            )
            matching = self.peer_support.find_matching_peers(req)
            if not matching:
                return {
                    "status": "no_peers_available",
                    "message": "No peer supporters available for this category.",
                }
            peer = matching[0]
            connection = self.peer_support.create_connection(
                user_id=user_id,
                peer_id=peer.peer_id,
                issue_category=issue_category,
            )
            return {
                "status": "connected",
                "connection_id": connection.connection_id,
                "peer_id": peer.peer_id,
                "peer_reputation": peer.reputation_score,
                "peer_expertise": peer.expertise_areas,
            }
        except Exception as e:
            logger.error(f"Error creating peer connection: {e}")
            return None

    def register_peer(
        self,
        peer_id: str,
        expertise_areas: List[str],
        languages: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        peer = self.peer_support.register_peer(peer_id, expertise_areas, languages)
        return {
            "peer_id": peer.peer_id,
            "expertise_areas": peer.expertise_areas,
            "reputation_score": peer.reputation_score,
            "languages": peer.languages,
        }

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def get_available_support_types(self) -> List[str]:
        return [t.value for t in SupportType]

    def get_rule_categories(self) -> List[str]:
        return self.rule_based.get_all_categories()

    def search_knowledge_base(self, query: str) -> List[Dict[str, str]]:
        return self.rule_based.search_knowledge_base(query)

    def get_system_stats(self) -> Dict[str, Any]:
        return {
            "total_users_with_history": len(self.conversation_history),
            "peer_system_health": self.peer_support.get_system_health(),
            "rule_categories": len(self.rule_based.get_all_categories()),
            "ai_chatbot_status": (
                "operational" if self.ai_chatbot.llm else "limited"
            ),
        }

    @staticmethod
    def _extract_extra_context(request: ChatRequest) -> Dict[str, Any]:
        """Pull any extra context fields that arrived with the request."""
        return {}

    @staticmethod
    def _error_response(user_id: str) -> ChatResponse:
        return ChatResponse(
            user_id=user_id,
            message="I encountered an error processing your request. Please try again.",
            message_type="error",
        )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _parse_date(date_str: str):
    """Parse an ISO date string, returning epoch-zero on failure."""
    from datetime import datetime
    try:
        return datetime.fromisoformat(date_str)
    except Exception:
        return datetime.min
