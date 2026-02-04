from typing import Dict, List
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    WebSocket连接管理器，用于管理前端的WebSocket连接
    核心职责：
    1. 维护trace_id到WebSocket连接列表的映射
    2. 处理连接的建立和断开
    3. 向特定trace的所有连接推送事件
    """
    def __init__(self):
        # 存储trace_id到WebSocket连接列表的映射
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, trace_id: str):
        """
        建立WebSocket连接，并将其添加到指定trace_id的连接列表中
        """
        await websocket.accept()
        if trace_id not in self.active_connections:
            self.active_connections[trace_id] = []
        self.active_connections[trace_id].append(websocket)
        logger.info(f"WebSocket connected for trace: {trace_id}, total connections: {len(self.active_connections[trace_id])}")

    def disconnect(self, websocket: WebSocket, trace_id: str):
        """
        断开WebSocket连接，并将其从连接列表中移除
        """
        if trace_id in self.active_connections:
            self.active_connections[trace_id].remove(websocket)
            logger.info(f"WebSocket disconnected for trace: {trace_id}, remaining: {len(self.active_connections[trace_id])}")
            # 如果该trace_id下没有连接了，清理该条目
            if not self.active_connections[trace_id]:
                del self.active_connections[trace_id]

    async def broadcast_to_trace(self, trace_id: str, message: dict):
        """
        向指定trace_id的所有连接推送消息
        """
        if trace_id in self.active_connections:
            connections = self.active_connections[trace_id]
            logger.info(f"Broadcasting to trace {trace_id}: {len(connections)} connections, event: {message.get('event')}")
            # 遍历连接列表，发送消息
            for websocket in list(connections):  # 使用 list() 复制，避免迭代时修改
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send message to WebSocket: {e}")
                    # 如果发送失败，将该连接从列表中移除
                    if websocket in self.active_connections.get(trace_id, []):
                        self.active_connections[trace_id].remove(websocket)
                    # 如果该trace_id下没有连接了，清理该条目
                    if trace_id in self.active_connections and not self.active_connections[trace_id]:
                        del self.active_connections[trace_id]
        else:
            logger.debug(f"No active connections for trace: {trace_id}, available traces: {list(self.active_connections.keys())[:5]}")
