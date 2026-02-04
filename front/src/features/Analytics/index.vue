<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import GlassCard from '@/components/ui/GlassCard.vue';

// API 基础 URL
const EVENTS_API_BASE_URL = '/api/events';

// ==================== 类型定义 ====================

interface SystemOverview {
  total_agents: number;
  online_agents: number;
  offline_agents: number;
  running_traces: number;
  pending_tasks: number;
  today_total_tasks: number;
  today_success_tasks: number;
  today_failed_tasks: number;
  success_rate: number;
  avg_duration_ms: number | null;
}

interface TrendData {
  dates: string[];
  total_tasks: number[];
  success_tasks: number[];
  failed_tasks: number[];
  success_rates: number[];
}

interface TopAgent {
  agent_id: string;
  total_tasks: number;
  success_tasks: number;
  failed_tasks: number;
  success_rate: number;
  avg_duration_ms: number | null;
}

interface RecentTrace {
  trace_id: string;
  status: string;
  total_tasks: number;
  status_distribution: {
    pending: number;
    running: number;
    success: number;
    failed: number;
    cancelled: number;
  };
  max_depth: number;
  duration_ms: number | null;
  created_at: string | null;
}

// ==================== 状态 ====================

const loading = ref(true);
const error = ref<string | null>(null);

const systemOverview = ref<SystemOverview | null>(null);
const trendData = ref<TrendData | null>(null);
const topAgents = ref<TopAgent[]>([]);
const recentTraces = ref<RecentTrace[]>([]);

// ==================== API 调用 ====================

