<script setup lang="ts">
import { computed, ref } from 'vue';
import { Handle, Position } from '@vue-flow/core';

interface CurrentTask {
  task_id: string;
  trace_id: string;
  name?: string;
  step: string;
  reported_at: number;
}

interface Runtime {
  is_alive: boolean;
  status_label: string;
  last_seen_seconds_ago: number;
  current_task?: CurrentTask;
}

interface Meta {
  type: string;
  is_leaf: boolean;
  weight: number;
  description: string;
}

interface Visual {
  progress: number;
  timeElapsedMs: number;
  statusIcon?: string;
  statusColor?: string;
  estimatedRemainingMs?: number;
  isOvertime?: boolean;
}

interface MonitorLoad {
  queueDepth: number;
  loadLevel: string;
  loadLevelColor: string;
}

interface MonitorPerformance {
  todayCompleted: number;
  todaySuccess: number;
  todayFailed: number;
  successRate: number;
  avgDurationMs: number;
}

interface MonitorHealth {
  recentFailures: number;
  consecutiveFailures: number;
  isHealthy: boolean;
}

interface Monitor {
  load: MonitorLoad;
  performance: MonitorPerformance;
  health: MonitorHealth;
}

interface NodeData {
  agentId: string;
  id: string;
  label: string;
  type: string;
  meta: Meta;
  runtime: Runtime;
  visual: Visual;
  monitor?: Monitor;
  childrenCount: number;
  depth: number;
  traceId: string;
}

const props = defineProps<{
  data: NodeData;
  selected: boolean;
  class?: string;
}>();

// ===== 状态计算 =====
const status = computed(() => props.data.runtime?.status_label || 'UNKNOWN');
const isRunning = computed(() => status.value === 'BUSY');
const isFailed = computed(() => status.value === 'ERROR');
const isKilled = computed(() => status.value === 'KILLED');
const isSuccess = computed(() => status.value === 'SUCCESS');
const isAlive = computed(() => props.data.runtime?.is_alive ?? false);
const isIdle = computed(() => status.value === 'IDLE');

// ===== 监控指标 =====
const monitor = computed(() => props.data.monitor);
const loadLevel = computed(() => monitor.value?.load?.loadLevel ?? 'LOW');
const loadLevelColor = computed(() => monitor.value?.load?.loadLevelColor ?? '#4ade80');
const queueDepth = computed(() => monitor.value?.load?.queueDepth ?? 0);
const todayCompleted = computed(() => monitor.value?.performance?.todayCompleted ?? 0);
const successRate = computed(() => monitor.value?.performance?.successRate ?? 0);
const avgDurationMs = computed(() => monitor.value?.performance?.avgDurationMs ?? 0);
const isHealthy = computed(() => monitor.value?.health?.isHealthy ?? true);
const consecutiveFailures = computed(() => monitor.value?.health?.consecutiveFailures ?? 0);

// ===== 进度 & 时间 =====
const progress = computed(() => props.data.visual?.progress ?? 0);
const timeElapsedMs = computed(() => props.data.visual?.timeElapsedMs ?? 0);
const estimatedRemainingMs = computed(() => props.data.visual?.estimatedRemainingMs ?? 0);
const isOvertime = computed(() => props.data.visual?.isOvertime ?? false);
const progressStyle = computed(() => ({ width: `${progress.value}%` }));
const loadBarStyle = computed(() => {
  const depth = queueDepth.value;
  const percent = Math.min(100, depth * 10); // 10个任务 = 100%
  return { width: `${percent}%` };
});

