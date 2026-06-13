# Personalized Support System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Application (main app)                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         API Routes Layer (api_routes.py)             │  │
│  │                                                       │  │
│  │  POST /api/support/chat                              │  │
│  │  GET  /api/support/chat/history/{user_id}            │  │
│  │  POST /api/support/peer/connect                      │  │
│  │  GET  /api/support/knowledge/search                  │  │
│  │  ... (more routes)                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                        │                                    │
│                        ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      Chat Manager (chat_manager.py)                  │  │
│  │   [Central Orchestrator & Router]                    │  │
│  └──────────────────────────────────────────────────────┘  │
│      │                 │                  │                 │
│      ▼                 ▼                  ▼                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ AI Chatbot  │  │ Rule-Based   │  │ Peer Support │      │
│  │(LangChain)  │  │ Support      │  │ System       │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
│       │                │                  │                 │
│       ▼                ▼                  ▼                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Storage Layer (storage.py)                │   │
│  │                                                      │   │
│  │  - ConversationStorage                              │   │
│  │  - PeerSupportStorage                               │   │
│  │  - KnowledgeBaseStorage                             │   │
│  │  - AnalyticsStorage                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Configuration (config.py)                    │   │
│  │                                                      │   │
│  │  - SupportConfig                                    │   │
│  │  - SupportPromptConfig                              │   │
│  │  - PeerSupportConfig                                │   │
│  │  - AnalyticsConfig                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Routes Layer (`api_routes.py`)

**Purpose:** HTTP endpoints for the FastAPI application

**Key Endpoints:**
- `POST /api/support/chat` - Send chat message
- `GET /api/support/chat/history/{user_id}` - Get conversation history
- `DELETE /api/support/chat/history/{user_id}` - Clear history
- `GET /api/support/analysis/{user_id}` - Analyze user needs
- `POST /api/support/recommendations/{user_id}` - Get recommendations
- `GET /api/support/knowledge/search` - Search knowledge base
- `POST /api/support/peer/connect` - Connect with peer
- `GET /api/support/peer/available` - Get available peers
- `GET /api/support/peer/leaderboard` - Get peer rankings
- `GET /api/support/status` - System status

### 2. Chat Manager (`chat_manager.py`)

**Purpose:** Central orchestrator that routes requests to appropriate support type

**Responsibilities:**
- Route user messages to AI, rule-based, or peer support
- Auto-select best support type
- Maintain conversation context
- Coordinate between support systems
- Log analytics events

**Key Methods:**
```python
process_message(request)           # Main entry point
analyze_user_needs(user_id)        # Analyze support needs
get_personalized_recommendations() # Generate recommendations
create_peer_connection()           # Connect with peer
```

### 3. AI Chatbot (`langchain_chatbot.py`)

**Purpose:** LangChain-based intelligent chatbot using LLMs

**Technology Stack:**
- LangChain
- OpenAI GPT-3.5/GPT-4
- Conversation Memory
- Custom Prompts

**Key Features:**
- Multi-turn conversations
- Context awareness
- Specialized prompts for different scenarios:
  - Spending analysis
  - Goal setting
  - Crisis support
  - Contextual advice
- Conversation memory per user

**Key Methods:**
```python
chat()                    # Main chat interface
analyze_spending()        # Analyze spending patterns
suggest_goals()          # Generate goal suggestions
get_contextual_advice()  # Personalized recommendations
handle_crisis_support()  # Empathetic crisis handling
```

### 4. Rule-Based Support (`rule_based_support.py`)

**Purpose:** Fast, deterministic responses to common questions

**Rule Categories:**
1. **Spending Reduction** - How to cut expenses
2. **Budget Planning** - Creating budgets
3. **Savings Goals** - Building emergency fund, savings
4. **Expense Tracking** - Logging and monitoring
5. **Debt Management** - Paying down debt
6. **Investment Basics** - Starting to invest
7. **Tax Planning** - Tax optimization
8. **General Finance** - Broad financial topics

**Pattern Matching:**
- Uses regex patterns to match user queries
- Multiple responses per pattern for variation
- Suggests next steps contextually

