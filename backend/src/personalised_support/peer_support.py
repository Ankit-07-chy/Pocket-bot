"""
Peer support system for connecting users with experienced peers
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from .schemas import (
    PeerProfile, PeerSupportConnection, PeerSupportRequest, ChatMessage
)

logger = logging.getLogger(__name__)


class PeerSupportSystem:
    """System for peer-to-peer financial support"""

    def __init__(self):
        """Initialize peer support system"""
        self.peers: Dict[str, PeerProfile] = {}
        self.connections: Dict[str, PeerSupportConnection] = {}
        self.conversations: Dict[str, List[ChatMessage]] = {}
        self.reputation_scores: Dict[str, float] = {}

    def register_peer(
        self,
        peer_id: str,
        expertise_areas: List[str],
        languages: Optional[List[str]] = None
    ) -> PeerProfile:
        """Register a peer as support provider"""
        peer = PeerProfile(
            peer_id=peer_id,
            expertise_areas=expertise_areas,
            reputation_score=5.0,
            total_helpings=0,
            availability=True,
            languages=languages or ["en"]
        )
        self.peers[peer_id] = peer
        self.reputation_scores[peer_id] = 5.0
        logger.info(f"Registered peer: {peer_id}")
        return peer

    def find_matching_peers(
        self,
        request: PeerSupportRequest,
        limit: int = 3
    ) -> List[PeerProfile]:
        """Find peers matching user's issue and preferences"""
        matching_peers = []

        for peer in self.peers.values():
            # Check availability
            if not peer.availability:
                continue

            # Check expertise match
            if request.issue_category.lower() not in [
                cat.lower() for cat in peer.expertise_areas
            ]:
                continue

            # Check language match
            if request.preferred_language not in peer.languages:
                continue

            matching_peers.append(peer)

        # Sort by reputation and total helpings
        matching_peers.sort(
            key=lambda p: (p.reputation_score, p.total_helpings),
            reverse=True
        )

        return matching_peers[:limit]

    def create_connection(
        self,
        user_id: str,
        peer_id: str,
        issue_category: str,
        request: Optional[PeerSupportRequest] = None
    ) -> PeerSupportConnection:
        """Create a peer support connection"""
        if peer_id not in self.peers:
            raise ValueError(f"Peer {peer_id} not found")

        connection_id = f"conn_{uuid.uuid4().hex[:12]}"
        connection = PeerSupportConnection(
            connection_id=connection_id,
            user_id=user_id,
            peer_id=peer_id,
            issue_category=issue_category,
            status="active",
            created_at=datetime.now()
        )

        self.connections[connection_id] = connection
        self.conversations[connection_id] = []

        logger.info(f"Created peer connection: {connection_id}")
        return connection

    def send_message(
        self,
        connection_id: str,
        sender_id: str,
        message: str
    ) -> ChatMessage:
        """Send message in peer support conversation"""
        if connection_id not in self.connections:
            raise ValueError(f"Connection {connection_id} not found")

        connection = self.connections[connection_id]

        # Verify sender is part of connection
        if sender_id not in [connection.user_id, connection.peer_id]:
            raise ValueError(f"Sender {sender_id} not part of this connection")

        # Determine role
        role = "peer" if sender_id == connection.peer_id else "user"

        # Create message
        chat_msg = ChatMessage(
            role=role,
            content=message,
            timestamp=datetime.now(),
            message_type="peer_support"
        )

        if connection_id not in self.conversations:
            self.conversations[connection_id] = []

        self.conversations[connection_id].append(chat_msg)
        logger.info(f"Message added to connection {connection_id}")
        return chat_msg

    def get_conversation(self, connection_id: str) -> List[ChatMessage]:
        """Get conversation history for a connection"""
        return self.conversations.get(connection_id, [])

    def close_connection(
        self,
        connection_id: str,
        rating: Optional[float] = None,
        feedback: Optional[str] = None
    ) -> None:
        """Close a peer support connection"""
        if connection_id not in self.connections:
            raise ValueError(f"Connection {connection_id} not found")

        connection = self.connections[connection_id]
        connection.status = "closed"
        connection.closed_at = datetime.now()
        connection.rating = rating

        # Update peer reputation
        if rating and connection.peer_id in self.peers:
            self._update_peer_reputation(connection.peer_id, rating, feedback)

        logger.info(f"Closed connection {connection_id} with rating {rating}")

    def _update_peer_reputation(
        self,
        peer_id: str,
        rating: float,
        feedback: Optional[str] = None
    ) -> None:
        """Update peer reputation based on user rating"""
        peer = self.peers.get(peer_id)
        if not peer:
            return

        # Weighted average of existing score and new rating
        new_score = (
            (peer.reputation_score * peer.total_helpings + rating) /
            (peer.total_helpings + 1)
        )

        peer.reputation_score = round(new_score, 2)
        peer.total_helpings += 1
        self.reputation_scores[peer_id] = peer.reputation_score

        logger.info(f"Updated peer {peer_id} reputation to {new_score}")

    def get_peer_profile(self, peer_id: str) -> Optional[PeerProfile]:
        """Get peer profile"""
        return self.peers.get(peer_id)

    def update_peer_availability(self, peer_id: str, available: bool) -> None:
        """Update peer availability"""
        if peer_id in self.peers:
            self.peers[peer_id].availability = available
            logger.info(f"Updated peer {peer_id} availability to {available}")

    def get_active_connections(self, user_id: str) -> List[PeerSupportConnection]:
        """Get active peer support connections for a user"""
        return [
            conn for conn in self.connections.values()
            if conn.user_id == user_id and conn.status == "active"
        ]

    def get_peer_connections(self, peer_id: str) -> List[PeerSupportConnection]:
        """Get connections for a peer"""
        return [
            conn for conn in self.connections.values()
            if conn.peer_id == peer_id
        ]

    def get_connection_stats(self, peer_id: str) -> Dict[str, Any]:
        """Get statistics for a peer"""
        peer = self.peers.get(peer_id)
        if not peer:
            return {}

        connections = self.get_peer_connections(peer_id)
        completed = [c for c in connections if c.status == "closed"]
        ratings = [c.rating for c in completed if c.rating]

        return {
            "peer_id": peer_id,
            "reputation_score": peer.reputation_score,
            "total_helpings": peer.total_helpings,
            "average_rating": sum(ratings) / len(ratings) if ratings else 0,
            "active_connections": len([c for c in connections if c.status == "active"]),
            "closed_connections": len(completed),
            "expertise_areas": peer.expertise_areas,
            "languages": peer.languages
        }

    def transfer_to_ai(
        self,
        connection_id: str,
        reason: str = "Peer unavailable"
    ) -> None:
        """Transfer peer support connection to AI chatbot"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            connection.status = "transferred"
            connection.closed_at = datetime.now()
            logger.info(f"Transferred connection {connection_id} to AI: {reason}")

    def get_peer_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard of top peers by reputation"""
        peer_stats = [
            {
                "peer_id": peer_id,
                "reputation_score": peer.reputation_score,
                "total_helpings": peer.total_helpings,
                "expertise_areas": peer.expertise_areas
            }
            for peer_id, peer in self.peers.items()
        ]

        return sorted(
            peer_stats,
            key=lambda x: (x["reputation_score"], x["total_helpings"]),
            reverse=True
        )[:limit]

    def get_expertise_coverage(self) -> Dict[str, int]:
        """Get coverage of expertise areas across all peers"""
        coverage = {}
        for peer in self.peers.values():
            for area in peer.expertise_areas:
                coverage[area] = coverage.get(area, 0) + 1
        return coverage

    def find_gap_expertise(self) -> List[str]:
        """Find areas with no peer coverage"""
        common_areas = [
            "budget_planning",
            "spending_reduction",
            "savings_goals",
            "debt_management",
            "investment_basics",
            "emergency_fund"
        ]

        coverage = self.get_expertise_coverage()
        gaps = [area for area in common_areas if area not in coverage]
        return gaps

    def cleanup_stale_connections(self, days: int = 30) -> int:
        """Clean up old closed connections"""
        cutoff = datetime.now() - timedelta(days=days)
        stale_connections = [
            conn_id for conn_id, conn in self.connections.items()
            if conn.status == "closed" and conn.closed_at < cutoff
        ]

        for conn_id in stale_connections:
            if conn_id in self.conversations:
                del self.conversations[conn_id]

        logger.info(f"Cleaned up {len(stale_connections)} stale connections")
        return len(stale_connections)

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        active_conns = [c for c in self.connections.values() if c.status == "active"]
        closed_conns = [c for c in self.connections.values() if c.status == "closed"]

        avg_rating = None
        if closed_conns:
            ratings = [c.rating for c in closed_conns if c.rating]
            if ratings:
                avg_rating = sum(ratings) / len(ratings)

        return {
            "total_peers": len(self.peers),
            "available_peers": len([p for p in self.peers.values() if p.availability]),
            "active_connections": len(active_conns),
            "closed_connections": len(closed_conns),
            "average_rating": avg_rating,
            "expertise_areas_covered": len(self.get_expertise_coverage()),
            "expertise_gaps": self.find_gap_expertise()
        }