async function fetchData(url: string) {
  const response = await fetch(`${EVENTS_API_BASE_URL}${url}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

async function loadAllData() {
  loading.value = true;
  error.value = null;

  try {
    const [overview, trend, agents, traces] = await Promise.all([
      fetchData('/api/v1/stats/system/overview'),
      fetchData('/api/v1/stats/system/trend?days=7'),
      fetchData('/api/v1/stats/system/top-agents?limit=5&days=7'),
      fetchData('/api/v1/stats/traces/recent?limit=5'),
    ]);

    systemOverview.value = overview;
    trendData.value = trend;
    topAgents.value = agents;
    recentTraces.value = traces;
  } catch (e) {
    console.error('Failed to load analytics data:', e);
    error.value = e instanceof Error ? e.message : 'Unknown error';
  } finally {
    loading.value = false;
  }
}

// ==================== 计算属性 ====================

const agentStatusPercent = computed(() => {
  if (!systemOverview.value) return { online: 0, offline: 0 };
  const total = systemOverview.value.total_agents || 1;
  return {
    online: Math.round((systemOverview.value.online_agents / total) * 100),
    offline: Math.round((systemOverview.value.offline_agents / total) * 100),
  };
});

// ==================== 格式化函数 ====================

function formatDuration(ms: number | null): string {
  if (!ms) return '-';
  const seconds = ms / 1000;
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const minutes = seconds / 60;
  if (minutes < 60) return `${minutes.toFixed(1)}m`;
  const hours = minutes / 60;
  return `${hours.toFixed(1)}h`;
}

function formatTime(isoString: string | null): string {
  if (!isoString) return '-';
  const date = new Date(isoString);
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'RUNNING':
      return 'text-teal-400';
    case 'SUCCESS':
    case 'COMPLETED':
      return 'text-emerald-400';
    case 'FAILED':
      return 'text-rose-400';
    case 'CANCELLED':
      return 'text-gray-400';
    default:
      return 'text-amber-400';
  }
}

function getSuccessRateColor(rate: number): string {
  if (rate >= 90) return 'text-emerald-400';
  if (rate >= 70) return 'text-amber-400';
  return 'text-rose-400';
}

// ==================== 生命周期 ====================

onMounted(() => {
  loadAllData();
});
</script>

<template>
  <div class="h-full overflow-auto p-6 space-y-6">
    <!-- 加载状态 -->
    <div v-if="loading" class="h-full flex items-center justify-center">
      <div class="text-center">
        <div class="w-12 h-12 border-4 border-teal-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-400">加载统计数据中...</p>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="h-full flex items-center justify-center">
      <div class="text-center">
        <div class="text-rose-400 text-4xl mb-4">⚠️</div>
        <p class="text-rose-400 mb-2">加载失败</p>
        <p class="text-gray-500 text-sm mb-4">{{ error }}</p>
        <button
          @click="loadAllData"
          class="px-4 py-2 bg-teal-500/20 text-teal-400 rounded-lg hover:bg-teal-500/30 transition"
        >
          重试
        </button>
      </div>
    </div>

    <!-- 主内容 -->
    <template v-else>
      <!-- 页面标题 -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-white">系统分析</h1>
          <p class="text-gray-500 text-sm mt-1">实时监控系统运行状态和性能指标</p>
        </div>
        <button
          @click="loadAllData"
          class="px-4 py-2 bg-white/5 text-gray-400 rounded-lg hover:bg-white/10 transition flex items-center gap-2"
        >
          <span>🔄</span>
          <span>刷新</span>
        </button>
      </div>

      <!-- 系统总览卡片 -->
      <div class="grid grid-cols-4 gap-4">
        <!-- Agent 状态 -->
        <GlassCard class="p-4">
          <div class="text-gray-400 text-xs mb-2">Agent 状态</div>
          <div class="flex items-baseline gap-2">
            <span class="text-3xl font-bold text-white">{{ systemOverview?.total_agents || 0 }}</span>
            <span class="text-gray-500 text-sm">个 Agent</span>
          </div>
          <div class="flex items-center gap-4 mt-3 text-sm">
            <span class="text-emerald-400">● {{ systemOverview?.online_agents || 0 }} 在线</span>
            <span class="text-gray-500">● {{ systemOverview?.offline_agents || 0 }} 离线</span>
          </div>
          <div class="mt-3 h-2 bg-white/10 rounded-full overflow-hidden flex">
            <div
              class="h-full bg-emerald-400"
              :style="{ width: `${agentStatusPercent.online}%` }"
            ></div>
            <div
              class="h-full bg-gray-600"
              :style="{ width: `${agentStatusPercent.offline}%` }"
            ></div>
          </div>
        </GlassCard>

        <!-- 运行中任务 -->
        <GlassCard class="p-4">
          <div class="text-gray-400 text-xs mb-2">运行中</div>
          <div class="flex items-baseline gap-2">
            <span class="text-3xl font-bold text-teal-400">{{ systemOverview?.running_traces || 0 }}</span>
            <span class="text-gray-500 text-sm">个 Trace</span>
          </div>
          <div class="flex items-center gap-4 mt-3 text-sm">
            <span class="text-amber-400">{{ systemOverview?.pending_tasks || 0 }} 待处理</span>
          </div>
        </GlassCard>

        <!-- 今日完成 -->
        <GlassCard class="p-4">
          <div class="text-gray-400 text-xs mb-2">今日任务</div>
          <div class="flex items-baseline gap-2">
            <span class="text-3xl font-bold text-white">{{ systemOverview?.today_total_tasks || 0 }}</span>
            <span class="text-gray-500 text-sm">个任务</span>
          </div>
          <div class="flex items-center gap-4 mt-3 text-sm">
            <span class="text-emerald-400">✓ {{ systemOverview?.today_success_tasks || 0 }}</span>
            <span class="text-rose-400">✗ {{ systemOverview?.today_failed_tasks || 0 }}</span>
          </div>
        </GlassCard>

        <!-- 成功率 -->
        <GlassCard class="p-4">
          <div class="text-gray-400 text-xs mb-2">今日成功率</div>
          <div class="flex items-baseline gap-2">
            <span
              class="text-3xl font-bold"
              :class="getSuccessRateColor(systemOverview?.success_rate || 0)"
            >
              {{ systemOverview?.success_rate || 0 }}%
            </span>
          </div>
          <div class="flex items-center gap-4 mt-3 text-sm text-gray-500">
            <span>平均耗时: {{ formatDuration(systemOverview?.avg_duration_ms || null) }}</span>
          </div>
        </GlassCard>
      </div>

      <!-- 趋势图和排行榜 -->
      <div class="grid grid-cols-3 gap-4">
        <!-- 7天趋势 -->
        <GlassCard class="col-span-2 p-4">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-white font-medium">最近 7 天趋势</h3>
          </div>

          <!-- 简易柱状图 -->
          <div class="h-48 flex items-end justify-between gap-2">
            <div
              v-for="(date, index) in trendData?.dates || []"
              :key="date"
              class="flex-1 flex flex-col items-center gap-1"
            >
              <!-- 柱子 -->
              <div class="w-full flex flex-col items-center gap-0.5" style="height: 160px;">
                <div class="w-full flex-1 flex flex-col justify-end gap-0.5">
                  <!-- 失败 -->
                  <div
                    v-if="trendData?.failed_tasks[index]"
                    class="w-full bg-rose-500/60 rounded-t"
                    :style="{
                      height: `${Math.max(4, (trendData?.failed_tasks[index] || 0) / Math.max(...(trendData?.total_tasks || [1])) * 100)}%`
                    }"
                  ></div>
                  <!-- 成功 -->
                  <div
                    class="w-full bg-emerald-500/60 rounded-t"
                    :style="{
                      height: `${Math.max(4, (trendData?.success_tasks[index] || 0) / Math.max(...(trendData?.total_tasks || [1])) * 100)}%`
                    }"
                  ></div>
                </div>
              </div>
              <!-- 日期标签 -->
              <div class="text-[10px] text-gray-500 mt-1">
                {{ date.slice(5) }}
              </div>
              <!-- 数量标签 -->
              <div class="text-[10px] text-gray-400">
                {{ trendData?.total_tasks[index] || 0 }}
              </div>
            </div>
          </div>

          <!-- 图例 -->
          <div class="flex items-center justify-center gap-6 mt-4 text-xs">
            <span class="flex items-center gap-1">
              <span class="w-3 h-3 bg-emerald-500/60 rounded"></span>
              <span class="text-gray-400">成功</span>
            </span>
            <span class="flex items-center gap-1">
              <span class="w-3 h-3 bg-rose-500/60 rounded"></span>
              <span class="text-gray-400">失败</span>
            </span>
          </div>
        </GlassCard>

        <!-- Top Agents -->
        <GlassCard class="p-4">
          <h3 class="text-white font-medium mb-4">活跃 Agent 排行</h3>
          <div class="space-y-3">
            <div
              v-for="(agent, index) in topAgents"
              :key="agent.agent_id"
              class="flex items-center gap-3 p-2 bg-white/5 rounded-lg"
            >
              <!-- 排名 -->
              <div
                class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                :class="{
                  'bg-amber-500/20 text-amber-400': index === 0,
                  'bg-gray-500/20 text-gray-400': index === 1,
                  'bg-orange-800/20 text-orange-400': index === 2,
                  'bg-white/5 text-gray-500': index > 2
                }"
              >
                {{ index + 1 }}
              </div>
              <!-- Agent 信息 -->
              <div class="flex-1 min-w-0">
                <div class="text-sm text-white truncate">{{ agent.agent_id }}</div>
                <div class="text-[10px] text-gray-500">
                  {{ agent.total_tasks }} 任务 · {{ formatDuration(agent.avg_duration_ms) }}
                </div>
              </div>
              <!-- 成功率 -->
              <div
                class="text-sm font-medium"
                :class="getSuccessRateColor(agent.success_rate)"
              >
                {{ agent.success_rate }}%
              </div>
            </div>

            <div v-if="topAgents.length === 0" class="text-center text-gray-500 py-4">
              暂无数据
            </div>
          </div>
        </GlassCard>
      </div>

      <!-- 最近 Trace -->
      <GlassCard class="p-4">
        <h3 class="text-white font-medium mb-4">最近 Trace</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-gray-500 text-left">
                <th class="pb-3 font-medium">Trace ID</th>
                <th class="pb-3 font-medium">状态</th>
                <th class="pb-3 font-medium">任务数</th>
                <th class="pb-3 font-medium">状态分布</th>
                <th class="pb-3 font-medium">深度</th>
                <th class="pb-3 font-medium">耗时</th>
                <th class="pb-3 font-medium">创建时间</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="trace in recentTraces"
                :key="trace.trace_id"
                class="border-t border-white/5"
              >
                <td class="py-3 font-mono text-gray-300">{{ trace.trace_id.slice(0, 8) }}...</td>
                <td class="py-3">
                  <span :class="getStatusColor(trace.status)">{{ trace.status }}</span>
                </td>
                <td class="py-3 text-gray-300">{{ trace.total_tasks }}</td>
                <td class="py-3">
                  <div class="flex items-center gap-1 text-[10px]">
                    <span v-if="trace.status_distribution.success" class="text-emerald-400">
                      ✓{{ trace.status_distribution.success }}
                    </span>
                    <span v-if="trace.status_distribution.running" class="text-teal-400">
                      ▶{{ trace.status_distribution.running }}
                    </span>
                    <span v-if="trace.status_distribution.pending" class="text-amber-400">
                      ○{{ trace.status_distribution.pending }}
                    </span>
                    <span v-if="trace.status_distribution.failed" class="text-rose-400">
                      ✗{{ trace.status_distribution.failed }}
                    </span>
                  </div>
                </td>
                <td class="py-3 text-gray-400">{{ trace.max_depth }}</td>
                <td class="py-3 text-gray-400">{{ formatDuration(trace.duration_ms) }}</td>
                <td class="py-3 text-gray-500">{{ formatTime(trace.created_at) }}</td>
              </tr>

              <tr v-if="recentTraces.length === 0">
                <td colspan="7" class="py-8 text-center text-gray-500">暂无数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </GlassCard>
    </template>
  </div>
</template>

<style scoped>
/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