// ===== 格式化函数 =====
const formatDuration = (ms: number): string => {
  if (!ms || ms <= 0) return '0s';
  const seconds = Math.floor(ms / 1000);
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  if (minutes < 60) return `${minutes}m ${remainingSeconds}s`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes}m`;
};

const formatAvgDuration = (ms: number): string => {
  if (!ms || ms <= 0) return '0s';
  const seconds = ms / 1000;
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const minutes = seconds / 60;
  return `${minutes.toFixed(1)}m`;
};

const elapsedDisplay = computed(() => formatDuration(timeElapsedMs.value));
const remainingDisplay = computed(() => {
  if (!isRunning.value || estimatedRemainingMs.value <= 0) return '';
  return `ETA: ${formatDuration(estimatedRemainingMs.value)}`;
});

const formatTime = (timestamp: number): string => {
  if (!timestamp) return '—';
  const date = new Date(timestamp);
  return date.toLocaleTimeString();
};

// ===== 折叠控制 =====
const showTask = ref(false);
const showMeta = ref(false);

// ===== 子节点数 =====
const childrenCount = computed(() => props.data.childrenCount || 0);

// ===== 当前任务名称 =====
const currentTaskName = computed(() => {
  return props.data.runtime?.current_task?.name || props.data.runtime?.current_task?.step || 'Processing...';
});
</script>

<template>
  <div
    class="glass-card w-[320px] p-4 relative group overflow-hidden"
    :class="{
      'selected': selected,
      'card-killed': isKilled,
      'status-running': isRunning,
      'status-success': isSuccess,
      'status-failed': isFailed,
      'status-unhealthy': !isHealthy
    }"
  >
    <Handle type="target" :position="Position.Top" class="!opacity-0 !w-full !h-4 !top-0" />

    <!-- Header -->
    <div class="flex justify-between items-start mb-3">
      <div class="flex flex-col">
        <span class="text-xs font-medium text-gray-400 tracking-wide uppercase">
          {{ data.meta?.type || data.type }}
        </span>
        <h3 class="text-sm font-bold text-white leading-tight mt-0.5 max-w-[180px] truncate">
          {{ data.label }}
        </h3>
        <div class="text-[10px] text-gray-500 mt-1">
          Agent: {{ data.agentId }}
        </div>
      </div>

      <div class="px-2 py-1 rounded-full bg-white/5 border border-white/10 text-[10px] text-gray-400 backdrop-blur-md whitespace-nowrap">
        #{{ data.id }}
      </div>
    </div>

    <!-- Status Line -->
    <div class="flex items-center gap-2 text-[11px] text-gray-300 mb-3">
      <span :class="{
        'text-teal-400': isRunning,
        'text-rose-500': isFailed || !isHealthy,
        'text-emerald-400': isSuccess || isIdle,
        'text-amber-500': !isRunning && !isFailed && !isSuccess && !isIdle
      }">
        {{ status }}
      </span>
      <span v-if="!isAlive" class="text-rose-400">● OFFLINE</span>
      <span v-else class="text-green-400">● LIVE</span>
      <span v-if="data.runtime?.last_seen_seconds_ago !== undefined" class="text-gray-500">
        ({{ data.runtime.last_seen_seconds_ago }}s ago)
      </span>
      <!-- 健康警告 -->
      <span v-if="!isHealthy" class="text-rose-400 text-[10px]">⚠️ {{ consecutiveFailures }} fails</span>
    </div>

    <!-- Performance Metrics (三列指标) -->
    <div class="grid grid-cols-3 gap-2 mb-3">
      <div class="bg-white/5 rounded-lg p-2 text-center">
        <div class="text-lg font-bold text-white">{{ todayCompleted }}</div>
        <div class="text-[9px] text-gray-500">今日完成</div>
      </div>
      <div class="bg-white/5 rounded-lg p-2 text-center">
        <div class="text-lg font-bold" :class="successRate >= 90 ? 'text-emerald-400' : successRate >= 70 ? 'text-amber-400' : 'text-rose-400'">
          {{ successRate }}%
        </div>
        <div class="text-[9px] text-gray-500">成功率</div>
      </div>
      <div class="bg-white/5 rounded-lg p-2 text-center">
        <div class="text-lg font-bold text-white">{{ formatAvgDuration(avgDurationMs) }}</div>
        <div class="text-[9px] text-gray-500">平均耗时</div>
      </div>
    </div>

    <!-- Load Indicator (队列负载) -->
    <div class="mb-3">
      <div class="flex justify-between items-center text-[10px] mb-1">
        <span class="text-gray-400">队列: {{ queueDepth }} 个待处理</span>
        <span :style="{ color: loadLevelColor }" class="font-medium">{{ loadLevel }}</span>
      </div>
      <div class="relative h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
        <div
          class="absolute top-0 left-0 h-full rounded-full transition-all duration-500"
          :style="{ ...loadBarStyle, backgroundColor: loadLevelColor }"
        ></div>
      </div>
    </div>

    <!-- Current Task Section -->
    <div v-if="isRunning && data.runtime?.current_task" class="mb-3 bg-teal-500/10 border border-teal-500/20 rounded-lg p-2">
      <div class="text-[10px] text-gray-400 mb-1">当前任务</div>
      <div class="text-[11px] text-white font-medium truncate">{{ currentTaskName }}</div>

      <!-- Task Progress -->
      <div class="mt-2">
        <div class="flex justify-between items-center text-[10px] mb-1">
          <span class="text-teal-400">{{ progress }}%</span>
          <div class="flex items-center gap-2">
            <span class="text-gray-500">{{ elapsedDisplay }}</span>
            <span v-if="remainingDisplay" class="text-teal-400">{{ remainingDisplay }}</span>
            <span v-if="isOvertime" class="text-rose-400 font-medium">OVERTIME</span>
          </div>
        </div>
        <div class="relative h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
          <div
            class="absolute top-0 left-0 h-full rounded-full transition-all duration-700 ease-out"
            :class="isOvertime ? 'bg-rose-500' : 'bg-teal-400'"
            :style="progressStyle"
          ></div>
        </div>
      </div>
    </div>

    <!-- Idle State -->
    <div v-else-if="isIdle" class="mb-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-2 text-center">
      <div class="text-[11px] text-emerald-400">空闲中，等待任务...</div>
    </div>

    <!-- Current Task Details (Collapsible) -->
    <div v-if="data.runtime?.current_task" class="mb-3">
      <div
        class="flex justify-between items-center text-[11px] font-medium text-gray-400 cursor-pointer"
        @click="showTask = !showTask"
      >
        <span>任务详情</span>
        <span>{{ showTask ? '▲' : '▼' }}</span>
      </div>
      <div v-show="showTask" class="text-[10px] text-gray-300 mt-1 space-y-1 bg-black/20 p-2 rounded">
        <div>Task ID: <span class="font-mono">{{ data.runtime.current_task.task_id }}</span></div>
        <div>Step: {{ data.runtime.current_task.step }}</div>
        <div>Trace: <span class="font-mono">{{ data.runtime.current_task.trace_id }}</span></div>
        <div>Reported: {{ formatTime(data.runtime.current_task.reported_at) }}</div>
      </div>
    </div>

    <!-- Meta Info (Collapsible) -->
    <div class="mb-3">
      <div
        class="flex justify-between items-center text-[11px] font-medium text-gray-400 cursor-pointer"
        @click="showMeta = !showMeta"
      >
        <span>Meta Info</span>
        <span>{{ showMeta ? '▲' : '▼' }}</span>
      </div>
      <div v-show="showMeta" class="text-[10px] text-gray-300 mt-1 space-y-1 bg-black/20 p-2 rounded">
        <div v-if="data.meta?.description">Desc: {{ data.meta.description }}</div>
        <div>Leaf: {{ data.meta?.is_leaf ? 'Yes' : 'No' }}</div>
        <div>Weight: {{ data.meta?.weight }}</div>
        <div>Depth: {{ data.depth }}</div>
        <div>Children: {{ childrenCount }}</div>
        <div>Trace ID: <span class="font-mono">{{ data.traceId }}</span></div>
      </div>
    </div>

    <!-- Footer -->
    <div class="flex items-center justify-between pt-2 border-t border-white/5">
      <div class="flex -space-x-2">
        <div class="w-5 h-5 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 border border-[#1e1e23]"></div>
        <div class="w-5 h-5 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 border border-[#1e1e23]"></div>
        <div v-if="childrenCount > 0" class="w-5 h-5 rounded-full bg-[#2a2a30] border border-[#1e1e23] flex items-center justify-center text-[7px] text-gray-400">
          +{{ childrenCount }}
        </div>
      </div>
    </div>

    <!-- Killed Overlay -->
    <div v-if="isKilled" class="absolute inset-0 bg-black/60 backdrop-blur-[1px] z-10 flex items-center justify-center">
      <span class="text-rose-500 font-bold tracking-widest border border-rose-500/30 px-3 py-1 rounded bg-rose-500/10">TERMINATED</span>
    </div>

    <Handle type="source" :position="Position.Bottom" class="!opacity-0 !w-full !h-4 !bottom-0" />
  </div>
</template>

<style scoped>
.glass-card {
  background: rgba(30, 30, 35, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    0 20px 40px -10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.glass-card.selected {
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow:
    0 0 0 4px rgba(255, 255, 255, 0.05),
    0 20px 40px -10px rgba(0, 0, 0, 0.7);
  transform: translateY(-2px) scale(1.02);
}

.gradient-bar-success {
  background: linear-gradient(90deg, #4ade80 0%, #2dd4bf 50%, #3b82f6 100%);
  box-shadow: 0 0 20px rgba(45, 212, 191, 0.4);
}

.gradient-bar-failed {
  background: linear-gradient(90deg, #f87171 0%, #f43f5e 50%, #e11d48 100%);
  box-shadow: 0 0 20px rgba(244, 63, 94, 0.4);
}

.status-running {
  border-color: rgba(45, 212, 191, 0.5);
  box-shadow: 0 0 10px rgba(45, 212, 191, 0.2);
  animation: pulse-running 2s ease-in-out infinite;
}

.status-success {
  border-color: rgba(74, 222, 128, 0.5);
  box-shadow: 0 0 10px rgba(74, 222, 128, 0.2);
}

.status-failed {
  border-color: rgba(244, 63, 94, 0.5);
  box-shadow: 0 0 10px rgba(244, 63, 94, 0.2);
}

.status-unhealthy {
  border-color: rgba(244, 63, 94, 0.5);
  box-shadow: 0 0 15px rgba(244, 63, 94, 0.3);
}

.card-killed {
  filter: grayscale(1) brightness(0.5);
  border-color: rgba(255, 50, 50, 0.3);
  transform: scale(0.95);
}

@keyframes pulse-running {
  0%, 100% {
    box-shadow: 0 0 10px rgba(45, 212, 191, 0.2), 0 0 20px rgba(45, 212, 191, 0.1);
  }
  50% {
    box-shadow: 0 0 20px rgba(45, 212, 191, 0.4), 0 0 40px rgba(45, 212, 191, 0.2), 0 0 60px rgba(45, 212, 191, 0.1);
  }
}
</style>
