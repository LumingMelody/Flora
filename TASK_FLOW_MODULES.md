# 任务创建/修改/调度流程：模块职责与可执行性清单

> 范围：以 `interaction/interaction_handler.py:stream_handle_user_input` 为主线，聚焦“任务能否被正确操控”（创建即时/定时/延迟/周期任务，以及修改/控制任务）。

## 流程总览（从输入到任务执行）
1. 用户输入 → 用户输入管理（规范化/补全）
2. 对话状态加载（DialogState）
3. 意图识别（CREATE / MODIFY / SET_SCHEDULE / CONTROL）
4. 任务草稿管理（收集参数/确认）
5. 确认后提交执行（TaskExecutionManager → TaskClient）

## 模块职责 & 可执行性判断

### 1) 交互编排器
- 位置：`interaction/interaction_handler.py` (`stream_handle_user_input`)
- 职责：
  - 统一路由意图（创建/修改/调度/控制）
  - 控制“待确认 → 执行”的门控
- 可执行性判断：
  - ✅ 创建/修改：能走到草稿与确认流程
  - ⚠️ 调度：`SET_SCHEDULE` 只更新草稿，未注册调度（见下）

### 2) 意图识别
- 位置：`interaction/capabilities/intent_recognition_manager/common_intent_recognition_manager.py`
- 职责：将用户话术识别为 CREATE / MODIFY / SET_SCHEDULE / CONTROL
- 可执行性判断：
  - ✅ 可识别意图（依赖 LLM 输出）

### 3) 任务草稿管理
- 位置：`interaction/capabilities/task_draft_manager/common_task_draft_manager.py`
- 职责：
  - 创建草稿、填槽、校验必填项
  - 生成待确认状态
  - 存储 schedule 信息（`draft.schedule`）
- 可执行性判断：
  - ✅ 即时任务创建/修改（基于草稿填槽与确认）
  - ⚠️ 调度任务仅存储 schedule，但不执行注册

### 4) 对话状态管理
- 位置：`interaction/capabilities/dialog_state_manager/common_dialog_state_manager.py`
- 职责：
  - 维护 active_task_draft / waiting_for_confirmation
  - 记录当前会话任务状态
- 可执行性判断：
  - ✅ 待确认与执行的门控状态正确

### 5) 任务执行管理
- 位置：`interaction/capabilities/task_execution_manager/common_task_execution_manager.py`
- 职责：
  - 提交任务到外部执行系统（TaskClient）
  - 管理执行上下文
- 可执行性判断：
  - ✅ 即时任务可提交（依赖 TaskClient 可用）
  - ❌ 未使用 `draft.schedule`，因此不支持定时/延迟/周期执行

### 6) 调度管理
- 位置：`interaction/capabilities/schedule_manager/common_schedule_manager.py`
- 职责：
  - 解析自然语言调度
  - 注册/更新/取消调度任务（TaskClient）
- 可执行性判断：
  - ⚠️ 模块存在，但 **未被 `stream_handle_user_input` 调用**
  - ❌ 实际调度注册/更新未接入主流程

### 7) 任务控制管理
- 位置：`interaction/capabilities/task_control_manager/common_task_control_manager.py`
- 职责：
  - 取消/暂停/恢复/重试/终止任务
- 可执行性判断：
  - ✅ 控制操作可走通（依赖 TaskClient 能力）
  - ❌ 不支持“修改运行中任务参数”

### 8) 外部任务系统（TaskClient）
- 位置：`interaction/external/client/task_client.py`
- 职责：
  - 实际执行、控制、调度
- 可执行性判断：
  - ✅/❌ 取决于外部服务是否可用、API 是否实现

## 任务类型支持矩阵（当前实现）

- **即时任务（立即执行）**
  - 创建：✅（草稿→确认→`execute_task`）
  - 修改草稿：✅（草稿填槽可重复更新）
  - 修改已执行任务参数：❌（未实现）

- **定时任务（指定时间执行）**
  - 解析时间：⚠️（ScheduleManager 支持，但未接入流程）
  - 注册执行：❌（`execute_task` 未使用 schedule）

- **延迟任务（延后执行）**
  - 同“定时任务”，属于 ONCE 调度类型
  - 当前：❌（未接入调度注册）

- **周期任务（重复执行）**
  - 解析周期：⚠️（ScheduleManager 支持 RECURRING）
  - 注册执行：❌（未接入调度注册）

- **任务控制（取消/暂停/恢复/重试/终止）**
  - 支持：✅（依赖 TaskClient）

## 关键缺口（导致“无法正确执行”）
1. `IntentType.SET_SCHEDULE` 分支仅更新草稿，没有调用 `schedule_manager.parse_schedule_expression` 或 `register_scheduled_task`。
2. `TaskExecutionManager.execute_task` 不读取 `draft.schedule`，因此不会触发定时/延迟/周期执行。
3. 缺少“修改已运行任务参数”的能力（仅有控制类操作）。

## 建议的可执行性验证
- **即时任务**：创建 → 确认 → 观察 TaskClient 是否被调用（日志/trace）。
- **定时/延迟/周期**：当前无法真实验证执行（流程未接入调度注册）。
- **控制操作**：对已运行任务执行 pause/resume/cancel，看 TaskClient 返回结果。

