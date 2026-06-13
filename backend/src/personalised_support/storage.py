"""
Storage layer for conversations and peer support data
"""

import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationStorage:
    """Store and retrieve conversation data"""

    def __init__(self):
        """Initialize storage (in-memory for now, can be replaced with DB)"""
        self.conversations: Dict[str, List[Dict]] = {}
        self.metadata: Dict[str, Dict] = {}

    def save_message(
        self,
        user_id: str,
        role: str,
        content: str,
        message_type: str
    ) -> None:
        """Save a message to conversation history"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        message = {
            "role": role,
            "content": content,
            "message_type": message_type,
            "timestamp": datetime.now().isoformat()
        }

        self.conversations[user_id].append(message)
        logger.info(f"Saved message for user {user_id}")

    def get_conversation(
        self,
        user_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Retrieve conversation history"""
        messages = self.conversations.get(user_id, [])

        if limit:
            messages = messages[-limit:]

        return messages

    def clear_conversation(self, user_id: str) -> None:
        """Clear conversation history"""
        if user_id in self.conversations:
            del self.conversations[user_id]
        if user_id in self.metadata:
            del self.metadata[user_id]
        logger.info(f"Cleared conversation for user {user_id}")

    def save_metadata(self, user_id: str, metadata: Dict[str, Any]) -> None:
        """Save user metadata"""
        if user_id not in self.metadata:
            self.metadata[user_id] = {}

        self.metadata[user_id].update({
            **metadata,
            "updated_at": datetime.now().isoformat()
        })

    def get_metadata(self, user_id: str) -> Optional[Dict]:
        """Get user metadata"""
        return self.metadata.get(user_id)


class PeerSupportStorage:
    """Store peer support connections and interactions"""

    def __init__(self):
        """Initialize peer storage"""
        self.peers: Dict[str, Dict] = {}
        self.connections: Dict[str, Dict] = {}
        self.reviews: Dict[str, List[Dict]] = {}

    def save_peer(
        self,
        peer_id: str,
        profile: Dict[str, Any]
    ) -> None:
        """Save peer profile"""
        self.peers[peer_id] = {
            **profile,
            "created_at": datetime.now().isoformat() if "created_at" not in profile else profile["created_at"],
            "updated_at": datetime.now().isoformat()
        }
        logger.info(f"Saved peer profile: {peer_id}")

    def get_peer(self, peer_id: str) -> Optional[Dict]:
        """Get peer profile"""
        return self.peers.get(peer_id)

    def save_connection(
        self,
        connection_id: str,
        connection_data: Dict[str, Any]
    ) -> None:
        """Save peer support connection"""
        self.connections[connection_id] = {
            **connection_data,
            "created_at": datetime.now().isoformat() if "created_at" not in connection_data else connection_data["created_at"],
            "updated_at": datetime.now().isoformat()
        }
        logger.info(f"Saved connection: {connection_id}")

    def get_connection(self, connection_id: str) -> Optional[Dict]:
        """Get connection details"""
        return self.connections.get(connection_id)

    def save_review(
        self,
        connection_id: str,
        peer_id: str,
        user_id: str,
        rating: float,
        feedback: Optional[str] = None
    ) -> None:
        """Save peer review"""
        if peer_id not in self.reviews:
            self.reviews[peer_id] = []

        review = {
            "connection_id": connection_id,
            "user_id": user_id,
            "rating": rating,
            "feedback": feedback,
            "created_at": datetime.now().isoformat()
        }

        self.reviews[peer_id].append(review)
        logger.info(f"Saved review for peer {peer_id}")

    def get_peer_reviews(self, peer_id: str) -> List[Dict]:
        """Get reviews for a peer"""
        return self.reviews.get(peer_id, [])

    def get_average_rating(self, peer_id: str) -> Optional[float]:
        """Get average rating for a peer"""
        reviews = self.reviews.get(peer_id, [])
        if not reviews:
            return None

        ratings = [r["rating"] for r in reviews]
        return sum(ratings) / len(ratings)


class KnowledgeBaseStorage:
    """Store rule-based knowledge base"""

    def __init__(self):
        """Initialize knowledge base"""
        self.articles: Dict[str, Dict] = {}
        self.categories: Dict[str, List[str]] = {}

    def add_article(
        self,
        article_id: str,
        category: str,
        title: str,
        content: str,
        tags: Optional[List[str]] = None
    ) -> None:
        """Add article to knowledge base"""
        self.articles[article_id] = {
            "category": category,
            "title": title,
            "content": content,
            "tags": tags or [],
            "created_at": datetime.now().isoformat()
        }

        if category not in self.categories:
            self.categories[category] = []

        if article_id not in self.categories[category]:
            self.categories[category].append(article_id)

        logger.info(f"Added article: {article_id}")

    def get_article(self, article_id: str) -> Optional[Dict]:
        """Get article by ID"""
        return self.articles.get(article_id)

    def search_articles(self, query: str) -> List[Dict]:
        """Search articles"""
        results = []

        for article_id, article in self.articles.items():
            if (query.lower() in article["title"].lower() or
                query.lower() in article["content"].lower() or
                any(query.lower() in tag.lower() for tag in article.get("tags", []))):
                results.append({**article, "id": article_id})

        return results

    def get_category_articles(self, category: str) -> List[Dict]:
        """Get all articles in a category"""
        article_ids = self.categories.get(category, [])
        return [
            {**self.articles[aid], "id": aid}
            for aid in article_ids
            if aid in self.articles
        ]


class AnalyticsStorage:
    """Store analytics and metrics"""

    def __init__(self):
        """Initialize analytics"""
        self.events: List[Dict] = []
        self.metrics: Dict[str, Any] = {}

    def log_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """Log an event"""
        event = {
            "event_type": event_type,
            "user_id": user_id,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        logger.info(f"Logged event: {event_type}")

    def get_events(
        self,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get events with optional filtering"""
        filtered = self.events

        if event_type:
            filtered = [e for e in filtered if e["event_type"] == event_type]

        if user_id:
            filtered = [e for e in filtered if e["user_id"] == user_id]

        return filtered[-limit:]

    def update_metric(self, metric_name: str, value: Any) -> None:
        """Update a metric"""
        self.metrics[metric_name] = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }

    def get_metric(self, metric_name: str) -> Any:
        """Get a metric value"""
        metric = self.metrics.get(metric_name, {})
        return metric.get("value")

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return {
            name: data.get("value")
            for name, data in self.metrics.items()
        }
