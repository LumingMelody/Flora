"""
统计 API - 提供系统级、Agent级、Trace级的统计指标
"""
import logging
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case

from ..deps import get_db_session, get_agent_monitor_service
from services.agent_monitor_service import AgentMonitorService
from external.db.models import EventInstanceDB, EventTraceDB, AgentTaskHistoryDB, AgentDailyMetricDB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stats", tags=["统计"])


# ==================== 响应模型 ====================

class SystemOverviewResponse(BaseModel):
    """系统总览响应"""
    total_agents: int
    online_agents: int
    offline_agents: int
    running_traces: int
    pending_tasks: int
    today_total_tasks: int
    today_success_tasks: int
    today_failed_tasks: int
    success_rate: float
    avg_duration_ms: Optional[float] = None


class DailyStatsResponse(BaseModel):
    """每日统计响应"""
    date: str
    total_tasks: int
    success_tasks: int
    failed_tasks: int
    cancelled_tasks: int
    avg_duration_ms: Optional[float] = None
    success_rate: float


class TrendDataResponse(BaseModel):
    """趋势数据响应"""
    dates: List[str]
    total_tasks: List[int]
    success_tasks: List[int]
    failed_tasks: List[int]
    success_rates: List[float]


class AgentSummaryResponse(BaseModel):
    """Agent 摘要响应"""
    agent_id: str
    status: str  # IDLE / BUSY / OFFLINE
    last_seen: Optional[datetime] = None
    current_task: Optional[Dict[str, Any]] = None
    today_total: int
    today_success: int
    today_failed: int
    avg_duration_ms: Optional[float] = None
    success_rate: float


class AgentHistoryItem(BaseModel):
    """Agent 历史记录项"""
    task_id: str
    task_name: Optional[str] = None
    trace_id: str
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    error_msg: Optional[str] = None


class StatusDistribution(BaseModel):
    """状态分布"""
    pending: int = 0
    running: int = 0
    success: int = 0
    failed: int = 0
    cancelled: int = 0
    paused: int = 0


class TraceSummaryStatsResponse(BaseModel):
    """Trace 统计摘要响应"""
    trace_id: str
    status: str
    total_tasks: int
    status_distribution: StatusDistribution
    max_depth: int
    duration_ms: Optional[int] = None
    created_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class TopAgentItem(BaseModel):
    """Top Agent 项"""
    agent_id: str
    total_tasks: int
    success_tasks: int
    failed_tasks: int
    success_rate: float
    avg_duration_ms: Optional[float] = None


# ==================== 系统级统计 API ====================

@router.get("/system/overview", response_model=SystemOverviewResponse)
async def get_system_overview(
    session: AsyncSession = Depends(get_db_session),
    agent_monitor: AgentMonitorService = Depends(get_agent_monitor_service)
):
    """
    获取系统总览指标

    返回：
    - 总 Agent 数量、在线/离线数量
    - 运行中的 Trace 数量
    - 待处理任务数量
    - 今日任务统计
    """
    try:
        # 获取 Agent 状态统计
        agent_states = agent_monitor.get_all_agent_states()
        total_agents = len(agent_states)
        online_agents = sum(1 for s in agent_states.values() if s.get("status") in ["IDLE", "BUSY"])
        offline_agents = total_agents - online_agents

        # 获取运行中的 Trace 数量
        running_traces_result = await session.execute(
            select(func.count(EventTraceDB.trace_id)).where(
                EventTraceDB.status == "RUNNING"
            )
        )
        running_traces = running_traces_result.scalar() or 0

        # 获取待处理任务数量
        pending_tasks_result = await session.execute(
            select(func.count(EventInstanceDB.id)).where(
                EventInstanceDB.status == "PENDING"
            )
        )
        pending_tasks = pending_tasks_result.scalar() or 0

        # 获取今日任务统计
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        today_stats_result = await session.execute(
            select(
                func.count(AgentTaskHistoryDB.id).label("total"),
                func.sum(case((AgentTaskHistoryDB.status == "COMPLETED", 1), else_=0)).label("success"),
                func.sum(case((AgentTaskHistoryDB.status == "FAILED", 1), else_=0)).label("failed"),
                func.avg(AgentTaskHistoryDB.duration_ms).label("avg_duration")
            ).where(
                AgentTaskHistoryDB.created_at >= today_start
            )
        )
        today_stats = today_stats_result.fetchone()

        today_total = today_stats.total or 0
        today_success = today_stats.success or 0
        today_failed = today_stats.failed or 0
        avg_duration = today_stats.avg_duration

        success_rate = (today_success / today_total * 100) if today_total > 0 else 0.0

        return SystemOverviewResponse(
            total_agents=total_agents,
            online_agents=online_agents,
            offline_agents=offline_agents,
            running_traces=running_traces,
            pending_tasks=pending_tasks,
            today_total_tasks=today_total,
            today_success_tasks=today_success,
            today_failed_tasks=today_failed,
            success_rate=round(success_rate, 2),
            avg_duration_ms=round(avg_duration, 2) if avg_duration else None
        )

    except Exception as e:
        logger.error(f"Failed to get system overview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/daily", response_model=DailyStatsResponse)
