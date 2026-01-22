from typing import Literal
from sqlalchemy.ext.asyncio import AsyncSession

from ..base import EventInstanceRepository, EventDefinitionRepository, EventLogRepository, AgentTaskHistoryRepository, AgentDailyMetricRepository
from .sqlite_impl import (
    SQLiteEventInstanceRepository,
    SQLiteEventDefinitionRepository,
    SQLiteEventLogRepository,
    SQLiteAgentTaskHistoryRepository,
    SQLiteAgentDailyMetricRepository
)
from .postgres_impl import (
    PostgreSQLEventInstanceRepository,
    PostgreSQLEventDefinitionRepository,
    PostgreSQLEventLogRepository,
    PostgreSQLAgentTaskHistoryRepository,
    PostgreSQLAgentDailyMetricRepository
)

def create_event_instance_repo(
    session: AsyncSession,
    dialect: Literal["sqlite", "postgresql", "mysql"]
) -> EventInstanceRepository:
    if dialect == "sqlite":
        return SQLiteEventInstanceRepository(session)
    elif dialect in ("postgresql", "mysql"):
        return PostgreSQLEventInstanceRepository(session)
    else:
        raise ValueError(f"Unsupported dialect: {dialect}")

def create_event_definition_repo(
    session: AsyncSession,
    dialect: Literal["sqlite", "postgresql", "mysql"]
) -> EventDefinitionRepository:
    if dialect == "sqlite":
        return SQLiteEventDefinitionRepository(session)
    elif dialect in ("postgresql", "mysql"):
        return PostgreSQLEventDefinitionRepository(session)
    else:
        raise ValueError(f"Unsupported dialect: {dialect}")

def create_event_log_repo(
    session: AsyncSession,
    dialect: Literal["sqlite", "postgresql", "mysql"]
) -> EventLogRepository:
    if dialect == "sqlite":
        return SQLiteEventLogRepository(session)
    elif dialect in ("postgresql", "mysql"):
        return PostgreSQLEventLogRepository(session)
    else:
        raise ValueError(f"Unsupported dialect: {dialect}")

def create_agent_task_history_repo(
    session: AsyncSession,
    dialect: Literal["sqlite", "postgresql", "mysql"]
) -> AgentTaskHistoryRepository:
    if dialect == "sqlite":
        return SQLiteAgentTaskHistoryRepository(session)
    elif dialect in ("postgresql", "mysql"):
        return PostgreSQLAgentTaskHistoryRepository(session)
    else:
        raise ValueError(f"Unsupported dialect: {dialect}")

def create_agent_daily_metric_repo(
    session: AsyncSession,
    dialect: Literal["sqlite", "postgresql", "mysql"]
) -> AgentDailyMetricRepository:
    if dialect == "sqlite":
        return SQLiteAgentDailyMetricRepository(session)
    elif dialect in ("postgresql", "mysql"):
        return PostgreSQLAgentDailyMetricRepository(session)
    else:
        raise ValueError(f"Unsupported dialect: {dialect}")