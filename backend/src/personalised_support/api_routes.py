"""
FastAPI routes for personalized support chatbot.
"""

import sys
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

try:
    from .schemas import (
        ChatRequest, ChatResponse, ConversationHistory,
        PeerSupportRequest, ChatMessage,
    )
    from . import (
        chat_manager, conversation_storage, peer_storage,
        analytics, knowledge_base,
    )
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from personalised_support.schemas import (
        ChatRequest, ChatResponse, ConversationHistory,
        PeerSupportRequest, ChatMessage,
    )
    from personalised_support import (
        chat_manager, conversation_storage, peer_storage,
        analytics, knowledge_base,
    )

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/support", tags=["personalized-support"])


# ──────────────────────────────────────────────────────────────────────────────
# Chat
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """Send a message to the personalised support chatbot."""
    try:
        analytics.log_event(
            "chat_message_received",
            user_id=request.user_id,
            metadata={"support_type": request.support_type},
        )

        response = await chat_manager.process_message(request)
        if not response:
            raise HTTPException(status_code=500, detail="Failed to generate response")

        # Persist to storage layer
        conversation_storage.save_message(
            user_id=request.user_id,
            role="user",
            content=request.message,
            message_type="user_input",
        )
        conversation_storage.save_message(
            user_id=request.user_id,
            role="assistant",
            content=response.message,
            message_type=response.message_type,
        )

        analytics.log_event(
            "chat_response_generated",
            user_id=request.user_id,
            metadata={"message_type": response.message_type},
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/history/{user_id}", response_model=ConversationHistory)
async def get_chat_history(
    user_id: str,
    limit: Optional[int] = Query(50, ge=1, le=500),
):
    """Get conversation history for a user."""
    try:
        messages = conversation_storage.get_conversation(user_id, limit=limit)

        chat_messages = [
            ChatMessage(
                role=msg["role"],
                content=msg["content"],
                message_type=msg.get("message_type"),
            )
            for msg in messages
        ]

        meta = conversation_storage.get_metadata(user_id) or {}
        now = datetime.now()

        return ConversationHistory(
            user_id=user_id,
            messages=chat_messages,
            created_at=meta.get("created_at") or now,
            updated_at=meta.get("updated_at") or now,
            context_data=meta.get("context_data"),
        )

    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/history/{user_id}")
async def clear_chat_history(user_id: str):
    """Clear conversation history for a user."""
    try:
        chat_manager.clear_conversation(user_id)
        conversation_storage.clear_conversation(user_id)
        analytics.log_event("conversation_cleared", user_id=user_id)
        return {"success": True, "message": "Conversation cleared"}
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# User context (expense data injection)
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/chat/context/{user_id}")
async def update_user_context(user_id: str, context: Dict[str, Any]):
    """
    Push the user's financial context into the chatbot so subsequent replies
    are personalised with real expense numbers.

    Expected fields (all optional):
    - current_month_total (float)
    - previous_month_total (float)
    - budget (float)
    - budget_status (str)
    - category_spending (dict[str, float])
    - biggest_category (str)
    - trend (str)
    """
    try:
        chat_manager.ai_chatbot.set_user_context(user_id, context)
        conversation_storage.save_metadata(
            user_id, {"context_data": context}
        )
        return {"success": True, "user_id": user_id, "context_keys": list(context.keys())}
    except Exception as e:
        logger.error(f"Error updating user context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Analysis & recommendations
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/analysis/{user_id}")
async def analyze_user_needs(user_id: str):
    """Analyse a user's support needs based on conversation history."""
    try:
        analysis = await chat_manager.analyze_user_needs(user_id)
        return {
            "user_id": user_id,
            "identified_issues": analysis.identified_issues,
            "recommended_support_type": analysis.recommended_support_type,
            "urgency_level": analysis.urgency_level,
            "confidence_score": analysis.confidence_score,
            "reasoning": analysis.reasoning,
        }
    except Exception as e:
        logger.error(f"Error in analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/{user_id}")
async def get_recommendations(
    user_id: str,
    context: Optional[Dict[str, Any]] = None,
):
    """Get personalised financial recommendations."""
    try:
        return await chat_manager.get_personalized_recommendations(
            user_id=user_id,
            context_data=context,
        )
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Knowledge base
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/knowledge/search")
async def search_knowledge_base(query: str = Query(..., min_length=1)):
    """Search the rule-based knowledge base."""
    try:
        results = chat_manager.search_knowledge_base(query)
        return {"query": query, "results": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/categories")
async def get_support_categories():
    """Get available support categories."""
    try:
        categories = chat_manager.get_rule_categories()
        return {"categories": categories, "count": len(categories)}
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Peer support
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/peer/connect")
async def connect_with_peer(request: PeerSupportRequest):
    """Connect a user with a peer supporter."""
    try:
        analytics.log_event(
            "peer_connection_requested",
            user_id=request.user_id,
            metadata={"category": request.issue_category},
        )

        connection = chat_manager.create_peer_connection(
            user_id=request.user_id,
            issue_category=request.issue_category,
        )
        if not connection:
            raise HTTPException(status_code=404, detail="No peers available")

        return connection
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting with peer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/peer/available")
async def get_available_peers(category: Optional[str] = None):
    """List available peer supporters, optionally filtered by category."""
    try:
        health = chat_manager.peer_support.get_system_health()
        peers = [
            {
                "peer_id": peer_id,
                "expertise_areas": peer.expertise_areas,
                "reputation_score": peer.reputation_score,
                "total_helpings": peer.total_helpings,
                "languages": peer.languages,
            }
            for peer_id, peer in chat_manager.peer_support.peers.items()
            if peer.availability and (not category or category in peer.expertise_areas)
        ]
        return {"peers": peers, "count": len(peers), "system_health": health}
    except Exception as e:
        logger.error(f"Error getting peers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class PeerRegisterRequest(BaseModel):
    peer_id: str
    expertise_areas: List[str]
    languages: Optional[List[str]] = None


@router.post("/peer/register")
async def register_peer(request: PeerRegisterRequest):
    """Register a new peer supporter."""
    try:
        result = chat_manager.register_peer(
            peer_id=request.peer_id,
            expertise_areas=request.expertise_areas,
            languages=request.languages,
        )
        analytics.log_event("peer_registered", metadata={"peer_id": request.peer_id})
        return {"success": True, "peer": result}
    except Exception as e:
        logger.error(f"Error registering peer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/peer/{peer_id}/profile")
async def get_peer_profile(peer_id: str):
    """Get a peer supporter's profile and stats."""
    try:
        stats = chat_manager.peer_support.get_connection_stats(peer_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Peer not found")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting peer profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/peer/leaderboard")
async def get_peer_leaderboard(limit: int = Query(10, ge=1, le=100)):
    """Get the peer supporter leaderboard."""
    try:
        leaderboard = chat_manager.peer_support.get_peer_leaderboard(limit)
        return {"leaderboard": leaderboard, "count": len(leaderboard)}
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# System info
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/types")
async def get_support_types():
    """Describe the available support modes."""
    try:
        types = chat_manager.get_available_support_types()
        return {
            "support_types": types,
            "descriptions": {
                "ai": "AI-powered financial advice using Groq LLM",
                "rule_based": "Predefined answers to common financial questions",
                "peer": "Connect with experienced peer supporters",
                "auto": "Automatic selection of the best support type",
            },
        }
    except Exception as e:
        logger.error(f"Error getting support types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_system_status():
    """Get system statistics."""
    try:
        stats = chat_manager.get_system_stats()
        return {"status": "operational", "timestamp": datetime.now().isoformat(), "stats": stats}
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for the support system."""
    try:
        import os
        groq_key = os.getenv("GROQ_API_KEY")
        return {
            "status": "operational",
            "systems": {
                "ai_chatbot": "operational" if chat_manager.ai_chatbot.llm else "limited (no LLM key)",
                "rule_based": "operational",
                "peer_support": "operational",
                "storage": "operational",
            },
            "debug": {
                "GROQ_API_KEY_len": len(groq_key) if groq_key else 0,
                "GROQ_API_KEY_prefix": groq_key[:8] if groq_key else None,
                "LLM_PROVIDER": os.getenv("LLM_PROVIDER"),
                "SupportConfig_PROVIDER": chat_manager.ai_chatbot.provider.get_model_info() if chat_manager.ai_chatbot.provider else None
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "degraded", "error": str(e)}