async def get_daily_stats(
    date: Optional[str] = Query(None, description="日期 (YYYY-MM-DD)，默认今天"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    获取指定日期的统计数据
    """
    try:
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        else:
            target_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        next_date = target_date + timedelta(days=1)

        stats_result = await session.execute(
            select(
                func.count(AgentTaskHistoryDB.id).label("total"),
                func.sum(case((AgentTaskHistoryDB.status == "COMPLETED", 1), else_=0)).label("success"),
                func.sum(case((AgentTaskHistoryDB.status == "FAILED", 1), else_=0)).label("failed"),
                func.sum(case((AgentTaskHistoryDB.status == "CANCELLED", 1), else_=0)).label("cancelled"),
                func.avg(AgentTaskHistoryDB.duration_ms).label("avg_duration")
            ).where(
                and_(
                    AgentTaskHistoryDB.created_at >= target_date,
                    AgentTaskHistoryDB.created_at < next_date
                )
            )
        )
        stats = stats_result.fetchone()

        total = stats.total or 0
        success = stats.success or 0
        failed = stats.failed or 0
        cancelled = stats.cancelled or 0
        avg_duration = stats.avg_duration

        success_rate = (success / total * 100) if total > 0 else 0.0

        return DailyStatsResponse(
            date=target_date.strftime("%Y-%m-%d"),
            total_tasks=total,
            success_tasks=success,
            failed_tasks=failed,
            cancelled_tasks=cancelled,
            avg_duration_ms=round(avg_duration, 2) if avg_duration else None,
            success_rate=round(success_rate, 2)
        )

    except Exception as e:
        logger.error(f"Failed to get daily stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/trend", response_model=TrendDataResponse)
async def get_trend_data(
    days: int = Query(7, ge=1, le=30, description="天数"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    获取最近 N 天的趋势数据
    """
    try:
        dates = []
        total_tasks = []
        success_tasks = []
        failed_tasks = []
        success_rates = []

        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        for i in range(days - 1, -1, -1):
            target_date = today - timedelta(days=i)
            next_date = target_date + timedelta(days=1)

            stats_result = await session.execute(
                select(
                    func.count(AgentTaskHistoryDB.id).label("total"),
                    func.sum(case((AgentTaskHistoryDB.status == "COMPLETED", 1), else_=0)).label("success"),
                    func.sum(case((AgentTaskHistoryDB.status == "FAILED", 1), else_=0)).label("failed")
                ).where(
                    and_(
                        AgentTaskHistoryDB.created_at >= target_date,
                        AgentTaskHistoryDB.created_at < next_date
                    )
                )
            )
            stats = stats_result.fetchone()

            total = stats.total or 0
            success = stats.success or 0
            failed = stats.failed or 0
            rate = (success / total * 100) if total > 0 else 0.0

            dates.append(target_date.strftime("%Y-%m-%d"))
            total_tasks.append(total)
            success_tasks.append(success)
            failed_tasks.append(failed)
            success_rates.append(round(rate, 2))

        return TrendDataResponse(
            dates=dates,
            total_tasks=total_tasks,
            success_tasks=success_tasks,
            failed_tasks=failed_tasks,
            success_rates=success_rates
        )

    except Exception as e:
        logger.error(f"Failed to get trend data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/top-agents", response_model=List[TopAgentItem])
async def get_top_agents(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    days: int = Query(7, ge=1, le=30, description="统计天数"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    获取 Top N 活跃 Agent
    """
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        result = await session.execute(
            select(
                AgentTaskHistoryDB.agent_id,
                func.count(AgentTaskHistoryDB.id).label("total"),
                func.sum(case((AgentTaskHistoryDB.status == "COMPLETED", 1), else_=0)).label("success"),
                func.sum(case((AgentTaskHistoryDB.status == "FAILED", 1), else_=0)).label("failed"),
                func.avg(AgentTaskHistoryDB.duration_ms).label("avg_duration")
            ).where(
                AgentTaskHistoryDB.created_at >= start_date
            ).group_by(
                AgentTaskHistoryDB.agent_id
            ).order_by(
                func.count(AgentTaskHistoryDB.id).desc()
            ).limit(limit)
        )

        items = []
        for row in result.fetchall():
            total = row.total or 0
            success = row.success or 0
            failed = row.failed or 0
            rate = (success / total * 100) if total > 0 else 0.0

            items.append(TopAgentItem(
                agent_id=row.agent_id,
                total_tasks=total,
                success_tasks=success,
                failed_tasks=failed,
                success_rate=round(rate, 2),
                avg_duration_ms=round(row.avg_duration, 2) if row.avg_duration else None
            ))

        return items

    except Exception as e:
        logger.error(f"Failed to get top agents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Agent 级统计 API ====================

@router.get("/agents/{agent_id}/summary", response_model=AgentSummaryResponse)
async def get_agent_summary(
    agent_id: str,
    session: AsyncSession = Depends(get_db_session),
    agent_monitor: AgentMonitorService = Depends(get_agent_monitor_service)
):
    """
    获取指定 Agent 的摘要信息
    """
    try:
        # 获取 Agent 实时状态
        agent_state = agent_monitor.get_agent_state(agent_id)
        status = agent_state.get("status", "OFFLINE") if agent_state else "OFFLINE"
        last_seen = agent_state.get("last_seen") if agent_state else None
        current_task = agent_state.get("current_task") if agent_state else None

        # 获取今日统计
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        stats_result = await session.execute(
            select(
                func.count(AgentTaskHistoryDB.id).label("total"),
                func.sum(case((AgentTaskHistoryDB.status == "COMPLETED", 1), else_=0)).label("success"),
                func.sum(case((AgentTaskHistoryDB.status == "FAILED", 1), else_=0)).label("failed"),
                func.avg(AgentTaskHistoryDB.duration_ms).label("avg_duration")
            ).where(
                and_(
                    AgentTaskHistoryDB.agent_id == agent_id,
                    AgentTaskHistoryDB.created_at >= today_start
                )
            )
        )
        stats = stats_result.fetchone()

        total = stats.total or 0
        success = stats.success or 0
        failed = stats.failed or 0
        avg_duration = stats.avg_duration

        success_rate = (success / total * 100) if total > 0 else 0.0

        return AgentSummaryResponse(
            agent_id=agent_id,
            status=status,
            last_seen=last_seen,
            current_task=current_task,
            today_total=total,
            today_success=success,
            today_failed=failed,
            avg_duration_ms=round(avg_duration, 2) if avg_duration else None,
            success_rate=round(success_rate, 2)
        )

    except Exception as e:
        logger.error(f"Failed to get agent summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}/history", response_model=List[AgentHistoryItem])
async def get_agent_history(
    agent_id: str,
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    获取指定 Agent 的历史任务记录
    """
    try:
        result = await session.execute(
            select(AgentTaskHistoryDB).where(
                AgentTaskHistoryDB.agent_id == agent_id
            ).order_by(
                AgentTaskHistoryDB.created_at.desc()
            ).limit(limit)
        )

        items = []
        for row in result.scalars():
            items.append(AgentHistoryItem(
                task_id=row.task_id,
                task_name=row.task_name,
                trace_id=row.trace_id,
                status=row.status,
                start_time=row.start_time,
                end_time=row.end_time,
                duration_ms=row.duration_ms,
                error_msg=row.error_msg
            ))

        return items

    except Exception as e:
        logger.error(f"Failed to get agent history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}/metrics", response_model=List[DailyStatsResponse])
async def get_agent_metrics(
    agent_id: str,
    days: int = Query(7, ge=1, le=30, description="天数"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    获取指定 Agent 最近 N 天的每日统计
    """
    try:
        result = await session.execute(
            select(AgentDailyMetricDB).where(
                AgentDailyMetricDB.agent_id == agent_id
            ).order_by(
                AgentDailyMetricDB.date_str.desc()
            ).limit(days)
        )

        items = []
        for row in result.scalars():
            total = row.total_tasks or 0
            success = row.success_tasks or 0
            failed = row.failed_tasks or 0
            rate = (success / total * 100) if total > 0 else 0.0
            avg_duration = (row.total_duration_ms / total) if total > 0 else None

            items.append(DailyStatsResponse(
                date=row.date_str,
                total_tasks=total,
                success_tasks=success,
                failed_tasks=failed,
                cancelled_tasks=0,  # 日报表中没有 cancelled 字段
                avg_duration_ms=round(avg_duration, 2) if avg_duration else None,
                success_rate=round(rate, 2)
            ))

        # 按日期正序返回
        items.reverse()
        return items

    except Exception as e:
        logger.error(f"Failed to get agent metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Trace 级统计 API ====================

@router.get("/traces/{trace_id}/stats", response_model=TraceSummaryStatsResponse)
async def get_trace_stats(
    trace_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """
    获取指定 Trace 的统计摘要
    """
    try:
        # 获取 Trace 基本信息
        trace_result = await session.execute(
            select(EventTraceDB).where(EventTraceDB.trace_id == trace_id)
        )
        trace = trace_result.scalar_one_or_none()

        if not trace:
            raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")

        # 获取任务统计
        stats_result = await session.execute(
            select(
                func.count(EventInstanceDB.id).label("total"),
                func.max(EventInstanceDB.depth).label("max_depth"),
                func.sum(case((EventInstanceDB.status == "PENDING", 1), else_=0)).label("pending"),
                func.sum(case((EventInstanceDB.status == "RUNNING", 1), else_=0)).label("running"),
                func.sum(case((EventInstanceDB.status == "SUCCESS", 1), else_=0)).label("success"),
                func.sum(case((EventInstanceDB.status == "FAILED", 1), else_=0)).label("failed"),
                func.sum(case((EventInstanceDB.status == "CANCELLED", 1), else_=0)).label("cancelled"),
                func.sum(case((EventInstanceDB.status == "PAUSED", 1), else_=0)).label("paused")
            ).where(
                EventInstanceDB.trace_id == trace_id
            )
        )
        stats = stats_result.fetchone()

        # 计算耗时
        duration_ms = None
        if trace.created_at:
            end_time = trace.ended_at or datetime.now(timezone.utc)
            if trace.created_at.tzinfo is None:
                trace.created_at = trace.created_at.replace(tzinfo=timezone.utc)
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=timezone.utc)
            duration_ms = int((end_time - trace.created_at).total_seconds() * 1000)

        return TraceSummaryStatsResponse(
            trace_id=trace_id,
            status=trace.status or "UNKNOWN",
            total_tasks=stats.total or 0,
            status_distribution=StatusDistribution(
                pending=stats.pending or 0,
                running=stats.running or 0,
                success=stats.success or 0,
                failed=stats.failed or 0,
                cancelled=stats.cancelled or 0,
                paused=stats.paused or 0
            ),
            max_depth=stats.max_depth or 0,
            duration_ms=duration_ms,
            created_at=trace.created_at,
            ended_at=trace.ended_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get trace stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces/recent", response_model=List[TraceSummaryStatsResponse])
async def get_recent_traces(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    status: Optional[str] = Query(None, description="状态过滤"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    获取最近的 Trace 列表
    """
    try:
        query = select(EventTraceDB).order_by(EventTraceDB.created_at.desc())

        if status:
            query = query.where(EventTraceDB.status == status)

        query = query.limit(limit)

        result = await session.execute(query)
        traces = result.scalars().all()

        items = []
        for trace in traces:
            # 获取每个 trace 的任务统计
            stats_result = await session.execute(
                select(
                    func.count(EventInstanceDB.id).label("total"),
                    func.max(EventInstanceDB.depth).label("max_depth"),
                    func.sum(case((EventInstanceDB.status == "PENDING", 1), else_=0)).label("pending"),
                    func.sum(case((EventInstanceDB.status == "RUNNING", 1), else_=0)).label("running"),
                    func.sum(case((EventInstanceDB.status == "SUCCESS", 1), else_=0)).label("success"),
                    func.sum(case((EventInstanceDB.status == "FAILED", 1), else_=0)).label("failed"),
                    func.sum(case((EventInstanceDB.status == "CANCELLED", 1), else_=0)).label("cancelled"),
                    func.sum(case((EventInstanceDB.status == "PAUSED", 1), else_=0)).label("paused")
                ).where(
                    EventInstanceDB.trace_id == trace.trace_id
                )
            )
            stats = stats_result.fetchone()

            # 计算耗时
            duration_ms = None
            if trace.created_at:
                end_time = trace.ended_at or datetime.now(timezone.utc)
                if trace.created_at.tzinfo is None:
                    trace.created_at = trace.created_at.replace(tzinfo=timezone.utc)
                if end_time.tzinfo is None:
                    end_time = end_time.replace(tzinfo=timezone.utc)
                duration_ms = int((end_time - trace.created_at).total_seconds() * 1000)

            items.append(TraceSummaryStatsResponse(
                trace_id=trace.trace_id,
                status=trace.status or "UNKNOWN",
                total_tasks=stats.total or 0,
                status_distribution=StatusDistribution(
                    pending=stats.pending or 0,
                    running=stats.running or 0,
                    success=stats.success or 0,
                    failed=stats.failed or 0,
                    cancelled=stats.cancelled or 0,
                    paused=stats.paused or 0
                ),
                max_depth=stats.max_depth or 0,
                duration_ms=duration_ms,
                created_at=trace.created_at,
                ended_at=trace.ended_at
            ))

        return items

    except Exception as e:
        logger.error(f"Failed to get recent traces: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
