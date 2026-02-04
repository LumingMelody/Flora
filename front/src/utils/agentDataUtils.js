/**
 * 用于将后端 Agent 数据转换为前端所需格式的工具函数
 */

/**
 * 计算已耗时（毫秒）
 * 优先使用 metrics.elapsed_seconds，否则根据 start_time 计算
 * @param {Object} runtime_state - 运行时状态
 * @returns {number} 已耗时（毫秒）
 */
function calculateElapsedMs(runtime_state) {
  if (!runtime_state) return 0;

  const currentTask = runtime_state.current_task;
  if (!currentTask) return 0;

  // 优先使用后端计算好的 elapsed_seconds
  if (currentTask.metrics?.elapsed_seconds) {
    return currentTask.metrics.elapsed_seconds * 1000;
  }

  // 否则根据 start_time 计算
  if (currentTask.start_time) {
    const startTime = currentTask.start_time * 1000; // 后端是秒级时间戳
    const now = Date.now();
    return Math.max(0, now - startTime);
  }

  return 0;
}

/**
 * 从状态标签获取对应的颜色
 * @param {string} statusLabel - 状态标签：IDLE、BUSY、OFFLINE
 * @returns {string} 对应的颜色代码
 */
function getStatusColor(statusLabel) {
  switch (statusLabel) {
    case 'IDLE':
      return '#4ade80';
    case 'BUSY':
      return '#FFA500';
    case 'OFFLINE':
      return '#f43f5e';
    default:
      return '#4ade80';
  }
}

/**
 * 从状态标签获取对应的图标
 * @param {string} statusLabel - 状态标签：IDLE、BUSY、OFFLINE
 * @returns {string} 对应的图标
 */
function getStatusIcon(statusLabel) {
  switch (statusLabel) {
    case 'IDLE':
      return '⏸️';
    case 'BUSY':
      return '🔄';
    case 'OFFLINE':
      return '🔴';
    default:
      return '⏸️';
  }
}

/**
 * 获取负载等级对应的颜色
 * @param {string} loadLevel - 负载等级：LOW、MEDIUM、HIGH
 * @returns {string} 对应的颜色代码
 */
function getLoadLevelColor(loadLevel) {
  switch (loadLevel) {
    case 'LOW':
      return '#4ade80';  // 绿色
    case 'MEDIUM':
      return '#fbbf24';  // 黄色
    case 'HIGH':
      return '#f43f5e';  // 红色
    default:
      return '#6b7280';  // 灰色
  }
}

/**
 * 计算节点的位置
 * @param {number} index - 节点在同级中的索引
 * @param {number} totalSiblings - 同级节点总数
 * @param {number} parentX - 父节点X坐标
 * @param {number} parentY - 父节点Y坐标
 * @param {number} depth - 当前节点深度
 * @returns {{x: number, y: number}} 计算出的位置
 */
function calculateNodePosition(index, totalSiblings, parentX, parentY, depth) {
  const verticalSpacing = 400;
  const horizontalSpacing = 400;

  // 计算水平偏移量，使子节点均匀分布在父节点下方
  const offset = (totalSiblings - 1) * horizontalSpacing / 2;
  const x = parentX + (index * horizontalSpacing) - offset;
  const y = parentY + verticalSpacing;

  return { x, y };
}

/**
 * 将后端Agent数据映射为前端NodeData结构
 * @param {Object} agent - 后端Agent数据
 * @param {number} x - 节点X坐标
 * @param {number} y - 节点Y坐标
 * @param {number} depth - 节点深度
 * @param {string} parentId - 父节点ID
 * @param {Object} monitorMetrics - 可选的监控指标数据（来自 /agents/{id}/metrics）
 * @returns {Object} 前端NodeData结构
 */