**Performance:**
- <50ms response time
- Zero API dependencies
- Perfect for FAQ-type questions

**Key Methods:**
```python
process_query()        # Main entry point
find_matching_rule()   # Pattern matching
suggest_next_steps()   # Generate suggestions
search_knowledge_base() # Knowledge search
```

### 5. Peer Support System (`peer_support.py`)

**Purpose:** Connect users with experienced peer supporters

**Features:**
- Peer registration and profiles
- Reputation-based matching
- Real-time conversations
- Rating and feedback system
- Leaderboard

**Peer Matching Algorithm:**
1. Filter by expertise match
2. Filter by language match
3. Filter by availability
4. Sort by reputation score
5. Sort by experience (total helpings)

**Connection Management:**
- Active connections
- Connection history
- Auto-cleanup of old connections
- Transfer to AI if peer unavailable

**Key Methods:**
```python
register_peer()           # Register peer supporter
find_matching_peers()     # Match users with peers
create_connection()       # Create session
send_message()           # Exchange messages
close_connection()       # End session with rating
get_connection_stats()   # Peer performance
```

### 6. Storage Layer (`storage.py`)

**Purpose:** Persist conversations, peer data, and analytics

**Storage Types:**

#### ConversationStorage
- Store message history per user
- Save user metadata
- Retrieve conversations with limits

#### PeerSupportStorage
- Store peer profiles
- Save connection history
- Store peer reviews
- Calculate averages ratings

#### KnowledgeBaseStorage
- Store articles for knowledge base
- Search functionality
- Category organization

#### AnalyticsStorage
- Log events
- Track metrics
- Time-series data
- Aggregations

**Default:** In-memory (easily replaceable with Firebase, PostgreSQL, etc.)

### 7. Schemas (`schemas.py`)

**Purpose:** Pydantic models for request/response validation

**Key Models:**
- `ChatRequest` - User message input
- `ChatResponse` - System response output
- `ChatMessage` - Individual message
- `ConversationHistory` - Full conversation
- `PeerSupportRequest` - Peer connection request
- `PeerProfile` - Peer supporter profile
- `SupportAnalysis` - Analysis of user needs
- `RuleBasedResponse` - Rule system response

### 8. Prompts (`prompts.py`)

**Purpose:** LangChain prompt templates and examples

**Content:**
- System prompts
- Chat templates
- Few-shot examples
- Specialized prompts:
  - Spending analysis
  - Goal setting
  - Contextual advice
  - Crisis support
  - Conversation analysis

### 9. Configuration (`config.py`)

**Purpose:** Centralized configuration management

**Configuration Classes:**
- `SupportConfig` - Main configuration
- `SupportPromptConfig` - Prompt settings
- `PeerSupportConfig` - Peer system settings
- `AnalyticsConfig` - Analytics settings
- `ErrorConfig` - Error messages

**Environment Variables:**
- `OPENAI_API_KEY` - LLM API key
- `LOG_LEVEL` - Logging level
- `ENABLE_*_SUPPORT` - Feature flags
- `CONVERSATION_MEMORY_SIZE` - Memory limit
- And more...

## Data Flow Diagrams

### Chat Flow

```
User Message
     │
     ▼
ChatRequest → ChatManager
                │
                ├─► Determine Support Type
                │
                ├─► If auto:
                │   ├─► Try Rule-Based
                │   └─► Fallback to AI
                │
                ├─► Process with selected system
                │   ├─► Rule-Based → Pattern match → Response
                │   ├─► AI → LLM → Response
                │   └─► Peer → Find peer → Connect
                │
                ├─► Store message in history
                │
                ├─► Log analytics event
                │
                └─► Return ChatResponse
                     │
                     ▼
              Client receives response
```

### Peer Matching Flow

```
Peer Connection Request
     │
     ▼
Find Matching Peers
     │
     ├─► Filter by expertise
     ├─► Filter by language
     ├─► Filter by availability
     │
     ▼
Score and Sort Peers
     │
     ├─► By reputation score (primary)
     ├─► By total helpings (secondary)
     │
     ▼
Select Top Peer
     │
     ├─► If found:
     │   ├─► Create connection
     │   ├─► Store in history
     │   └─► Return connection details
     │
     └─► If not found:
         └─► Suggest AI alternative
```

