# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Run Commands

### Infrastructure (Required First)
```bash
docker compose up -d  # Starts RabbitMQ (5672/15672), Redis (6379), PostgreSQL (5432)
```

### Backend Services (Python/FastAPI)
```bash
python start_events.py       # Events service - Port 8000
python start_interaction.py  # Interaction service - Port 8001
python start_tasks.py        # Tasks service - Port 8002 (supports --rabbitmq --debug flags)
python start_trigger.py      # Trigger service - Port 8003
```

### Frontend (Vue 3 + Vite)
```bash
cd front
npm install
npm run dev      # Development server (port 5173)
npm run build    # Production build
```

### Running Tests
```bash
python -m pytest <test_file.py>           # Run specific test file
python -m pytest <dir>/                   # Run all tests in directory
python -m pytest -k "test_name"           # Run tests matching pattern
```

Test files are scattered across modules (e.g., `interaction/test_*.py`, `tasks/common/test_*.py`, `trigger/test_api_endpoints.py`).

## Architecture Overview

Flora is a **distributed multi-agent AI orchestration system** with 4 independent backend services:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vue 3)                         │
│              (Conversation UI + Task Overview)              │
└──────────────┬──────────────┬──────────────┬────────────────┘
               │              │              │
        ┌──────▼──────┐ ┌────▼──────┐ ┌────▼──────┐
        │ Interaction │ │   Tasks   │ │  Trigger  │
        │  (8001)     │ │  (8002)   │ │  (8003)   │
        └──────┬──────┘ └────┬──────┘ └────┬──────┘
               │             │             │
        ┌──────▼─────────────▼─────────────▼──────┐
        │         Events Service (8000)           │
        │    (Event/Observer Pattern Hub)         │
        └──────┬──────────────────────────────────┘
               │
        ┌──────▼──────────────────────────────────┐
        │  External Services: RabbitMQ, Redis,    │
        │  PostgreSQL, Neo4j, Dify, Mem0          │
        └─────────────────────────────────────────┘
```

### Service Responsibilities

- **Events (8000)**: Central event hub using Observer pattern, broadcasts via RabbitMQ
- **Interaction (8001)**: User conversations, Mem0 memory, Dify RAG integration, SSE streaming
- **Tasks (8002)**: Multi-agent execution using Thespian Actor framework, Neo4j-backed agent tree
- **Trigger (8003)**: Cron-based task scheduling and dispatch

## Key Architectural Patterns

### Multi-Agent Actor System (Thespian)
- Tasks service uses Thespian's actor model (`multiprocTCPBase`) for concurrent execution
- Hierarchical structure: root agents spawn child agents
- Agent metadata stored in Neo4j knowledge graph
- Message types: `AgentTaskMessage`, `TaskCompletedMessage`, `ResumeTaskMessage`

### Capability Plugin Architecture
Both `tasks/capabilities/` and `interaction/capabilities/` use a plugin system:
- Dynamic capability discovery via `capability_manager.py`
- Each capability implements a base interface (e.g., `ILLMCapability`, `IMemoryCapability`)
- Global registry accessed via `capability_registry.get_capability(name, interface)`
- Configuration-driven via JSON config files

Key capability types:
- `llm/`: LLM providers (Qwen via DashScope)
- `memory/`: Mem0-based memory management
- `task_planning/`: Task decomposition and planning
- `text_to_sql/`: Vanna-based natural language to SQL
- `context_manager/`, `dialog_state_manager/`: Conversation state

### Task Planning Pipeline
1. **Semantic Phase**: LLM decomposes user intent into task chain
2. **Structural Phase**: Neo4j dependency expansion and SCC detection
3. **Execution Phase**: Actor system executes with memory context injection

### Memory System
- **Core Memory**: Mem0 with Chroma vector store (local)
- **RAG**: Dify-based retrieval-augmented generation
- **Memory Extraction**: Automatic precipitation from conversations

## Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:
- `DASHSCOPE_API_KEY`: Alibaba Qwen LLM (required)
- `DIFY_API_KEY`, `DIFY_BASE_URL`: Dify RAG service
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`: Agent structure graph
- `REDIS_HOST`, `REDIS_PORT`: Cache layer
- `MEM0_API_KEY`: Memory service (optional)
- `POSTGRESQL_*`, `MYSQL_*`: Database connections for text-to-sql

### Config Files
- `events/event_config.json`: Auto-created on first run
- `trigger/trigger_config.json`: Auto-created (defaults to SQLite)
- `interaction/interaction_config.json`: Manual creation required
- `tasks/config.json`: Task service capabilities

## API Endpoints (Interaction Service)

Main conversation endpoints under `/v1`:
- `POST /conversations/{session_id}/messages` - Send message (returns 202, triggers async processing)
- `GET /conversations/{session_id}/stream` - SSE stream for responses
- `GET /session/{session_id}` - Get session info
- `GET /session/{session_id}/history` - Get conversation history
- `GET /user/{user_id}/sessions` - List user sessions
- `GET /memory/{user_id}/core` - Get/set core memories
- `GET /rag/documents` - List RAG documents (requires DIFY_API_KEY)

## Data Flow

### User Conversation
1. Frontend → Interaction service (`POST /v1/conversations/{session_id}/messages`)
2. Interaction retrieves Mem0 memory + Dify RAG context
3. LLM (Qwen) generates response, streams via SSE
4. Memory extracted and stored post-conversation

### Task Execution
1. Trigger scheduled task → publishes to RabbitMQ
2. Tasks service AgentActor loads agent tree from Neo4j
3. Task planner generates execution plan
4. Child actors spawned for subtasks
5. Results aggregated and returned

## Development Workflow

### New Feature Requests
When the user requests a new feature or significant change, follow this workflow:

1. **Interview First**: For non-trivial features, use `/openspec:interview <topic>` to clarify requirements before coding
2. **Create Proposal**: After interview confirmation, create a formal proposal with `/openspec:proposal`
3. **Implement**: Use `/openspec:apply` to implement the approved proposal
4. **Archive**: After completion, use `/openspec:archive` to archive the change

**Trigger interview mode when:**
- User says "我想要...", "帮我实现...", "添加一个功能...", "新增..."
- User describes a feature that touches multiple modules
- User's request is ambiguous or has multiple possible interpretations
- The change would take more than ~30 minutes to implement

**Skip interview for:**
- Bug fixes with clear reproduction steps
- Simple config changes
- Typos or documentation updates
- User explicitly says "直接做" or "不用问了"