function mapToNodeData(agent, x, y, depth = 0, parentId = null, monitorMetrics = null) {
  // 使用可选链和默认值确保数据完整性
  const { agent_id, meta = {}, runtime_state = {}, children = [] } = agent;

  // 基础数据结构
  const nodeData = {
    agentId: agent_id,
    id: agent_id,
    label: meta.name || 'Unnamed',
    type: meta.type || 'Unknown',
    meta: {
      type: meta.type || 'Unknown',
      is_leaf: meta.is_leaf ?? false,
      weight: meta.weight ?? 0,
      description: meta.description || ''
    },
    runtime: {
      is_alive: runtime_state.is_alive ?? false,
      status_label: runtime_state.status_label || 'UNKNOWN',
      last_seen_seconds_ago: runtime_state.last_seen_seconds_ago ?? 0,
      current_task: runtime_state.current_task ? {
        task_id: runtime_state.current_task.task_id,
        trace_id: runtime_state.current_task.trace_id,
        name: runtime_state.current_task.name,
        step: runtime_state.current_task.step,
        reported_at: runtime_state.current_task.reported_at
      } : undefined,
      last_completed_task: runtime_state.last_completed_task ? {
        task_id: runtime_state.last_completed_task.task_id,
        status: runtime_state.last_completed_task.status,
        end_time: runtime_state.last_completed_task.end_time,
        duration: runtime_state.last_completed_task.duration
      } : undefined
    },
    visual: {
      // 从 current_task 中提取进度信息
      progress: runtime_state.current_task?.progress ?? 0,
      // 从 current_task.metrics 中提取已耗时（秒转毫秒），或根据 start_time 计算
      timeElapsedMs: calculateElapsedMs(runtime_state),
      statusColor: getStatusColor(runtime_state.status_label || 'UNKNOWN'),
      statusIcon: getStatusIcon(runtime_state.status_label || 'UNKNOWN'),
      // 额外的指标信息
      estimatedRemainingMs: (runtime_state.current_task?.metrics?.estimated_remaining_seconds ?? 0) * 1000,
      isOvertime: runtime_state.current_task?.metrics?.is_overtime ?? false
    },
    // 监控指标（默认值）
    monitor: {
      // 负载指标
      load: {
        queueDepth: 0,
        loadLevel: 'LOW',
        loadLevelColor: getLoadLevelColor('LOW')
      },
      // 性能指标
      performance: {
        todayCompleted: 0,
        todaySuccess: 0,
        todayFailed: 0,
        successRate: 0,
        avgDurationMs: 0
      },
      // 健康指标
      health: {
        recentFailures: 0,
        consecutiveFailures: 0,
        isHealthy: true
      }
    },
    childrenCount: children.length,
    depth: depth,
    parentId: parentId,
    traceId: runtime_state.current_task?.trace_id || '',
    position: { x, y }
  };

  // 如果有监控指标数据，合并进去
  if (monitorMetrics) {
    nodeData.monitor = {
      load: {
        queueDepth: monitorMetrics.load?.queue_depth ?? 0,
        loadLevel: monitorMetrics.load?.load_level ?? 'LOW',
        loadLevelColor: getLoadLevelColor(monitorMetrics.load?.load_level ?? 'LOW'),
        nextTasks: monitorMetrics.load?.next_tasks ?? []
      },
      performance: {
        todayCompleted: monitorMetrics.performance?.today_completed ?? 0,
        todaySuccess: monitorMetrics.performance?.today_success ?? 0,
        todayFailed: monitorMetrics.performance?.today_failed ?? 0,
        successRate: monitorMetrics.performance?.success_rate ?? 0,
        avgDurationMs: monitorMetrics.performance?.avg_duration_ms ?? 0
      },
      health: {
        recentFailures: monitorMetrics.health?.recent_failures ?? 0,
        consecutiveFailures: monitorMetrics.health?.consecutive_failures ?? 0,
        isHealthy: monitorMetrics.health?.is_healthy ?? true
      }
    };

    // 如果有实时指标，覆盖 visual 中的数据（更准确）
    if (monitorMetrics.realtime) {
      nodeData.visual.progress = monitorMetrics.realtime.task_progress ?? nodeData.visual.progress;
      nodeData.visual.timeElapsedMs = monitorMetrics.realtime.task_elapsed_ms ?? nodeData.visual.timeElapsedMs;
      nodeData.visual.estimatedRemainingMs = monitorMetrics.realtime.task_eta_ms ?? nodeData.visual.estimatedRemainingMs;
      nodeData.visual.isOvertime = monitorMetrics.realtime.is_overtime ?? nodeData.visual.isOvertime;

      // 更新当前任务信息
      if (monitorMetrics.realtime.current_task) {
        nodeData.runtime.current_task = {
          ...nodeData.runtime.current_task,
          ...monitorMetrics.realtime.current_task
        };
      }
    }
  }

  return nodeData;
}

/**
 * 递归处理树形结构，计算所有节点的位置和深度
 * @param {Object} agentTree - 后端Agent树数据
 * @param {number} rootX - 根节点X坐标
 * @param {number} rootY - 根节点Y坐标
 * @param {Object} metricsMap - 可选的监控指标映射（agent_id -> metrics）
 * @returns {{nodes: Array, edges: Array}} 前端节点和边数据
 */
function processAgentTree(agentTree, rootX = 200, rootY = 50, metricsMap = null) {
  const nodes = [];
  const edges = [];

  // 递归处理节点
  function recursiveProcess(agent, parentPosition, depth, parentId = null) {
    const { x, y } = parentPosition;

    // 获取该 agent 的监控指标
    const agentMetrics = metricsMap ? metricsMap[agent.agent_id] : null;

    // 创建前端节点
    const nodeId = `node-${agent.agent_id}`;
    const node = mapToNodeData(agent, x, y, depth, parentId, agentMetrics);
    nodes.push({
      id: nodeId,
      type: 'tree',
      position: { x, y },
      data: node
    });

    // 如果有父节点，创建边
    if (parentId) {
      edges.push({
        id: `e${parentId}-${nodeId}`,
        source: parentId,
        target: nodeId,
        animated: true,
        style: { stroke: '#4ade80' }
      });
    }

    // 处理子节点
    const children = agent.children || [];
    children.forEach((child, index) => {
      const childPosition = calculateNodePosition(
        index,
        children.length,
        x,
        y,
        depth + 1
      );
      recursiveProcess(child, childPosition, depth + 1, nodeId);
    });
  }

  // 开始处理根节点
  recursiveProcess(agentTree, { x: rootX, y: rootY }, 0);

  return { nodes, edges };
}

/**
 * 从树中提取所有 agent_id
 * @param {Object} agentTree - Agent 树数据
 * @returns {Array<string>} agent_id 列表
 */
function extractAgentIds(agentTree) {
  const ids = [];

  function collect(node) {
    if (node.agent_id) {
      ids.push(node.agent_id);
    }
    if (node.children) {
      node.children.forEach(collect);
    }
  }

  collect(agentTree);
  return ids;
}

export {
  mapToNodeData,
  processAgentTree,
  extractAgentIds,
  getStatusColor,
  getStatusIcon,
  getLoadLevelColor
};