## Integration Points

### With Expense Management System

```
Personalized Support ←→ Expense Management
         │                      │
         ├─► Get user spending  │
         ├─► Get budget info    │
         ├─► Get categories     │
         └─► Get trends         │
                                │
         ←─ Provide context for support
```

### With Firebase

```
Personalized Support ←→ Firebase Realtime Database
         │
         ├─► Store conversations
         ├─► Store peer data
         ├─► Store analytics
         └─► Retrieve history
```

## Deployment Architecture

### Single Server
```
┌──────────────────────────┐
│   FastAPI App            │
│ ┌──────────────────────┐ │
│ │ Support System       │ │
│ │ + Expense System     │ │
│ │ + Auth               │ │
│ └──────────────────────┘ │
└──────────────────────────┘
         │
         ▼
    Firebase
```

### Microservices
```
┌──────────────────┐
│  API Gateway     │
└────────┬─────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌──────┐
│Support │ │Chat  │ │Expense │ │Auth  │
│Manager │ │Store │ │Service │ │      │
└────────┘ └──────┘ └────────┘ └──────┘
    │
    ├─→ OpenAI API
    └─→ Firebase
```

## Performance Characteristics

| Component | Latency | Throughput | Storage |
|-----------|---------|-----------|---------|
| Rule-Based | <50ms | 1000s/sec | None |
| AI Chatbot | 1-3s | 10-100/sec | Chat history |
| Peer Support | <100ms | N/A | Connections |
| Storage | Variable | Variable | Per-use |

## Security Considerations

```
┌─────────────────────────────────────┐
│    User Input Validation            │
│    (schemas.py via Pydantic)        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│    Rate Limiting                    │
│    (API layer)                      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│    Authentication/Authorization     │
│    (FastAPI security)               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│    Sensitive Data Handling          │
│    - No logging of sensitive data   │
│    - HTTPS only                     │
│    - Encrypted storage              │
└─────────────────────────────────────┘
```

## Scalability Strategy

1. **Horizontal Scaling:**
   - Multiple API instances behind load balancer
   - Shared storage (Firebase/Database)
   - Queue for AI requests (to manage cost)

2. **Vertical Scaling:**
   - Increase server resources
   - Optimize LLM calls with caching
   - Use faster models (GPT-3.5 vs GPT-4)

3. **Optimization:**
   - Cache rule-based responses
   - Batch AI requests
   - Use peer support to reduce AI load
   - Implement conversation summarization

## File Structure

```
backend/src/personalised_support/
├── __init__.py              # Package exports
├── api_routes.py            # FastAPI routes
├── chat_manager.py          # Central orchestrator
├── langchain_chatbot.py     # AI chatbot
├── rule_based_support.py    # Rule system
├── peer_support.py          # Peer network
├── storage.py               # Storage layer
├── schemas.py               # Pydantic models
├── prompts.py               # LangChain prompts
├── config.py                # Configuration
├── examples.py              # Usage examples
├── requirements.txt         # Dependencies
├── README.md                # Main documentation
├── INTEGRATION_GUIDE.md     # Integration instructions
└── ARCHITECTURE.md          # This file
```

## Dependencies

### Core
- `langchain` - LLM orchestration
- `openai` - GPT models
- `fastapi` - Web framework
- `pydantic` - Data validation

### Optional
- `firebase-admin` - Firebase integration
- `sqlalchemy` - Database ORM
- `redis` - Caching
- `pytest` - Testing

## Future Enhancements

1. **Multi-language Support**
   - Translate prompts
   - Regional peer networks
   - Localized rule sets

2. **Advanced NLP**
   - Intent recognition
   - Entity extraction
   - Sentiment analysis

3. **Machine Learning**
   - Predict user support needs
   - Peer matching optimization
   - Response quality ranking

4. **Mobile Integration**
   - Mobile app API
   - Push notifications
   - Voice support

5. **Enterprise Features**
   - White-label support
   - Custom rule sets
   - Advanced analytics dashboard

---

**Last Updated:** 2024
**Version:** 1.0
