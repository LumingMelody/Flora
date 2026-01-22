from typing import List, Optional, Dict, Any
import json
import os
import logging
from datetime import datetime

from common.task_draft import TaskDraftDTO, SlotValueDTO, ScheduleDTO

logger = logging.getLogger(__name__)

# 数据库类型
DB_TYPE = os.getenv('DB_TYPE', 'sqlite').lower()


class TaskDraftRepository:
    def __init__(self, pool=None):
        self.db_type = DB_TYPE
        self._is_mysql = self.db_type == 'mysql'

        if pool:
            self.pool = pool
        elif self._is_mysql:
            from .mysql_pool import MySQLConnectionPool
            self.pool = MySQLConnectionPool(database='flora_interaction')
        else:
            from .sqlite_pool import SQLiteConnectionPool
            self.pool = SQLiteConnectionPool(db_path="task_drafts.db")

        self._create_table()

    def _ph(self, sql: str) -> str:
        """转换 SQL 占位符：MySQL 用 %s，SQLite 用 ?"""
        if self._is_mysql:
            return sql.replace('?', '%s')
        return sql

    def _create_table(self):
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()

            if self._is_mysql:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS task_drafts (
                        draft_id VARCHAR(255) PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        task_type VARCHAR(255) NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        slots LONGTEXT NOT NULL,
                        missing_slots TEXT NOT NULL,
                        invalid_slots TEXT NOT NULL,
                        schedule TEXT,
                        is_cancelable TINYINT NOT NULL,
                        is_resumable TINYINT NOT NULL,
                        original_utterances TEXT NOT NULL,
                        created_at DOUBLE NOT NULL,
                        updated_at DOUBLE NOT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                ''')
            else:
                # 先创建表（如果不存在）
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS task_drafts (
                        draft_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        task_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        slots TEXT NOT NULL,
                        missing_slots TEXT NOT NULL,
                        invalid_slots TEXT NOT NULL,
                        schedule TEXT,
                        is_cancelable INTEGER NOT NULL,
                        is_resumable INTEGER NOT NULL,
                        original_utterances TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL
                    )
                ''')

                # 获取当前表的所有列名
                cursor.execute("PRAGMA table_info(task_drafts)")
                columns = {col[1] for col in cursor.fetchall()}

                # 对每个期望的列，如果不存在就添加
                if 'user_id' not in columns:
                    cursor.execute("ALTER TABLE task_drafts ADD COLUMN user_id TEXT")

            conn.commit()
        finally:
            self.pool.return_connection(conn)

    def _serialize_slots(self, slots: Dict[str, SlotValueDTO]) -> str:
        return json.dumps({
            k: v.model_dump() for k, v in slots.items()
        })

    def _deserialize_slots(self, slots_str: str) -> Dict[str, SlotValueDTO]:
        return {
            k: SlotValueDTO(**v) for k, v in json.loads(slots_str).items()
        }

    def _serialize_list(self, lst: List[str]) -> str:
        return json.dumps(lst)

    def _deserialize_list(self, lst_str: str) -> List[str]:
        return json.loads(lst_str)

    def _serialize_schedule(self, schedule: Optional[ScheduleDTO]) -> Optional[str]:
        return json.dumps(schedule.model_dump()) if schedule else None

    def _deserialize_schedule(self, schedule_str: Optional[str]) -> Optional[ScheduleDTO]:
        return ScheduleDTO(**json.loads(schedule_str)) if schedule_str else None

    def _row_to_draft(self, row) -> TaskDraftDTO:
        """将数据库行转换为 TaskDraftDTO"""
        if self._is_mysql:
            return TaskDraftDTO(
                draft_id=row['draft_id'],
                user_id=row['user_id'],
                task_type=row['task_type'],
                status=row['status'],
                slots=self._deserialize_slots(row['slots']),
                missing_slots=self._deserialize_list(row['missing_slots']),
                invalid_slots=self._deserialize_list(row['invalid_slots']),
                schedule=self._deserialize_schedule(row['schedule']),
                is_cancelable=bool(row['is_cancelable']),
                is_resumable=bool(row['is_resumable']),
                original_utterances=self._deserialize_list(row['original_utterances']),
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        else:
            return TaskDraftDTO(
                draft_id=row['draft_id'],
                user_id=row['user_id'],
                task_type=row['task_type'],
                status=row['status'],
                slots=self._deserialize_slots(row['slots']),
                missing_slots=self._deserialize_list(row['missing_slots']),
                invalid_slots=self._deserialize_list(row['invalid_slots']),
                schedule=self._deserialize_schedule(row['schedule']),
                is_cancelable=bool(row['is_cancelable']),
                is_resumable=bool(row['is_resumable']),
                original_utterances=self._deserialize_list(row['original_utterances']),
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )

    def save_draft(self, draft: TaskDraftDTO) -> bool:
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            if self._is_mysql:
                cursor.execute('''
                    REPLACE INTO task_drafts (
                        draft_id, user_id, task_type, status, slots, missing_slots, invalid_slots,
                        schedule, is_cancelable, is_resumable, original_utterances,
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    draft.draft_id,
                    draft.user_id,
                    draft.task_type,
                    draft.status,
                    self._serialize_slots(draft.slots),
                    self._serialize_list(draft.missing_slots),
                    self._serialize_list(draft.invalid_slots),
                    self._serialize_schedule(draft.schedule),
                    1 if draft.is_cancelable else 0,
                    1 if draft.is_resumable else 0,
                    self._serialize_list(draft.original_utterances),
                    draft.created_at,
                    draft.updated_at
                ))
            else:
                cursor.execute('''
                    INSERT OR REPLACE INTO task_drafts (
                        draft_id, user_id, task_type, status, slots, missing_slots, invalid_slots,
                        schedule, is_cancelable, is_resumable, original_utterances,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    draft.draft_id,
                    draft.user_id,
                    draft.task_type,
                    draft.status,
                    self._serialize_slots(draft.slots),
                    self._serialize_list(draft.missing_slots),
                    self._serialize_list(draft.invalid_slots),
                    self._serialize_schedule(draft.schedule),
                    1 if draft.is_cancelable else 0,
                    1 if draft.is_resumable else 0,
                    self._serialize_list(draft.original_utterances),
                    draft.created_at,
                    draft.updated_at
                ))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            self.pool.return_connection(conn)

    def get_draft(self, draft_id: str) -> Optional[TaskDraftDTO]:
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(self._ph('''
                SELECT draft_id, user_id, task_type, status, slots, missing_slots, invalid_slots,
                       schedule, is_cancelable, is_resumable, original_utterances,
                       created_at, updated_at
                FROM task_drafts
                WHERE draft_id = ?
            '''), (draft_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_draft(row)
            return None
        finally:
            self.pool.return_connection(conn)

    def delete_draft(self, draft_id: str) -> bool:
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(self._ph('''
                DELETE FROM task_drafts
                WHERE draft_id = ?
            '''), (draft_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            self.pool.return_connection(conn)

    def get_all_drafts(self) -> List[TaskDraftDTO]:
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT draft_id, user_id, task_type, status, slots, missing_slots, invalid_slots,
                       schedule, is_cancelable, is_resumable, original_utterances,
                       created_at, updated_at
                FROM task_drafts
                ORDER BY created_at DESC
            ''')
            rows = cursor.fetchall()
            return [self._row_to_draft(row) for row in rows]
        finally:
            self.pool.return_connection(conn)

    def update_draft_status(self, draft_id: str, status: str) -> bool:
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(self._ph('''
                UPDATE task_drafts
                SET status = ?, updated_at = ?
                WHERE draft_id = ?
            '''), (status, datetime.now().timestamp(), draft_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            self.pool.return_connection(conn)

    def get_drafts_by_status(self, status: str) -> List[TaskDraftDTO]:
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(self._ph('''
                SELECT draft_id, user_id, task_type, status, slots, missing_slots, invalid_slots,
                       schedule, is_cancelable, is_resumable, original_utterances,
                       created_at, updated_at
                FROM task_drafts
                WHERE status = ?
                ORDER BY created_at DESC
            '''), (status,))
            rows = cursor.fetchall()
            return [self._row_to_draft(row) for row in rows]
        finally:
            self.pool.return_connection(conn)
