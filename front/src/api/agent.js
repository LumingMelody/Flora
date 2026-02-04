// 导入数据转换工具
import { processAgentTree, extractAgentIds } from '../utils/agentDataUtils';

// API 基础 URL
const EVENTS_API_BASE_URL = '/api/events';

/**
 * 构建 WebSocket URL
 * @param {string} path - WebSocket 路径
 * @returns {string} 完整的 WebSocket URL
 */
function buildWebSocketUrl(path) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  return `${protocol}//${host}${path}`;
}

/**
 * 通用 HTTP 请求函数
 * @param {string} url - 请求 URL
 * @param {Object} options - 请求选项
 * @returns {Promise<any>} 响应数据
 */
async function request(url, options = {}) {
  const response = await fetch(`${EVENTS_API_BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

/**
 * Agent API 服务，用于处理与Agent相关的WebSocket连接和HTTP请求
 */
class AgentAPI {
  /**
   * 获取单个 Agent 的监控指标
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} 监控指标数据
   */
  static async getAgentMetrics(agentId) {
    return request(`/api/v1/traces/agents/${agentId}/metrics`);
  }

  /**
   * 批量获取多个 Agent 的监控指标
   * @param {Array<string>} agentIds - Agent ID 列表
   * @returns {Promise<Object>} 以 agent_id 为 key 的指标字典
   */
  static async getBatchAgentMetrics(agentIds) {
    return request('/api/v1/traces/agents/batch-metrics', {
      method: 'POST',
      body: JSON.stringify(agentIds),
    });
  }

  /**
   * 创建Agent树WebSocket连接（带监控指标）
   * @param {string} agentId - Agent ID
   * @param {Object} callbacks - 回调函数对象
   * @param {Function} callbacks.onOpen - 连接打开时的回调
   * @param {Function} callbacks.onMessage - 接收消息时的回调
   * @param {Function} callbacks.onError - 发生错误时的回调
   * @param {Function} callbacks.onClose - 连接关闭时的回调
   * @param {boolean} withMetrics - 是否同时获取监控指标（默认 true）
   * @returns {WebSocket} WebSocket实例
   */
  static createAgentTreeWebSocket(agentId, callbacks = {}, withMetrics = true) {
    const { onOpen, onMessage, onError, onClose } = callbacks;

    // 构建WebSocket URL: /api/events/ 会被 nginx 代理到 events:8000/
    const wsUrl = buildWebSocketUrl(`/api/events/api/v1/traces/ws/agent/${agentId}`);

    // 创建WebSocket连接
    const ws = new WebSocket(wsUrl);

    // 设置事件处理程序
    ws.onopen = (event) => {
      console.log(`WebSocket connected to agent ${agentId}`);
      if (onOpen) onOpen(event);
    };

    ws.onmessage = async (event) => {
      try {
        const rawData = JSON.parse(event.data);

        // 如果需要监控指标，先获取所有 agent 的指标
        let metricsMap = null;
        if (withMetrics) {
          try {
            const agentIds = extractAgentIds(rawData);
            if (agentIds.length > 0) {
              metricsMap = await AgentAPI.getBatchAgentMetrics(agentIds);
            }
          } catch (metricsError) {
            console.warn('Failed to fetch agent metrics:', metricsError);
            // 继续处理，不阻塞主流程
          }
        }

        // 将后端数据转换为前端所需格式，并合并监控指标
        const processedData = processAgentTree(rawData, 200, 50, metricsMap);

        // 调用回调函数并传递转换后的数据
        if (onMessage) onMessage(processedData);
      } catch (error) {
        console.error('Error parsing or processing WebSocket message:', error);
        if (onError) onError(error);
      }
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error for agent ${agentId}:`, error);
      if (onError) onError(error);
    };

    ws.onclose = (event) => {
      console.log(`WebSocket disconnected from agent ${agentId}`, event.code, event.reason);
      if (onClose) onClose(event);
    };

    return ws;
  }

  /**
   * 发送refresh指令到WebSocket连接
   * @param {WebSocket} ws - WebSocket实例
   */
  static refreshAgentTree(ws) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send('refresh');
    } else {
      console.error('WebSocket is not open, cannot send refresh command');
    }
  }

  /**
   * 关闭Agent树WebSocket连接
   * @param {WebSocket} ws - WebSocket实例
   */
  static closeAgentTreeWebSocket(ws) {
    if (ws) {
      ws.close();
    }
  }
}

export default AgentAPI;