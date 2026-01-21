    "description": ""
  },
  {
    "id": "user_strat_fission",
    "seq": "2",
    "name": " 用户分层裂变设计",
    "capabilities": "【用户场景】用户分层、设计裂变方案、做裂变活动、提高分享率、提高用户活跃度\n【核心能力】作为私域营销体系中精准裂变的核心策略源头，向上承接私域营销的流量运营与转化目标，向下为定制沟通话术与素材、匹配裂变玩法提供分层依据，具体包括：基 于用户价值 / 行为特征制定分层裂变策略（如高净值用户专属裂变方案），针对不同价值、行为特征的用户群体，设计差异化裂变策略，重点提升高潜力用户的传播转化效率，为下游模块输出清晰的用户分层导向与策略方向。\n【关键词】用户分层、分层裂变、用户价值、差异化策略、 裂变方案",
    "description": ""
  },
  {
    "id": "copy_planning",
    "seq": "3",
    "name": " 文案策划",
    "capabilities": "【用户场景】设计推广文案、写活动文案、降低获客成本、解决活动效果不好的问题\n【核心能力】聚焦活动主文案、传播文案、落地页文案等核心内容的策略性策划，具体包括撰写适配不同场景的营销文案 —— 活动主标题贴合主题调性，社交媒体传播语匹配平台 氛围，落地页正文衔接用户转化路径，最终精准传递品牌或活动核心价值，助力营销目标落地。\n【关键词】文案策划、活动文案、传播文案、 推广文案、获客成本",
    "description": ""
  }
]  [common_task_planner.py:104]
2026-01-08 10:10:02,416 INFO    =>  [CommonTaskPlanner] LLM response:
[{'step': 1, 'type': 'AGENT', 'executor': 'fission_mech_design', 'content': '为一家投影仪公司设计裂变营销的目标，包括设定裂变规则、邀请奖励机制以及层级关系。确保这些目标能够有效促进产品销量和品牌知名度的提升。', 'description': '设计裂变机制'}, {'step': 2, 'type': 'AGENT', 'executor': 'user_strat_fission', 'content': '基于第一步中确定的裂变目标，对用户进行分层，并针对不同层次的用户（如高净值客户与普通消费者）设计相应的裂变策略，以提高整体分享率和参与度。', 'description': '用户分层裂变策略'}, {'step': 3, 'type': 'AGENT', 'executor': 'copy_planning', 'content': '根据前两步的结果，编写一系列吸引潜在买家注意的推广文案，内容需围绕投 影仪的特点及其带来的生活方式改变，旨在降低获客成本并提高活动转化率。', 'description': '撰写营销文案'}]  [common_task_planner.py:98]
2026-01-08 10:10:02,416 INFO    =>  Final plan generated with 3 steps (expanded from 3).  [common_task_planner.py:71]
2026-01-08 10:10:02,417 INFO    =>  [AgentActor] Task planning result:
[{'step': 1, 'type': 'AGENT', 'executor': 'fission_mech_design', 'content': '为一家投影仪公司设计裂变营销的目标，包括设定裂变规则、邀请奖励机制以及层级关系。确保这些目标能够有效促进产品销量和品牌知名度的提升。', 'description': '设计裂变机制'}, {'step': 2, 'type': 'AGENT', 'executor': 'user_strat_fission', 'content': '基于第一步中确定的裂变目标，对用户进行分层，并针对不同层次的用户（如高净值客户与普通消费者）设计相应的裂变策略，以提高整体分享率和参与度。', 'description': '用户分层裂变策略'}, {'step': 3, 'type': 'AGENT', 'executor': 'copy_planning', 'content': '根据前两步的结果，编写一系列吸引潜在买家注意的推广文案，内容需围绕投 影仪的特点及其带来的生活方式改变，旨在降低获客成本并提高活动转化率。', 'description': '撰写营销文案'}]  [agent_actor.py:187]   
2026-01-08 10:10:02,425 INFO    =>  Sending task group to aggregator  [agent_actor.py:419]
E:\Data\Flora\tasks\agents\agent_actor.py:195: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited 
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:02,426 INFO    =>  Starting TaskGroup Workflow: 46cdc530-d522-4a7c-bd0c-59091c5b419c  [task_group_aggregator_actor.py:132]
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:148: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:02,427 INFO    =>  Executing Step 1: '设计裂变机制' (type=AGENT)  [task_group_aggregator_actor.py:192]        
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:195: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:02,428 INFO    =>  --> Route: ResultAggregator for Step 1 (Agent)  [task_group_aggregator_actor.py:263]       
2026-01-08 10:10:02,428 WARNING =>  _get_merged_context called before task step_1 was registered  [result_aggregator_actor.py:547]
2026-01-08 10:10:02,444 INFO    =>  HTTP Request: GET http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status "HTTP/1.1 502 Bad Gateway"  [_client.py:1740]
2026-01-08 10:10:02,444 ERROR   =>  Failed to get signal status: 502 -   [event_bus.py:266]
2026-01-08 10:10:02,446 WARNING =>  Error checking signal status: Server error '502 Bad Gateway' for url 'http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502, continuing execution...  [result_aggregator_actor.py:103]
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:167: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:02,447 INFO    =>  ResultAggregator: Received task request for AgentActor: fission_mech_design  [result_aggregator_actor.py:187]
2026-01-08 10:10:02,449 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:10:02,585 INFO    =>  Created new AgentActor for fission_mech_design  [result_aggregator_actor.py:241]
2026-01-08 10:10:02,587 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:10:02,732 INFO    =>  AgentActor initialized for fission_mech_design  [agent_actor.py:106]
2026-01-08 10:10:02,732 INFO    =>  [AgentActor] Handling task step_1: 内容：为一家投影仪公司设计裂变营销的目标，包括设定裂变规则、邀请奖励机制以及层级关系。确保这些目标能...  [agent_actor.py:142]
E:\Data\Flora\tasks\agents\agent_actor.py:145: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited 
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
Retrieving core memory for user <user_id:1>,<tenant_id:1>
2026-01-08 10:10:03,115 INFO    =>  HTTP Request: POST https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings "HTTP/1.1 200 OK"  [_client.py:1025]
2026-01-08 10:10:03,290 INFO    =>  HTTP Request: POST https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings "HTTP/1.1 200 OK"  [_client.py:1025]
E:\Data\Flora\tasks\agents\agent_actor.py:163: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:03,396 INFO    =>  [CommonTaskPlanner] agents:
[
  {
    "id": "goal_setting",
    "seq": 1,
    "name": " 目标设定",
    "capabilities": "【用户场景】设定KPI、配置活动目标、定义考核指标、关于目标的功能\n【核心能力】作为机制与玩法设计的目标导向 模块，承接其玩法与规则设计需求，明确裂变活动的量化标准，具体包括：锚定裂变活动核心 KPI（如新增用户数、分享率、裂变转化率），先 明确活动需达成的关键结果指标（匹配机制与玩法设计的互动目标），再为各指标设定可量化的目标值，同时确定清晰的考核周期，确保目标可 落地、可追踪，为玩法与激励设计提供结果导向。\n【关键词】目标设定、KPI、活动目标、考核指标、量化目标",
    "description": ""
  }
]  [common_task_planner.py:104]
2026-01-08 10:10:09,708 INFO    =>  [CommonTaskPlanner] LLM response:
[{'step': 1, 'type': 'AGENT', 'executor': 'goal_setting', 'content': '为一家投影仪公司设计裂变营销活动的目标。首先，确定该活动 的核心KPI，例如新增用户数、分享率和裂变转化率等关键结果指标。其次，设定可量化的目标值，并定义清晰的考核周期来确保这些目标是可以落地并追踪的。此外，还需要设计裂变规则及邀请奖励机制，包括但不限于推荐人与被推荐人的层级关系及其对应的奖励制度，以此有效促进产 品销量和品牌知名度的提升。', 'description': '裂变营销目标设定'}]  [common_task_planner.py:98]
2026-01-08 10:10:09,708 INFO    =>  Final plan generated with 1 steps (expanded from 1).  [common_task_planner.py:71]
2026-01-08 10:10:09,708 INFO    =>  [AgentActor] Task planning result:
[{'step': 1, 'type': 'AGENT', 'executor': 'goal_setting', 'content': '为一家投影仪公司设计裂变营销活动的目标。首先，确定该活动 的核心KPI，例如新增用户数、分享率和裂变转化率等关键结果指标。其次，设定可量化的目标值，并定义清晰的考核周期来确保这些目标是可以落地并追踪的。此外，还需要设计裂变规则及邀请奖励机制，包括但不限于推荐人与被推荐人的层级关系及其对应的奖励制度，以此有效促进产 品销量和品牌知名度的提升。', 'description': '裂变营销目标设定'}]  [agent_actor.py:187]
2026-01-08 10:10:09,708 INFO    =>  Sending task group to aggregator  [agent_actor.py:419]
E:\Data\Flora\tasks\agents\agent_actor.py:195: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited 
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:09,709 INFO    =>  Starting TaskGroup Workflow: step_1  [task_group_aggregator_actor.py:132]
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:148: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:09,709 INFO    =>  Executing Step 1: '裂变营销目标设定' (type=AGENT)  [task_group_aggregator_actor.py:192]    
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:195: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:09,710 INFO    =>  --> Route: ResultAggregator for Step 1 (Agent)  [task_group_aggregator_actor.py:263]       
2026-01-08 10:10:09,710 WARNING =>  _get_merged_context called before task step_1 was registered  [result_aggregator_actor.py:547]
2026-01-08 10:10:09,714 INFO    =>  HTTP Request: GET http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status "HTTP/1.1 502 Bad Gateway"  [_client.py:1740]
2026-01-08 10:10:09,714 ERROR   =>  Failed to get signal status: 502 -   [event_bus.py:266]
2026-01-08 10:10:09,714 WARNING =>  Error checking signal status: Server error '502 Bad Gateway' for url 'http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502, continuing execution...  [result_aggregator_actor.py:103]
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:167: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:09,715 INFO    =>  ResultAggregator: Received task request for AgentActor: goal_setting  [result_aggregator_actor.py:187]
2026-01-08 10:10:09,716 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:10:09,853 INFO    =>  Created new LeafActor for goal_setting  [result_aggregator_actor.py:241]
2026-01-08 10:10:09,854 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:10:09,971 INFO    =>  LeafActor initialized for goal_setting  [leaf_actor.py:70]
2026-01-08 10:10:09,971 INFO    =>  [LeafActor] Handling task step_1: 内容：为一家投影仪公司设计裂变营销活动的目标。首先，确定 该活动的核心KPI，例如新增用户数、分享率和...  [leaf_actor.py:94]
2026-01-08 10:10:09,972 INFO    =>  ExecutionActor initialized  [execution_actor.py:35]
E:\Data\Flora\tasks\agents\leaf_actor.py:164: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited  
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:09,972 INFO    =>  ⑪ 具体执行: task=step_1, capability=dify  [execution_actor.py:96]
E:\Data\Flora\tasks\capability_actors\execution_actor.py:106: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:09,973 INFO    =>  Executing Dify workflow for task step_1  [execution_actor.py:128]
2026-01-08 10:10:10,049 INFO    =>  Dify schema: {'opening_statement': '', 'suggested_questions': [], 'suggested_questions_after_answer': {'enabled': False}, 'speech_to_text': {'enabled': False}, 'text_to_speech': {'enabled': False, 'language': '', 'voice': ''}, 'retriever_resource': {'enabled': True}, 'annotation_reply': {'enabled': False}, 'more_like_this': {'enabled': False}, 'user_input_form': [{'text-input': {'label': '用户id', 'max_length': 48, 'options': [], 'required': True, 'type': 'text-input', 'variable': 'user_id'}}, {'text-input': {'label': '租户id', 'max_length': 48, 'options': [], 'required': True, 'type': 'text-input', 'variable': 'tenant_id'}}, {'text-input': {'label': '产品类型或者行业类型：用户的产品名称或者如美妆、教育、新零售、本地生活、餐饮等行业名称', 'max_length': 48, 'options': [], 'required': True, 'type': 'text-input', 'variable': 'industry'}}], 'sensitive_word_avoidance': {'enabled': False}, 'file_upload': {'image': {'enabled': False, 'number_limits': 3, 'transfer_methods': ['local_file', 'remote_url']}, 'enabled': False, 'allowed_file_types': ['image'], 'allowed_file_extensions': ['.JPG', '.JPEG', '.PNG', '.GIF', '.WEBP', '.SVG'], 'allowed_file_upload_methods': ['local_file', 'remote_url'], 'number_limits': 3, 'fileUploadConfig': {'file_size_limit': 15, 'batch_count_limit': 5, 'image_file_size_limit': 10, 'video_file_size_limit': 100, 'audio_file_size_limit': 50, 'workflow_file_upload_limit': 10}}, 'system_parameters': {'image_file_size_limit': 10, 'video_file_size_limit': 100, 'audio_file_size_limit': 50, 'file_size_limit': 15, 'workflow_file_upload_limit': 10}}  [dify_connector.py:125]        
2026-01-08 10:10:10,050 INFO    =>  Missing inputs: {'user_id': '用户id', 'tenant_id': '租户id', 'industry': '产品类型或者行业 类型：用户的产品名称或者如美妆、教育、新零售、本地生活、餐饮等行业名称'}  [dify_connector.py:158]
2026-01-08 10:10:10,050 INFO    =>  Full context: {'global_context': {}, 'enriched_context': {}, 'content': '为一家投影仪公司设计裂变营销活动的目标。首先，确定该活动的核心KPI，例如新增用户数、分享率和裂变转化率等关键结果指标。其次，设定可量化的目标值，并定义清晰的考核周期来确保这些目标是可以落地并追踪的。此外，还需要设计裂变规则及邀请奖励机制，包括但不限于推荐人与被推荐人的层级 关系及其对应的奖励制度，以此有效促进产品销量和品牌知名度的提升。', 'description': '裂变营销目标设定', 'agent_id': 'goal_setting', 'user_id': '<user_id:1>,<tenant_id:1>', 'original_inputs': {}}  [dify_connector.py:176]
2026-01-08 10:10:10,050 INFO    =>  Dependencies (TreeManager, LLM) injected.  [tree_context_resolver.py:56]
2026-01-08 10:10:13,846 INFO    =>  params will be used: {'api_key': 'app-onEo7S6WehdvW5OgwqfzB0zK', 'inputs': {}, 'agent_id': 'goal_setting', 'user_id': '<user_id:1>,<tenant_id:1>', 'content': '为一家投影仪公司设计裂变营销活动的目标。首先，确定该活动的 核心KPI，例如新增用户数、分享率和裂变转化率等关键结果指标。其次，设定可量化的目标值，并定义清晰的考核周期来确保这些目标是可以落地并追踪的。此外，还需要设计裂变规则及邀请奖励机制，包括但不限于推荐人与被推荐人的层级关系及其对应的奖励制度，以此有效促进产品 销量和品牌知名度的提升。', 'description': '裂变营销目标设定', 'global_context': {}, 'enriched_context': {}}  [dify_connector.py:182]
2026-01-08 10:10:13,846 INFO    =>  Enhanced inputs: {}  [dify_connector.py:187]
2026-01-08 10:10:13,923 INFO    =>  Start resolving context for agent: goal_setting (Path: 10000000000000000000000000000001 -> private_domain -> fission_mech_design -> goal_setting)  [tree_context_resolver.py:78]
2026-01-08 10:10:13,923 INFO    =>  Completed inputs: {'user_id': '1', 'tenant_id': '1', 'industry': '投影仪'}  [dify_connector.py:190]
2026-01-08 10:10:20,327 INFO    =>  Dify response: {'task_id': 'd08cf493-ed3d-466d-83c3-d99f25804bae', 'workflow_run_id': 'da8f5430-931b-49dd-9e9b-05c824fb3847', 'data': {'id': 'da8f5430-931b-49dd-9e9b-05c824fb3847', 'workflow_id': '173d6c4a-ccac-4c21-b991-b1db4ca3e9d3', 'status': 'succeeded', 'outputs': {'active_id': '664289733874159616'}, 'error': None, 'elapsed_time': 6.238108, 'total_tokens': 697, 'total_steps': 5, 'created_at': 1767838214, 'finished_at': 1767838220}}  [dify_connector.py:246]       
2026-01-08 10:10:20,327 INFO    =>  Dify outputs: {'active_id': '664289733874159616'}  [dify_connector.py:285]
E:\Data\Flora\tasks\capability_actors\execution_actor.py:265: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
E:\Data\Flora\tasks\agents\leaf_actor.py:226: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited  
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:20,328 INFO    =>  Received TaskCompletedMessage for step_1: SUCCESS  [result_aggregator_actor.py:246]        
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:279: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:432: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:20,331 INFO    =>  Step 1 succeeded.  [task_group_aggregator_actor.py:314]
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:317: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:20,332 INFO    =>  Workflow step_1 Completed.  [task_group_aggregator_actor.py:426]
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:429: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:20,333 INFO    =>  Received ActorExitRequest, shutting down.  [result_aggregator_actor.py:113]
E:\Data\Flora\tasks\agents\agent_actor.py:463: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited 
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:20,333 INFO    =>  Received ActorExitRequest, shutting down.  [task_group_aggregator_actor.py:73]
2026-01-08 10:10:20,334 INFO    =>  Received TaskCompletedMessage for step_1: SUCCESS  [result_aggregator_actor.py:246]        
2026-01-08 10:10:20,334 INFO    =>  Child actor exited: ActorAddr-/A~a~a~a~a~a, reason: {'_childAddr': <thespian.actors.ActorAddress object at 0x0000027F2613E570>}  [agent_actor.py:68]
2026-01-08 10:10:20,334 INFO    =>  Received ActorExitRequest, shutting down.  [leaf_actor.py:25]
2026-01-08 10:10:20,335 INFO    =>  Step 1 succeeded.  [task_group_aggregator_actor.py:314]
2026-01-08 10:10:20,335 INFO    =>  Executing Step 2: '用户分层裂变策略' (type=AGENT)  [task_group_aggregator_actor.py:192]    
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:195: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:20,335 INFO    =>  --> Route: ResultAggregator for Step 2 (Agent)  [task_group_aggregator_actor.py:263]       
2026-01-08 10:10:20,335 INFO    =>  Received ActorExitRequest, shutting down.  [result_aggregator_actor.py:113]
2026-01-08 10:10:20,336 WARNING =>  _get_merged_context called before task step_2 was registered  [result_aggregator_actor.py:547]
2026-01-08 10:10:20,356 INFO    =>  HTTP Request: GET http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status "HTTP/1.1 502 Bad Gateway"  [_client.py:1740]
2026-01-08 10:10:20,356 ERROR   =>  Failed to get signal status: 502 -   [event_bus.py:266]
2026-01-08 10:10:20,356 WARNING =>  Error checking signal status: Server error '502 Bad Gateway' for url 'http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502, continuing execution...  [result_aggregator_actor.py:103]
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:167: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:20,356 INFO    =>  ResultAggregator: Received task request for AgentActor: user_strat_fission  [result_aggregator_actor.py:187]
2026-01-08 10:10:20,358 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:10:20,479 INFO    =>  Created new AgentActor for user_strat_fission  [result_aggregator_actor.py:241]
2026-01-08 10:10:20,480 INFO    =>  Child actor exited: ActorAddr-/A~a~a~a, reason: {'_childAddr': <thespian.actors.ActorAddress object at 0x0000027F25A536B0>}  [task_group_aggregator_actor.py:77]
2026-01-08 10:10:20,480 WARNING =>  Unknown message format: <class 'thespian.actors.ActorExitRequest'>  [execution_actor.py:56]
2026-01-08 10:10:20,481 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:10:20,626 INFO    =>  AgentActor initialized for user_strat_fission  [agent_actor.py:106]
2026-01-08 10:10:20,627 INFO    =>  [AgentActor] Handling task step_2: 内容：基于第一步中确定的裂变目标，对用户进行分层，并针对不同层次的用户（如高净值客户与普通消费者）设...  [agent_actor.py:142]
E:\Data\Flora\tasks\agents\agent_actor.py:145: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited 
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
Retrieving core memory for user <user_id:1>,<tenant_id:1>
2026-01-08 10:10:20,909 INFO    =>  HTTP Request: POST https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings "HTTP/1.1 200 OK"  [_client.py:1025]
2026-01-08 10:10:21,091 INFO    =>  HTTP Request: POST https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings "HTTP/1.1 200 OK"  [_client.py:1025]
E:\Data\Flora\tasks\agents\agent_actor.py:163: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:21,199 INFO    =>  [CommonTaskPlanner] agents:
[
  {
    "id": "strat_fission_strat",
    "seq": 2,
    "name": " 分层裂变策略设计",
    "capabilities": "【用户场景】设计裂变方案、设置用户等级、划分用户群体、实现病毒式传播、提高分享率\n【核心能力】针对新客、活跃用户、KOC 等不同层级用户群体，设计差异化裂变路径及配套激励方案，具体包括针对各层级用户规划适配的专属裂变路径与激励组合，进而 提升整体裂变的传播效率与转化效果。\n【关键词】分层策略、裂变策略、用户等级、差异化路径、传播效率",
    "description": ""
  },
  {
    "id": "strat_portraits",
    "seq": 2,
    "name": " 绘制分层画像",
    "capabilities": "【用户场景】用户分层、分析用户特征、解决用户流失问题、增加用户数量\n【核心能力】基于行为、属性、价值等核心维度，构建多维度用户分层画像，具体包括综合用户基础属性（如年龄、地域）、关键行为数据（如浏览频次、消费记录）和商业价值（如客单 价、复购率），划分差异化用户群体并输出结构化分层画像报告，为后续精准营销、分层运营提供数据支撑。\n【关键词】用户画像、用户分层 、用户分析、用户特征、用户流失",
    "description": ""
  }
]  [common_task_planner.py:104]
2026-01-08 10:10:34,362 INFO    =>  [CommonTaskPlanner] LLM response:
[{'step': 1, 'type': 'AGENT', 'executor': 'strat_portraits', 'content': '基于用户行为、属性和价值等维度，构建多维度用户分层画像。具体包括综合用户的基础属性（如年龄、地域）、关键行为数据（如浏览频次、消费记录）以及商业价值（如客单价、复购率），划分出不同 的用户群体，并输出一份结构化的分层画像报告。', 'description': '绘制用户分层画像'}, {'step': 2, 'type': 'AGENT', 'executor': 'strat_fission_strat', 'content': '根据第一步中创建的用户分层画像，针对不同层次的用户（例如高净值客户与普通消费者）设计差异化的裂 变路径及激励方案。目标是提高整体分享率和用户的参与度。确保每个层级都有适合其特性的专属裂变路径与激励组合，以提升传播效率与转化 效果。', 'description': '设计分层裂变策略'}]  [common_task_planner.py:98]
2026-01-08 10:10:34,362 INFO    =>  Final plan generated with 2 steps (expanded from 2).  [common_task_planner.py:71]
2026-01-08 10:10:34,362 INFO    =>  [AgentActor] Task planning result:
[{'step': 1, 'type': 'AGENT', 'executor': 'strat_portraits', 'content': '基于用户行为、属性和价值等维度，构建多维度用户分层画像。具体包括综合用户的基础属性（如年龄、地域）、关键行为数据（如浏览频次、消费记录）以及商业价值（如客单价、复购率），划分出不同 的用户群体，并输出一份结构化的分层画像报告。', 'description': '绘制用户分层画像'}, {'step': 2, 'type': 'AGENT', 'executor': 'strat_fission_strat', 'content': '根据第一步中创建的用户分层画像，针对不同层次的用户（例如高净值客户与普通消费者）设计差异化的裂 变路径及激励方案。目标是提高整体分享率和用户的参与度。确保每个层级都有适合其特性的专属裂变路径与激励组合，以提升传播效率与转化 效果。', 'description': '设计分层裂变策略'}]  [agent_actor.py:187]
2026-01-08 10:10:34,362 INFO    =>  Sending task group to aggregator  [agent_actor.py:419]
E:\Data\Flora\tasks\agents\agent_actor.py:195: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited 
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:34,363 INFO    =>  Received ActorExitRequest, shutting down.  [agent_actor.py:64]
2026-01-08 10:10:34,363 INFO    =>  Starting TaskGroup Workflow: step_2  [task_group_aggregator_actor.py:132]
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:148: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:34,363 INFO    =>  Executing Step 1: '绘制用户分层画像' (type=AGENT)  [task_group_aggregator_actor.py:192]    
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:195: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:34,363 INFO    =>  --> Route: ResultAggregator for Step 1 (Agent)  [task_group_aggregator_actor.py:263]       
2026-01-08 10:10:34,363 WARNING =>  _get_merged_context called before task step_1 was registered  [result_aggregator_actor.py:547]
2026-01-08 10:10:34,367 INFO    =>  HTTP Request: GET http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status "HTTP/1.1 502 Bad Gateway"  [_client.py:1740]
2026-01-08 10:10:34,368 ERROR   =>  Failed to get signal status: 502 -   [event_bus.py:266]
2026-01-08 10:10:34,368 WARNING =>  Error checking signal status: Server error '502 Bad Gateway' for url 'http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502, continuing execution...  [result_aggregator_actor.py:103]
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:167: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:34,368 INFO    =>  ResultAggregator: Received task request for AgentActor: strat_portraits  [result_aggregator_actor.py:187]
2026-01-08 10:10:34,370 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:10:34,470 INFO    =>  Created new LeafActor for strat_portraits  [result_aggregator_actor.py:241]
2026-01-08 10:10:34,470 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:10:34,606 INFO    =>  LeafActor initialized for strat_portraits  [leaf_actor.py:70]
2026-01-08 10:10:34,606 INFO    =>  [LeafActor] Handling task step_1: 内容：基于用户行为、属性和价值等维度，构建多维度用户分层 画像。具体包括综合用户的基础属性（如年龄、地...  [leaf_actor.py:94]
2026-01-08 10:10:34,606 INFO    =>  ExecutionActor initialized  [execution_actor.py:35]
E:\Data\Flora\tasks\agents\leaf_actor.py:164: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited  
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:34,606 INFO    =>  ⑪ 具体执行: task=step_1, capability=dify  [execution_actor.py:96]
E:\Data\Flora\tasks\capability_actors\execution_actor.py:106: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:34,606 INFO    =>  Executing Dify workflow for task step_1  [execution_actor.py:128]
2026-01-08 10:10:34,674 INFO    =>  Dify schema: {'opening_statement': '', 'suggested_questions': [], 'suggested_questions_after_answer': {'enabled': False}, 'speech_to_text': {'enabled': False}, 'text_to_speech': {'enabled': False, 'language': '', 'voice': ''}, 'retriever_resource': {'enabled': True}, 'annotation_reply': {'enabled': False}, 'more_like_this': {'enabled': False}, 'user_input_form': [{'text-input': {'label': '用户id', 'max_length': 48, 'options': [], 'required': True, 'type': 'text-input', 'variable': 'user_id'}}, {'text-input': {'label': '租户id', 'max_length': 48, 'options': [], 'required': True, 'type': 'text-input', 'variable': 'tenant_id'}}, {'paragraph': {'label': '裂变目标', 'max_length': 512, 'options': [], 'required': False, 'type': 'paragraph', 'variable': 'fission_plan_set_id'}}, {'text-input': {'variable': 'active_id', 'label': '活动ID', 'type': 'text-input', 'max_length': 128, 'required': True, 'options': [], 'placeholder': '', 'default': '', 'hint': ''}}], 'sensitive_word_avoidance': {'enabled': False}, 'file_upload': {'image': {'enabled': False, 'number_limits': 3, 'transfer_methods': ['local_file', 'remote_url']}, 'enabled': False, 'allowed_file_types': ['image'], 'allowed_file_extensions': ['.JPG', '.JPEG', '.PNG', '.GIF', '.WEBP', '.SVG'], 'allowed_file_upload_methods': ['local_file', 'remote_url'], 'number_limits': 3, 'fileUploadConfig': {'file_size_limit': 15, 'batch_count_limit': 5, 'image_file_size_limit': 10, 'video_file_size_limit': 100, 'audio_file_size_limit': 50, 'workflow_file_upload_limit': 10}}, 'system_parameters': {'image_file_size_limit': 10, 'video_file_size_limit': 100, 'audio_file_size_limit': 50, 'file_size_limit': 15, 'workflow_file_upload_limit': 10}}  [dify_connector.py:125]
2026-01-08 10:10:34,674 INFO    =>  Missing inputs: {'user_id': '用户id', 'tenant_id': '租户id', 'active_id': '活动ID'}  [dify_connector.py:158]
2026-01-08 10:10:34,674 INFO    =>  Full context: {'global_context': {}, 'enriched_context': {'__private_domain_task_group.step_1': ContextEntry(value={'step_results': {'step_1_output': {'status': 'SUCCESS', 'result': {'active_id': '664289733874159616'}}}}, source='ActorAddr-/A~a~a~a', task_path='//private_domain/task_group', timestamp=1767838220.3350613, confidence=1.0)}, 'content': '基于用户行为、属性和价值等维度，构建多维度用户分层画像。具体包括综合用户的基础属性（如年龄、地域）、关键行为数据（如浏览频次、消费记录）以及商业价值（如客单价、复购率），划分出不同的用户群体，并输出一份结构化的分层画像报告。', 'description': '绘制用户分层画像', 'agent_id': 'strat_portraits', 'user_id': '<user_id:1>,<tenant_id:1>', 'original_inputs': {}}  [dify_connector.py:176]
2026-01-08 10:10:38,386 INFO    =>  params will be used: {'api_key': 'app-y96fZH5kCbv6YEuQtMZangg0', 'inputs': {}, 'agent_id': 'strat_portraits', 'user_id': '<user_id:1>,<tenant_id:1>', 'content': '基于用户行为、属性和价值等维度，构建多维度用户分层画像。具体包括综合用户的基础属性（如年龄、地域）、关键行为数据（如浏览频次、消费记录）以及商业价值（如客单价、复购率），划分出不同的 用户群体，并输出一份结构化的分层画像报告。', 'description': '绘制用户分层画像', 'global_context': {}, 'enriched_context': {'__private_domain_task_group.step_1': ContextEntry(value={'step_results': {'step_1_output': {'status': 'SUCCESS', 'result': {'active_id': '664289733874159616'}}}}, source='ActorAddr-/A~a~a~a', task_path='//private_domain/task_group', timestamp=1767838220.3350613, confidence=1.0)}}  [dify_connector.py:182]
2026-01-08 10:10:38,386 INFO    =>  Enhanced inputs: {}  [dify_connector.py:187]
2026-01-08 10:10:38,422 INFO    =>  Start resolving context for agent: strat_portraits (Path: 10000000000000000000000000000001 -> private_domain -> user_strat_fission -> strat_portraits)  [tree_context_resolver.py:78]
2026-01-08 10:10:38,422 INFO    =>  Completed inputs: {'user_id': '1', 'tenant_id': '1', 'active_id': '664289733874159616'}  [dify_connector.py:190]
2026-01-08 10:10:48,462 INFO    =>  Dify response: {'task_id': '8dac51e4-5a4b-4ae3-8c8c-3f3191db7e11', 'workflow_run_id': 'cfdc9935-956c-49e3-9b61-51a4f7d081da', 'data': {'id': 'cfdc9935-956c-49e3-9b61-51a4f7d081da', 'workflow_id': '9c322a4c-dba9-4816-8780-26bcc8789a10', 'status': 'succeeded', 'outputs': {'body': '{"code":0,"data":9,"msg":""}'}, 'error': None, 'elapsed_time': 9.968689, 'total_tokens': 1461, 'total_steps': 7, 'created_at': 1767838238, 'finished_at': 1767838248}}  [dify_connector.py:246] 
2026-01-08 10:10:48,462 INFO    =>  Dify outputs: {'body': '{"code":0,"data":9,"msg":""}'}  [dify_connector.py:285]
E:\Data\Flora\tasks\capability_actors\execution_actor.py:265: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
E:\Data\Flora\tasks\agents\leaf_actor.py:226: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited  
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:48,463 INFO    =>  Received TaskCompletedMessage for step_1: SUCCESS  [result_aggregator_actor.py:246]        
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:279: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:432: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:48,464 INFO    =>  Step 1 succeeded.  [task_group_aggregator_actor.py:314]
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:317: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:48,464 INFO    =>  Executing Step 2: '设计分层裂变策略' (type=AGENT)  [task_group_aggregator_actor.py:192]    
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:195: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:48,464 INFO    =>  --> Route: ResultAggregator for Step 2 (Agent)  [task_group_aggregator_actor.py:263]       
2026-01-08 10:10:48,464 INFO    =>  Received ActorExitRequest, shutting down.  [result_aggregator_actor.py:113]
2026-01-08 10:10:48,464 WARNING =>  _get_merged_context called before task step_2 was registered  [result_aggregator_actor.py:547]
2026-01-08 10:10:48,471 INFO    =>  HTTP Request: GET http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status "HTTP/1.1 502 Bad Gateway"  [_client.py:1740]
2026-01-08 10:10:48,471 ERROR   =>  Failed to get signal status: 502 -   [event_bus.py:266]
2026-01-08 10:10:48,471 WARNING =>  Error checking signal status: Server error '502 Bad Gateway' for url 'http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502, continuing execution...  [result_aggregator_actor.py:103]
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:167: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:48,472 INFO    =>  ResultAggregator: Received task request for AgentActor: strat_fission_strat  [result_aggregator_actor.py:187]
2026-01-08 10:10:48,473 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:10:48,631 INFO    =>  Created new AgentActor for strat_fission_strat  [result_aggregator_actor.py:241]
2026-01-08 10:10:48,631 INFO    =>  Child actor exited: ActorAddr-/A~a~a~b~a~a~a, reason: {'_childAddr': <thespian.actors.ActorAddress object at 0x0000027F257D6A20>}  [task_group_aggregator_actor.py:77]
2026-01-08 10:10:48,633 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:10:48,771 INFO    =>  AgentActor initialized for strat_fission_strat  [agent_actor.py:106]
2026-01-08 10:10:48,771 INFO    =>  [AgentActor] Handling task step_2: 内容：根据第一步中创建的用户分层画像，针对不同层次的用户（例如高净值客户与普通消费者）设计差异化的裂...  [agent_actor.py:142]
E:\Data\Flora\tasks\agents\agent_actor.py:145: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited 
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
Retrieving core memory for user <user_id:1>,<tenant_id:1>
2026-01-08 10:10:49,077 INFO    =>  HTTP Request: POST https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings "HTTP/1.1 200 OK"  [_client.py:1025]
2026-01-08 10:10:49,229 INFO    =>  HTTP Request: POST https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings "HTTP/1.1 200 OK"  [_client.py:1025]
E:\Data\Flora\tasks\agents\agent_actor.py:163: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:10:49,366 INFO    =>  [CommonTaskPlanner] agents:
[
  {
    "id": "comm_scripts",
    "seq": 1,
    "name": " 定制沟通话术与素材",
    "capabilities": "【用户场景】写营销话术、设计沟通话术、解决用户流失问题、定制客服话术\n【核心能力】作为用户分层裂变设计的场景化内容落地载体，承接其输出的用户分层特征与策略需求，具体包括：针对私域、客服、推送三大场景，定制个性化沟通话术与视觉素材，结 合用户分层裂变设计的群体差异（如新客对福利敏感、高净值用户注重体验）与场景特点，产出精准适配的沟通话术（如欢迎语、催促语、售后 安抚语）及配套视觉素材（含图片、短视频），确保内容与用户需求、场景氛围高度契合，强化分层裂变的沟通精准度。\n【关键词】话术设计 、沟通话术、客服话术、营销话术、用户流失",
    "description": ""
  },
  {
    "id": "fission_game_match",
    "seq": 3,
    "name": " 匹配裂变玩法",
    "capabilities": "【用户场景】选择裂变玩法、做裂变活动、设计裂变方案、提高转化、增加用户数量\n【核心能力】作为用户分层裂变设计的玩法执行支撑模块，依托其输出的用户特征与策略方向，具体包括：结合用户分层裂变设计的用户群体属性（如行为偏好、价值层级）与业 务目标，匹配最优裂变玩法机制（如砍价、邀请助力等），基于精准用户画像与明确活动目标，筛选并推荐最适配的裂变玩法类型，同步提升用 户参与意愿、传播广度与最终转化效率，让分层裂变策略通过具象化玩法落地。\n【关键词】匹配玩法、裂变玩法、玩法推荐、转化效率",     
    "description": ""
  },
  {
    "id": "strat_incentives",
    "seq": 4,
    "name": " 设计分层激励",
    "capabilities": "【用户场景】用户分层激励、设置不同用户不同奖励、提高用户活跃度、设置用户等级\n【核心能力】针对新客、老客、KOC 等不同用户层级，设计差异化激励策略，具体包括为不同价值用户匹配阶梯式或定制化激励内容 —— 新客可获首单专属礼包，老客享裂变专 属折扣券，KOC 得更高比例佣金，以此提升各层级用户的裂变参与度与价值贡献。\n【关键词】分层激励、差异化激励、用户层级、阶梯激励", 
    "description": ""
  }
]  [common_task_planner.py:104]
2026-01-08 10:11:13,766 INFO    =>  [CommonTaskPlanner] LLM response:
[{'step': 1, 'type': 'AGENT', 'executor': 'fission_game_match', 'content': '基于已创建的用户分层画像，分别为高净值客户与普通消 费者匹配最适合的裂变玩法。对于高净值客户，考虑使用能体现其身份尊贵且参与感强的活动形式；对于普通消费者，则选择门槛低、易于传播 的方式以提高他们的参与度。', 'description': '为不同用户层级匹配裂变玩法'}, {'step': 2, 'type': 'AGENT', 'executor': 'strat_incentives', 'content': '针对已经定义好的两个主要用户群体（高净值客户和普通消费者），设计差异化的激励方案。对高净值客户可以提供独家优惠或限量版礼品作为奖励；而对于普通消费者，则通过发放小额红包或者积分来鼓励他们参与到裂变活动中。', 'description': '制定分层激励策略'}, {'step': 3, 'type': 'AGENT', 'executor': 'comm_scripts', 'content': '结合前两步确定的裂变玩法及激励措施，为高净值客户和普通消费者分别定制专属沟通话术和视觉素材。确保所有内容都符合各自群体的特点，并能够有效促进信息分享与转化。', 'description': '定制化沟通材料'}]  [common_task_planner.py:98]
2026-01-08 10:11:13,767 INFO    =>  Final plan generated with 3 steps (expanded from 3).  [common_task_planner.py:71]
2026-01-08 10:11:13,767 INFO    =>  [AgentActor] Task planning result:
[{'step': 1, 'type': 'AGENT', 'executor': 'fission_game_match', 'content': '基于已创建的用户分层画像，分别为高净值客户与普通消 费者匹配最适合的裂变玩法。对于高净值客户，考虑使用能体现其身份尊贵且参与感强的活动形式；对于普通消费者，则选择门槛低、易于传播 的方式以提高他们的参与度。', 'description': '为不同用户层级匹配裂变玩法'}, {'step': 2, 'type': 'AGENT', 'executor': 'strat_incentives', 'content': '针对已经定义好的两个主要用户群体（高净值客户和普通消费者），设计差异化的激励方案。对高净值客户可以提供独家优惠或限量版礼品作为奖励；而对于普通消费者，则通过发放小额红包或者积分来鼓励他们参与到裂变活动中。', 'description': '制定分层激励策略'}, {'step': 3, 'type': 'AGENT', 'executor': 'comm_scripts', 'content': '结合前两步确定的裂变玩法及激励措施，为高净值客户和普通消费者分别定制专属沟通话术和视觉素材。确保所有内容都符合各自群体的特点，并能够有效促进信息分享与转化。', 'description': '定制化沟通材料'}]  [agent_actor.py:187]
2026-01-08 10:11:13,767 INFO    =>  Sending task group to aggregator  [agent_actor.py:419]
E:\Data\Flora\tasks\agents\agent_actor.py:195: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited 
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:13,767 INFO    =>  Received ActorExitRequest, shutting down.  [leaf_actor.py:25]
2026-01-08 10:11:13,768 INFO    =>  Starting TaskGroup Workflow: step_2  [task_group_aggregator_actor.py:132]
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:148: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:13,769 INFO    =>  Executing Step 1: '为不同用户层级匹配裂变玩法' (type=AGENT)  [task_group_aggregator_actor.py:192]
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:195: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:13,769 INFO    =>  --> Route: ResultAggregator for Step 1 (Agent)  [task_group_aggregator_actor.py:263]       
2026-01-08 10:11:13,769 WARNING =>  _get_merged_context called before task step_1 was registered  [result_aggregator_actor.py:547]
2026-01-08 10:11:13,773 INFO    =>  HTTP Request: GET http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status "HTTP/1.1 502 Bad Gateway"  [_client.py:1740]
2026-01-08 10:11:13,774 ERROR   =>  Failed to get signal status: 502 -   [event_bus.py:266]
2026-01-08 10:11:13,774 WARNING =>  Error checking signal status: Server error '502 Bad Gateway' for url 'http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502, continuing execution...  [result_aggregator_actor.py:103]
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:167: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:13,775 INFO    =>  ResultAggregator: Received task request for AgentActor: fission_game_match  [result_aggregator_actor.py:187]
2026-01-08 10:11:13,776 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:11:13,847 INFO    =>  Created new LeafActor for fission_game_match  [result_aggregator_actor.py:241]
2026-01-08 10:11:13,847 WARNING =>  Unknown message format: <class 'thespian.actors.ActorExitRequest'>  [execution_actor.py:56]
2026-01-08 10:11:13,848 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:11:13,994 INFO    =>  LeafActor initialized for fission_game_match  [leaf_actor.py:70]
2026-01-08 10:11:13,994 INFO    =>  [LeafActor] Handling task step_1: 内容：基于已创建的用户分层画像，分别为高净值客户与普通消 费者匹配最适合的裂变玩法。对于高净值客户，考...  [leaf_actor.py:94]
2026-01-08 10:11:13,994 INFO    =>  ExecutionActor initialized  [execution_actor.py:35]
E:\Data\Flora\tasks\agents\leaf_actor.py:164: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited  
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:13,994 INFO    =>  ⑪ 具体执行: task=step_1, capability=dify  [execution_actor.py:96]
E:\Data\Flora\tasks\capability_actors\execution_actor.py:106: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:13,995 INFO    =>  Executing Dify workflow for task step_1  [execution_actor.py:128]
2026-01-08 10:11:14,064 INFO    =>  Dify schema: {'opening_statement': '', 'suggested_questions': [], 'suggested_questions_after_answer': {'enabled': False}, 'speech_to_text': {'enabled': False}, 'text_to_speech': {'enabled': False, 'language': '', 'voice': ''}, 'retriever_resource': {'enabled': True}, 'annotation_reply': {'enabled': False}, 'more_like_this': {'enabled': False}, 'user_input_form': [{'text-input': {'label': '用户id', 'max_length': 48, 'options': [], 'required': True, 'type': 'text-input', 'variable': 'user_id'}}, {'text-input': {'label': '租户id', 'max_length': 48, 'options': [], 'required': True, 'type': 'text-input', 'variable': 'tenant_id'}}, {'text-input': {'variable': 'active_id', 'label': '活动ID', 'type': 'text-input', 'max_length': 128, 'required': True, 'options': [], 'placeholder': '', 'default': '', 'hint': ''}}], 'sensitive_word_avoidance': {'enabled': False}, 'file_upload': {'image': {'enabled': False, 'number_limits': 3, 'transfer_methods': ['local_file', 'remote_url']}, 'enabled': False, 'allowed_file_types': ['image'], 'allowed_file_extensions': ['.JPG', '.JPEG', '.PNG', '.GIF', '.WEBP', '.SVG'], 'allowed_file_upload_methods': ['local_file', 'remote_url'], 'number_limits': 3, 'fileUploadConfig': {'file_size_limit': 15, 'batch_count_limit': 5, 'image_file_size_limit': 10, 'video_file_size_limit': 100, 'audio_file_size_limit': 50, 'workflow_file_upload_limit': 10}}, 'system_parameters': {'image_file_size_limit': 10, 'video_file_size_limit': 100, 'audio_file_size_limit': 50, 'file_size_limit': 15, 'workflow_file_upload_limit': 10}}  [dify_connector.py:125]
2026-01-08 10:11:14,064 INFO    =>  Missing inputs: {'user_id': '用户id', 'tenant_id': '租户id', 'active_id': '活动ID'}  [dify_connector.py:158]
2026-01-08 10:11:14,064 INFO    =>  Full context: {'global_context': {}, 'enriched_context': {'__private_domain_task_group.step_1': ContextEntry(value={'step_results': {'step_1_output': {'status': 'SUCCESS', 'result': {'active_id': '664289733874159616'}}}}, source='ActorAddr-/A~a~a~a', task_path='//private_domain/task_group', timestamp=1767838220.3350613, confidence=1.0), '__private_domain_task_group_user_strat_fission_task_group.step_1': ContextEntry(value={'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":9,"msg":""}'}}, source='ActorAddr-/A~a~a~b~a~a~a', task_path='//private_domain/task_group/user_strat_fission/task_group', timestamp=1767838248.4642818, confidence=1.0)}, 'content': '基于已创建的用户分层画像，分别为高净值客户与普通消费者匹配 最适合的裂变玩法。对于高净值客户，考虑使用能体现其身份尊贵且参与感强的活动形式；对于普通消费者，则选择门槛低、易于传播的方式以 提高他们的参与度。', 'description': '为不同用户层级匹配裂变玩法', 'agent_id': 'fission_game_match', 'user_id': '<user_id:1>,<tenant_id:1>', 'original_inputs': {}}  [dify_connector.py:176]
2026-01-08 10:11:17,359 INFO    =>  params will be used: {'api_key': 'app-biWQJ47WcAcxiXouNOw68mwB', 'inputs': {}, 'agent_id': 'fission_game_match', 'user_id': '<user_id:1>,<tenant_id:1>', 'content': '基于已创建的用户分层画像，分别为高净值客户与普通消费 者匹配最适合的裂变玩法。对于高净值客户，考虑使用能体现其身份尊贵且参与感强的活动形式；对于普通消费者，则选择门槛低、易于传播的 方式以提高他们的参与度。', 'description': '为不同用户层级匹配裂变玩法', 'global_context': {}, 'enriched_context': {'__private_domain_task_group.step_1': ContextEntry(value={'step_results': {'step_1_output': {'status': 'SUCCESS', 'result': {'active_id': '664289733874159616'}}}}, source='ActorAddr-/A~a~a~a', task_path='//private_domain/task_group', timestamp=1767838220.3350613, confidence=1.0), '__private_domain_task_group_user_strat_fission_task_group.step_1': ContextEntry(value={'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":9,"msg":""}'}}, source='ActorAddr-/A~a~a~b~a~a~a', task_path='//private_domain/task_group/user_strat_fission/task_group', timestamp=1767838248.4642818, confidence=1.0)}}  [dify_connector.py:182]
2026-01-08 10:11:17,359 INFO    =>  Enhanced inputs: {}  [dify_connector.py:187]
2026-01-08 10:11:17,508 INFO    =>  Start resolving context for agent: fission_game_match (Path: 10000000000000000000000000000001 -> private_domain -> user_strat_fission -> strat_fission_strat -> fission_game_match)  [tree_context_resolver.py:78]        
2026-01-08 10:11:17,509 INFO    =>  Completed inputs: {'user_id': '1', 'tenant_id': '1', 'active_id': '664289733874159616'}  [dify_connector.py:190]
2026-01-08 10:11:24,522 INFO    =>  Dify response: {'task_id': 'c022aa23-72d4-40d3-b7ea-8d8c27bf1e36', 'workflow_run_id': 'b33411c7-2e16-4ec4-a56c-7dc727a6e669', 'data': {'id': 'b33411c7-2e16-4ec4-a56c-7dc727a6e669', 'workflow_id': 'c326639d-01db-4246-a53f-3963752671da', 'status': 'succeeded', 'outputs': {'body': '{"code":0,"data":13,"msg":""}'}, 'error': None, 'elapsed_time': 6.952587, 'total_tokens': 1385, 'total_steps': 8, 'created_at': 1767838277, 'finished_at': 1767838284}}  [dify_connector.py:246]
2026-01-08 10:11:24,523 INFO    =>  Dify outputs: {'body': '{"code":0,"data":13,"msg":""}'}  [dify_connector.py:285]
E:\Data\Flora\tasks\capability_actors\execution_actor.py:265: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
E:\Data\Flora\tasks\agents\leaf_actor.py:226: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited  
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:24,523 INFO    =>  Received TaskCompletedMessage for step_1: SUCCESS  [result_aggregator_actor.py:246]        
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:279: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:432: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:24,524 INFO    =>  Step 1 succeeded.  [task_group_aggregator_actor.py:314]
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:317: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:24,525 INFO    =>  Executing Step 2: '制定分层激励策略' (type=AGENT)  [task_group_aggregator_actor.py:192]    
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:195: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:24,525 INFO    =>  --> Route: ResultAggregator for Step 2 (Agent)  [task_group_aggregator_actor.py:263]       
2026-01-08 10:11:24,525 INFO    =>  Received ActorExitRequest, shutting down.  [result_aggregator_actor.py:113]
2026-01-08 10:11:24,526 WARNING =>  _get_merged_context called before task step_2 was registered  [result_aggregator_actor.py:547]
2026-01-08 10:11:24,533 INFO    =>  HTTP Request: GET http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status "HTTP/1.1 502 Bad Gateway"  [_client.py:1740]
2026-01-08 10:11:24,534 ERROR   =>  Failed to get signal status: 502 -   [event_bus.py:266]
2026-01-08 10:11:24,534 WARNING =>  Error checking signal status: Server error '502 Bad Gateway' for url 'http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502, continuing execution...  [result_aggregator_actor.py:103]
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:167: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:24,535 INFO    =>  ResultAggregator: Received task request for AgentActor: strat_incentives  [result_aggregator_actor.py:187]
2026-01-08 10:11:24,535 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:11:24,622 INFO    =>  Created new LeafActor for strat_incentives  [result_aggregator_actor.py:241]
2026-01-08 10:11:24,622 INFO    =>  Child actor exited: ActorAddr-/A~a~a~b~a~a~b~a~a~a, reason: {'_childAddr': <thespian.actors.ActorAddress object at 0x0000027F2613D670>}  [task_group_aggregator_actor.py:77]
2026-01-08 10:11:24,623 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:11:24,760 INFO    =>  LeafActor initialized for strat_incentives  [leaf_actor.py:70]
2026-01-08 10:11:24,760 INFO    =>  [LeafActor] Handling task step_2: 内容：针对已经定义好的两个主要用户群体（高净值客户和普通 消费者），设计差异化的激励方案。对高净值客户...  [leaf_actor.py:94]
2026-01-08 10:11:24,760 INFO    =>  ExecutionActor initialized  [execution_actor.py:35]
E:\Data\Flora\tasks\agents\leaf_actor.py:164: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited  
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:24,761 INFO    =>  Received ActorExitRequest, shutting down.  [leaf_actor.py:25]
2026-01-08 10:11:24,761 INFO    =>  ⑪ 具体执行: task=step_2, capability=dify  [execution_actor.py:96]
E:\Data\Flora\tasks\capability_actors\execution_actor.py:106: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:24,761 INFO    =>  Executing Dify workflow for task step_2  [execution_actor.py:128]
2026-01-08 10:11:24,823 INFO    =>  Dify schema: {'opening_statement': '', 'suggested_questions': [], 'suggested_questions_after_answer': {'enabled': False}, 'speech_to_text': {'enabled': False}, 'text_to_speech': {'enabled': False, 'language': '', 'voice': ''}, 'retriever_resource': {'enabled': True}, 'annotation_reply': {'enabled': False}, 'more_like_this': {'enabled': False}, 'user_input_form': [{'text-input': {'label': '用户id', 'max_length': 48, 'options': [], 'required': True, 'type': 'text-input', 'variable': 'user_id'}}, {'text-input': {'label': '租户id', 'max_length': 48, 'options': [], 'required': True, 'type': 'text-input', 'variable': 'tenant_id'}}, {'text-input': {'label': '已绘制的分层用户画像（需含各分层核心特征，如“高消费层：22-30岁女性，偏好套装+大额券；低活跃层：30-40岁宝妈，需低门槛互动”） 2. fission_core_goal：裂变核心目标（如“GMV转化/私域拉新/老用户激活”）', 'max_length': 48, 'options': [], 'required': False, 'type': 'text-input', 'variable': 'user_portraits'}}, {'text-input': {'label': '单份激励成本上限（如“高消费层≤50元，低活跃层≤15元”）', 'max_length': 48, 'options': [], 'required': False, 'type': 'text-input', 'variable': 'incentive_cost_cap'}}, {'text-input': {'label': '裂变核心场景（如：私域拉新、GMV转化、老用户激活）', 'max_length': 48, 'options': [], 'required': False, 'type': 'text-input', 'variable': 'fission_core'}}, {'text-input': {'label': '可提供的激励类型（如“现金红包/无门槛券/实物小样/会员时长/积分”）', 'max_length': 48, 'options': [], 'required': False, 'type': 'text-input', 'variable': 'incentive_types_available'}}, {'text-input': {'variable': 'active_id', 'label': '活动ID', 'type': 'text-input', 'max_length': 128, 'required': True, 'options': [], 'placeholder': '', 'default': '', 'hint': ''}}], 'sensitive_word_avoidance': {'enabled': False}, 'file_upload': {'image': {'enabled': False, 'number_limits': 3, 'transfer_methods': ['local_file', 'remote_url']}, 'enabled': False, 'allowed_file_types': ['image'], 'allowed_file_extensions': ['.JPG', '.JPEG', '.PNG', '.GIF', '.WEBP', '.SVG'], 'allowed_file_upload_methods': ['local_file', 'remote_url'], 'number_limits': 3, 'fileUploadConfig': {'file_size_limit': 15, 'batch_count_limit': 5, 'image_file_size_limit': 10, 'video_file_size_limit': 100, 'audio_file_size_limit': 50, 'workflow_file_upload_limit': 10}}, 'system_parameters': {'image_file_size_limit': 10, 'video_file_size_limit': 100, 'audio_file_size_limit': 50, 'file_size_limit': 15, 'workflow_file_upload_limit': 10}}  [dify_connector.py:125]
2026-01-08 10:11:24,824 INFO    =>  Missing inputs: {'user_id': '用户id', 'tenant_id': '租户id', 'active_id': '活动ID'}  [dify_connector.py:158]
2026-01-08 10:11:24,824 INFO    =>  Full context: {'global_context': {}, 'enriched_context': {'__private_domain_task_group.step_1': ContextEntry(value={'step_results': {'step_1_output': {'status': 'SUCCESS', 'result': {'active_id': '664289733874159616'}}}}, source='ActorAddr-/A~a~a~a', task_path='//private_domain/task_group', timestamp=1767838220.3350613, confidence=1.0), '__private_domain_task_group_user_strat_fission_task_group.step_1': ContextEntry(value={'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":9,"msg":""}'}}, source='ActorAddr-/A~a~a~b~a~a~a', task_path='//private_domain/task_group/user_strat_fission/task_group', timestamp=1767838248.4642818, confidence=1.0), '__private_domain_task_group_user_strat_fission_task_group_strat_fission_strat_task_group.step_1': ContextEntry(value={'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":13,"msg":""}'}}, source='ActorAddr-/A~a~a~b~a~a~b~a~a~a', task_path='//private_domain/task_group/user_strat_fission/task_group/strat_fission_strat/task_group', timestamp=1767838284.5253012, confidence=1.0)}, 'content': '针对已经定义好的两个主要用户群体（高净值客户和普通消费者），设计差异化的激励方案。对高净值客户可以提供独家优惠或限量版礼品作为奖励；而对于普通消费者，则通过发放小额红包或者积分来鼓励 他们参与到裂变活动中。', 'description': '制定分层激励策略', 'agent_id': 'strat_incentives', 'user_id': '<user_id:1>,<tenant_id:1>', 'original_inputs': {}}  [dify_connector.py:176]
2026-01-08 10:11:27,494 INFO    =>  params will be used: {'api_key': 'app-RrquaFK7AUav58HDtMWcsNgG', 'inputs': {}, 'agent_id': 'strat_incentives', 'user_id': '<user_id:1>,<tenant_id:1>', 'content': '针对已经定义好的两个主要用户群体（高净值客户和普通消费 者），设计差异化的激励方案。对高净值客户可以提供独家优惠或限量版礼品作为奖励；而对于普通消费者，则通过发放小额红包或者积分来鼓 励他们参与到裂变活动中。', 'description': '制定分层激励策略', 'global_context': {}, 'enriched_context': {'__private_domain_task_group.step_1': ContextEntry(value={'step_results': {'step_1_output': {'status': 'SUCCESS', 'result': {'active_id': '664289733874159616'}}}}, source='ActorAddr-/A~a~a~a', task_path='//private_domain/task_group', timestamp=1767838220.3350613, confidence=1.0), '__private_domain_task_group_user_strat_fission_task_group.step_1': ContextEntry(value={'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":9,"msg":""}'}}, source='ActorAddr-/A~a~a~b~a~a~a', task_path='//private_domain/task_group/user_strat_fission/task_group', timestamp=1767838248.4642818, confidence=1.0), '__private_domain_task_group_user_strat_fission_task_group_strat_fission_strat_task_group.step_1': ContextEntry(value={'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":13,"msg":""}'}}, source='ActorAddr-/A~a~a~b~a~a~b~a~a~a', task_path='//private_domain/task_group/user_strat_fission/task_group/strat_fission_strat/task_group', timestamp=1767838284.5253012, confidence=1.0)}}  [dify_connector.py:182]
2026-01-08 10:11:27,494 INFO    =>  Enhanced inputs: {}  [dify_connector.py:187]
2026-01-08 10:11:27,541 INFO    =>  Start resolving context for agent: strat_incentives (Path: 10000000000000000000000000000001 -> private_domain -> user_strat_fission -> strat_fission_strat -> strat_incentives)  [tree_context_resolver.py:78]
2026-01-08 10:11:27,542 INFO    =>  Completed inputs: {'user_id': '1', 'tenant_id': '1', 'active_id': '664289733874159616'}  [dify_connector.py:190]
2026-01-08 10:11:37,511 INFO    =>  Dify response: {'task_id': '7225689c-b36c-4981-8f5c-8001adb41f66', 'workflow_run_id': 'c0f4020d-7d34-4964-9ea1-d0a9e86900bd', 'data': {'id': 'c0f4020d-7d34-4964-9ea1-d0a9e86900bd', 'workflow_id': '7c9ae191-7466-43b9-b3dc-1ab912db0ddc', 'status': 'succeeded', 'outputs': {'body': '{"code":0,"data":12,"msg":""}'}, 'error': None, 'elapsed_time': 9.891138, 'total_tokens': 2101, 'total_steps': 8, 'created_at': 1767838287, 'finished_at': 1767838297}}  [dify_connector.py:246]
2026-01-08 10:11:37,512 INFO    =>  Dify outputs: {'body': '{"code":0,"data":12,"msg":""}'}  [dify_connector.py:285]
E:\Data\Flora\tasks\capability_actors\execution_actor.py:265: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
E:\Data\Flora\tasks\agents\leaf_actor.py:226: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited  
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:37,512 WARNING =>  Unknown message format: <class 'thespian.actors.ActorExitRequest'>  [execution_actor.py:56]
2026-01-08 10:11:37,512 INFO    =>  Received TaskCompletedMessage for step_2: SUCCESS  [result_aggregator_actor.py:246]        
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:279: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:432: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:37,512 INFO    =>  Step 2 succeeded.  [task_group_aggregator_actor.py:314]
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:317: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:37,513 INFO    =>  Executing Step 3: '定制化沟通材料' (type=AGENT)  [task_group_aggregator_actor.py:192]      
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:195: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:37,513 INFO    =>  --> Route: ResultAggregator for Step 3 (Agent)  [task_group_aggregator_actor.py:263]       
2026-01-08 10:11:37,513 INFO    =>  Received ActorExitRequest, shutting down.  [result_aggregator_actor.py:113]
2026-01-08 10:11:37,513 WARNING =>  _get_merged_context called before task step_3 was registered  [result_aggregator_actor.py:547]
2026-01-08 10:11:37,534 INFO    =>  HTTP Request: GET http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status "HTTP/1.1 502 Bad Gateway"  [_client.py:1740]
2026-01-08 10:11:37,534 ERROR   =>  Failed to get signal status: 502 -   [event_bus.py:266]
2026-01-08 10:11:37,535 WARNING =>  Error checking signal status: Server error '502 Bad Gateway' for url 'http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502, continuing execution...  [result_aggregator_actor.py:103]
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:167: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:37,535 INFO    =>  ResultAggregator: Received task request for AgentActor: comm_scripts  [result_aggregator_actor.py:187]
2026-01-08 10:11:37,536 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:11:37,636 INFO    =>  Created new LeafActor for comm_scripts  [result_aggregator_actor.py:241]
2026-01-08 10:11:37,636 INFO    =>  Child actor exited: ActorAddr-/A~a~a~b~a~a~b~a~a~b, reason: {'_childAddr': <thespian.actors.ActorAddress object at 0x0000027F26742D80>}  [task_group_aggregator_actor.py:77]
2026-01-08 10:11:37,637 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:11:37,776 INFO    =>  LeafActor initialized for comm_scripts  [leaf_actor.py:70]
2026-01-08 10:11:37,776 INFO    =>  [LeafActor] Handling task step_3: 内容：结合前两步确定的裂变玩法及激励措施，为高净值客户和 普通消费者分别定制专属沟通话术和视觉素材。确...  [leaf_actor.py:94]
2026-01-08 10:11:37,777 INFO    =>  ExecutionActor initialized  [execution_actor.py:35]
E:\Data\Flora\tasks\agents\leaf_actor.py:164: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited  
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:37,777 INFO    =>  Received ActorExitRequest, shutting down.  [leaf_actor.py:25]
2026-01-08 10:11:37,778 INFO    =>  ⑪ 具体执行: task=step_3, capability=dify  [execution_actor.py:96]
E:\Data\Flora\tasks\capability_actors\execution_actor.py:106: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:37,778 INFO    =>  Executing Dify workflow for task step_3  [execution_actor.py:128]
2026-01-08 10:11:37,848 INFO    =>  Dify schema: {'opening_statement': '', 'suggested_questions': [], 'suggested_questions_after_answer': {'enabled': False}, 'speech_to_text': {'enabled': False}, 'text_to_speech': {'enabled': False, 'language': '', 'voice': ''}, 'retriever_resource': {'enabled': True}, 'annotation_reply': {'enabled': False}, 'more_like_this': {'enabled': False}, 'user_input_form': [{'text-input': {'label': '用户id', 'max_length': 48, 'options': [], 'required': True, 'type': 'text-input', 'variable': 'user_id'}}, {'text-input': {'label': '租户id', 'max_length': 48, 'options': [], 'required': True, 'type': 'text-input', 'variable': 'tenant_id'}}, {'paragraph': {'label': '活动规则详情：确保文案准确传递活动核心信息（如参与条件、奖励门槛） ，避免因规则模糊导致用户误解、放弃参与，同时让 “奖励吸引力” 成为文案重点，推动用户行动', 'max_length': 2048, 'options': [], 'required': False, 'type': 'paragraph', 'variable': 'fission_incentive_system_id'}}, {'text-input': {'variable': 'active_id', 'label': '活动ID', 'type': 'text-input', 'max_length': 128, 'required': True, 'options': [], 'placeholder': '', 'default': '', 'hint': ''}}], 'sensitive_word_avoidance': {'enabled': False}, 'file_upload': {'image': {'enabled': False, 'number_limits': 3, 'transfer_methods': ['local_file', 'remote_url']}, 'enabled': False, 'allowed_file_types': ['image'], 'allowed_file_extensions': ['.JPG', '.JPEG', '.PNG', '.GIF', '.WEBP', '.SVG'], 'allowed_file_upload_methods': ['local_file', 'remote_url'], 'number_limits': 3, 'fileUploadConfig': {'file_size_limit': 15, 'batch_count_limit': 5, 'image_file_size_limit': 10, 'video_file_size_limit': 100, 'audio_file_size_limit': 50, 'workflow_file_upload_limit': 10}}, 'system_parameters': {'image_file_size_limit': 10, 'video_file_size_limit': 100, 'audio_file_size_limit': 50, 'file_size_limit': 15, 'workflow_file_upload_limit': 10}}  [dify_connector.py:125]
2026-01-08 10:11:37,849 INFO    =>  Missing inputs: {'user_id': '用户id', 'tenant_id': '租户id', 'active_id': '活动ID'}  [dify_connector.py:158]
2026-01-08 10:11:37,849 INFO    =>  Full context: {'global_context': {}, 'enriched_context': {'__private_domain_task_group.step_1': ContextEntry(value={'step_results': {'step_1_output': {'status': 'SUCCESS', 'result': {'active_id': '664289733874159616'}}}}, source='ActorAddr-/A~a~a~a', task_path='//private_domain/task_group', timestamp=1767838220.3350613, confidence=1.0), '__private_domain_task_group_user_strat_fission_task_group.step_1': ContextEntry(value={'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":9,"msg":""}'}}, source='ActorAddr-/A~a~a~b~a~a~a', task_path='//private_domain/task_group/user_strat_fission/task_group', timestamp=1767838248.4642818, confidence=1.0), '__private_domain_task_group_user_strat_fission_task_group_strat_fission_strat_task_group.step_1': ContextEntry(value={'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":13,"msg":""}'}}, source='ActorAddr-/A~a~a~b~a~a~b~a~a~a', task_path='//private_domain/task_group/user_strat_fission/task_group/strat_fission_strat/task_group', timestamp=1767838284.5253012, confidence=1.0), '__private_domain_task_group_user_strat_fission_task_group_strat_fission_strat_task_group.step_2': ContextEntry(value={'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":12,"msg":""}'}}, source='ActorAddr-/A~a~a~b~a~a~b~a~a~b', task_path='//private_domain/task_group/user_strat_fission/task_group/strat_fission_strat/task_group', timestamp=1767838297.5133114, confidence=1.0)}, 'content': '结合前两步确定的裂变玩法及激励措施，为高净值客户和普 通消费者分别定制专属沟通话术和视觉素材。确保所有内容都符合各自群体的特点，并能够有效促进信息分享与转化。', 'description': '定制化沟通材料', 'agent_id': 'comm_scripts', 'user_id': '<user_id:1>,<tenant_id:1>', 'original_inputs': {}}  [dify_connector.py:176]
2026-01-08 10:11:41,722 INFO    =>  params will be used: {'api_key': 'app-IxAznVKxVZ8e0OrZgWrDDxfT', 'inputs': {}, 'agent_id': 'comm_scripts', 'user_id': '<user_id:1>,<tenant_id:1>', 'content': '结合前两步确定的裂变玩法及激励措施，为高净值客户和普通消费 者分别定制专属沟通话术和视觉素材。确保所有内容都符合各自群体的特点，并能够有效促进信息分享与转化。', 'description': '定制化沟通材料', 'global_context': {}, 'enriched_context': {'__private_domain_task_group.step_1': ContextEntry(value={'step_results': {'step_1_output': {'status': 'SUCCESS', 'result': {'active_id': '664289733874159616'}}}}, source='ActorAddr-/A~a~a~a', task_path='//private_domain/task_group', timestamp=1767838220.3350613, confidence=1.0), '__private_domain_task_group_user_strat_fission_task_group.step_1': ContextEntry(value={'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":9,"msg":""}'}}, source='ActorAddr-/A~a~a~b~a~a~a', task_path='//private_domain/task_group/user_strat_fission/task_group', timestamp=1767838248.4642818, confidence=1.0), '__private_domain_task_group_user_strat_fission_task_group_strat_fission_strat_task_group.step_1': ContextEntry(value={'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":13,"msg":""}'}}, source='ActorAddr-/A~a~a~b~a~a~b~a~a~a', task_path='//private_domain/task_group/user_strat_fission/task_group/strat_fission_strat/task_group', timestamp=1767838284.5253012, confidence=1.0), '__private_domain_task_group_user_strat_fission_task_group_strat_fission_strat_task_group.step_2': ContextEntry(value={'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":12,"msg":""}'}}, source='ActorAddr-/A~a~a~b~a~a~b~a~a~b', task_path='//private_domain/task_group/user_strat_fission/task_group/strat_fission_strat/task_group', timestamp=1767838297.5133114, confidence=1.0)}}  [dify_connector.py:182]
2026-01-08 10:11:41,722 INFO    =>  Enhanced inputs: {}  [dify_connector.py:187]
2026-01-08 10:11:41,757 INFO    =>  Start resolving context for agent: comm_scripts (Path: 10000000000000000000000000000001 -> private_domain -> user_strat_fission -> strat_fission_strat -> comm_scripts)  [tree_context_resolver.py:78]
2026-01-08 10:11:41,757 INFO    =>  Completed inputs: {'user_id': '1', 'tenant_id': '1', 'active_id': '664289733874159616'}  [dify_connector.py:190]
2026-01-08 10:11:58,516 INFO    =>  Dify response: {'task_id': 'efa981dc-27bb-4e66-af74-1fe409ede7b3', 'workflow_run_id': '23008fb4-06fc-4888-b711-cb58241320a6', 'data': {'id': '23008fb4-06fc-4888-b711-cb58241320a6', 'workflow_id': 'cdf2024b-aa44-4688-b8ee-ef13e7254df8', 'status': 'succeeded', 'outputs': {'body': '{"code":0,"data":12,"msg":""}'}, 'error': None, 'elapsed_time': 16.707011, 'total_tokens': 1651, 'total_steps': 7, 'created_at': 1767838302, 'finished_at': 1767838318}}  [dify_connector.py:246]
2026-01-08 10:11:58,517 INFO    =>  Dify outputs: {'body': '{"code":0,"data":12,"msg":""}'}  [dify_connector.py:285]
E:\Data\Flora\tasks\capability_actors\execution_actor.py:265: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
E:\Data\Flora\tasks\agents\leaf_actor.py:226: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited  
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:58,518 WARNING =>  Unknown message format: <class 'thespian.actors.ActorExitRequest'>  [execution_actor.py:56]
2026-01-08 10:11:58,518 INFO    =>  Received TaskCompletedMessage for step_3: SUCCESS  [result_aggregator_actor.py:246]        
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:279: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:432: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:58,518 INFO    =>  Step 3 succeeded.  [task_group_aggregator_actor.py:314]
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:317: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:58,518 INFO    =>  Workflow step_2 Completed.  [task_group_aggregator_actor.py:426]
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:429: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:58,519 INFO    =>  Received ActorExitRequest, shutting down.  [result_aggregator_actor.py:113]
E:\Data\Flora\tasks\agents\agent_actor.py:463: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited 
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:58,519 INFO    =>  Received ActorExitRequest, shutting down.  [task_group_aggregator_actor.py:73]
2026-01-08 10:11:58,519 INFO    =>  Received TaskCompletedMessage for step_2: SUCCESS  [result_aggregator_actor.py:246]        
2026-01-08 10:11:58,519 INFO    =>  Child actor exited: ActorAddr-/A~a~a~b~a~a~b~a~a, reason: {'_childAddr': <thespian.actors.ActorAddress object at 0x0000027F26742990>}  [agent_actor.py:68]
2026-01-08 10:11:58,519 INFO    =>  Received ActorExitRequest, shutting down.  [leaf_actor.py:25]
2026-01-08 10:11:58,519 INFO    =>  Step 2 succeeded.  [task_group_aggregator_actor.py:314]
2026-01-08 10:11:58,519 INFO    =>  Workflow step_2 Completed.  [task_group_aggregator_actor.py:426]
2026-01-08 10:11:58,519 INFO    =>  Received ActorExitRequest, shutting down.  [result_aggregator_actor.py:113]
2026-01-08 10:11:58,520 INFO    =>  Received ActorExitRequest, shutting down.  [task_group_aggregator_actor.py:73]
2026-01-08 10:11:58,520 WARNING =>  Unknown message format: <class 'thespian.actors.ActorExitRequest'>  [execution_actor.py:56]
2026-01-08 10:11:58,520 INFO    =>  Received TaskCompletedMessage for step_2: SUCCESS  [result_aggregator_actor.py:246]        
2026-01-08 10:11:58,521 INFO    =>  Child actor exited: ActorAddr-/A~a~a~b~a~a, reason: {'_childAddr': <thespian.actors.ActorAddress object at 0x0000027F2670F860>}  [agent_actor.py:68]
2026-01-08 10:11:58,521 INFO    =>  Received ActorExitRequest, shutting down.  [agent_actor.py:64]
2026-01-08 10:11:58,521 INFO    =>  Step 2 succeeded.  [task_group_aggregator_actor.py:314]
2026-01-08 10:11:58,521 INFO    =>  Executing Step 3: '撰写营销文案' (type=AGENT)  [task_group_aggregator_actor.py:192]        
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:195: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:58,521 INFO    =>  --> Route: ResultAggregator for Step 3 (Agent)  [task_group_aggregator_actor.py:263]       
2026-01-08 10:11:58,521 INFO    =>  Received ActorExitRequest, shutting down.  [result_aggregator_actor.py:113]
2026-01-08 10:11:58,521 WARNING =>  _get_merged_context called before task step_3 was registered  [result_aggregator_actor.py:547]
2026-01-08 10:11:58,526 INFO    =>  HTTP Request: GET http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status "HTTP/1.1 502 Bad Gateway"  [_client.py:1740]
2026-01-08 10:11:58,527 ERROR   =>  Failed to get signal status: 502 -   [event_bus.py:266]
2026-01-08 10:11:58,527 WARNING =>  Error checking signal status: Server error '502 Bad Gateway' for url 'http://localhost:8004/v1/commands/00209d37-fb95-4920-b970-bd70ed013502/status'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502, continuing execution...  [result_aggregator_actor.py:103]
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:167: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:58,528 INFO    =>  ResultAggregator: Received task request for AgentActor: copy_planning  [result_aggregator_actor.py:187]
2026-01-08 10:11:58,529 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:11:58,663 INFO    =>  Created new LeafActor for copy_planning  [result_aggregator_actor.py:241]
2026-01-08 10:11:58,664 INFO    =>  Child actor exited: ActorAddr-/A~a~a~b, reason: {'_childAddr': <thespian.actors.ActorAddress object at 0x0000027F260CF3E0>}  [task_group_aggregator_actor.py:77]
2026-01-08 10:11:58,665 INFO    =>  树形结构管理器初始化成功  [tree_manager.py:35]
2026-01-08 10:11:58,771 INFO    =>  LeafActor initialized for copy_planning  [leaf_actor.py:70]
2026-01-08 10:11:58,772 INFO    =>  [LeafActor] Handling task step_3: 内容：根据前两步的结果，编写一系列吸引潜在买家注意的推广 文案，内容需围绕投影仪的特点及其带来的生活方...  [leaf_actor.py:94]
2026-01-08 10:11:58,772 INFO    =>  ExecutionActor initialized  [execution_actor.py:35]
E:\Data\Flora\tasks\agents\leaf_actor.py:164: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited  
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:58,772 INFO    =>  Received ActorExitRequest, shutting down.  [agent_actor.py:64]
2026-01-08 10:11:58,772 INFO    =>  ⑪ 具体执行: task=step_3, capability=dify  [execution_actor.py:96]
E:\Data\Flora\tasks\capability_actors\execution_actor.py:106: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:11:58,773 INFO    =>  Executing Dify workflow for task step_3  [execution_actor.py:128]
2026-01-08 10:11:58,829 INFO    =>  Dify schema: {'opening_statement': '', 'suggested_questions': [], 'suggested_questions_after_answer': {'enabled': False}, 'speech_to_text': {'enabled': False}, 'text_to_speech': {'enabled': False, 'language': '', 'voice': ''}, 'retriever_resource': {'enabled': True}, 'annotation_reply': {'enabled': False}, 'more_like_this': {'enabled': False}, 'user_input_form': [{'text-input': {'label': '用户id', 'max_length': 48, 'options': [], 'required': True, 'type': 'text-input', 'variable': 'user_id'}}, {'text-input': {'label': '租户id', 'max_length': 48, 'options': [], 'required': True, 'type': 'text-input', 'variable': 'tenant_id'}}, {'paragraph': {'label': '核心裂变玩法', 'max_length': 2048, 'options': [], 'required': False, 'type': 'paragraph', 'variable': 'fission_game_mode_id'}}, {'paragraph': {'label': '分层用户及其玩法', 'max_length': 2048, 'options': [], 'required': False, 'type': 'paragraph', 'variable': 'fission_layered_gameplay_id'}}, {'paragraph': {'label': '核心目标', 'max_length': 512, 'options': [], 'required': False, 'type': 'paragraph', 'variable': 'fission_plan_set_id'}}, {'text-input': {'variable': 'active_id', 'label': '活动ID', 'type': 'text-input', 'max_length': 128, 'required': True, 'options': [], 'placeholder': '', 'default': '', 'hint': ''}}], 'sensitive_word_avoidance': {'enabled': False}, 'file_upload': {'image': {'enabled': False, 'number_limits': 3, 'transfer_methods': ['local_file', 'remote_url']}, 'enabled': False, 'allowed_file_types': ['image'], 'allowed_file_extensions': ['.JPG', '.JPEG', '.PNG', '.GIF', '.WEBP', '.SVG'], 'allowed_file_upload_methods': ['local_file', 'remote_url'], 'number_limits': 3, 'fileUploadConfig': {'file_size_limit': 15, 'batch_count_limit': 5, 'image_file_size_limit': 10, 'video_file_size_limit': 100, 'audio_file_size_limit': 50, 'workflow_file_upload_limit': 10}}, 'system_parameters': {'image_file_size_limit': 10, 'video_file_size_limit': 100, 'audio_file_size_limit': 50, 'file_size_limit': 15, 'workflow_file_upload_limit': 10}}  [dify_connector.py:125]
2026-01-08 10:11:58,829 INFO    =>  Missing inputs: {'user_id': '用户id', 'tenant_id': '租户id', 'active_id': '活动ID'}  [dify_connector.py:158]
2026-01-08 10:11:58,829 INFO    =>  Full context: {'global_context': {}, 'enriched_context': {'__private_domain_task_group.step_1': ContextEntry(value={'step_results': {'step_1_output': {'status': 'SUCCESS', 'result': {'active_id': '664289733874159616'}}}}, source='ActorAddr-/A~a~a~a', task_path='//private_domain/task_group', timestamp=1767838220.3350613, confidence=1.0), '__private_domain_task_group.step_2': ContextEntry(value={'step_results': {'step_1_output': {'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":9,"msg":""}'}}, 'step_2_output': {'step_results': {'step_1_output': {'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":13,"msg":""}'}}, 'step_2_output': {'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":12,"msg":""}'}}, 'step_3_output': {'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":12,"msg":""}'}}}}}}, source='ActorAddr-/A~a~a~b', task_path='//private_domain/task_group', timestamp=1767838318.5214167, confidence=1.0)}, 'content': '根据前两步的结果，编写一系列吸引潜在买家注意的推广文案，内容需围绕投影仪的特点及其带来的生活方式改变，旨在降低获客成本并提高活动转化率。', 'description': '撰写营销文案', 'agent_id': 'copy_planning', 'user_id': '<user_id:1>,<tenant_id:1>', 'original_inputs': {}}  [dify_connector.py:176]
2026-01-08 10:12:02,669 INFO    =>  params will be used: {'api_key': 'app-zH133VOxSTZqNTQwYGkvSfdb', 'inputs': {}, 'agent_id': 'copy_planning', 'user_id': '<user_id:1>,<tenant_id:1>', 'content': '根据前两步的结果，编写一系列吸引潜在买家注意的推广文案，内容需围绕投影仪的特点及其带来的生活方式改变，旨在降低获客成本并提高活动转化率。', 'description': '撰写营销文案', 'global_context': {}, 'enriched_context': {'__private_domain_task_group.step_1': ContextEntry(value={'step_results': {'step_1_output': {'status': 'SUCCESS', 'result': {'active_id': '664289733874159616'}}}}, source='ActorAddr-/A~a~a~a', task_path='//private_domain/task_group', timestamp=1767838220.3350613, confidence=1.0), '__private_domain_task_group.step_2': ContextEntry(value={'step_results': {'step_1_output': {'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":9,"msg":""}'}}, 'step_2_output': {'step_results': {'step_1_output': {'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":13,"msg":""}'}}, 'step_2_output': {'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":12,"msg":""}'}}, 'step_3_output': {'status': 'SUCCESS', 'result': {'body': '{"code":0,"data":12,"msg":""}'}}}}}}, source='ActorAddr-/A~a~a~b', task_path='//private_domain/task_group', timestamp=1767838318.5214167, confidence=1.0)}}  [dify_connector.py:182]
2026-01-08 10:12:02,670 INFO    =>  Enhanced inputs: {}  [dify_connector.py:187]
2026-01-08 10:12:02,777 INFO    =>  Start resolving context for agent: copy_planning (Path: 10000000000000000000000000000001 -> private_domain -> copy_planning)  [tree_context_resolver.py:78]
2026-01-08 10:12:02,777 INFO    =>  Completed inputs: {'user_id': '1', 'tenant_id': '1', 'active_id': '664289733874159616'}  [dify_connector.py:190]
2026-01-08 10:12:09,495 INFO    =>  Dify response: {'task_id': 'd39b0c64-3a30-417b-9f54-819284b540fd', 'workflow_run_id': 'c5e5ee17-bd5c-4a31-a555-7cedbb00f951', 'data': {'id': 'c5e5ee17-bd5c-4a31-a555-7cedbb00f951', 'workflow_id': '3526d163-83ee-4d0a-ae7a-be548a89fdc5', 'status': 'succeeded', 'outputs': {'body': '{"code":0,"data":11,"msg":""}'}, 'error': None, 'elapsed_time': 6.652633, 'total_tokens': 1474, 'total_steps': 7, 'created_at': 1767838323, 'finished_at': 1767838329}}  [dify_connector.py:246]
2026-01-08 10:12:09,496 INFO    =>  Dify outputs: {'body': '{"code":0,"data":11,"msg":""}'}  [dify_connector.py:285]
E:\Data\Flora\tasks\capability_actors\execution_actor.py:265: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
E:\Data\Flora\tasks\agents\leaf_actor.py:226: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited  
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:12:09,496 INFO    =>  Received TaskCompletedMessage for step_3: SUCCESS  [result_aggregator_actor.py:246]        
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:279: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
E:\Data\Flora\tasks\capability_actors\result_aggregator_actor.py:432: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:12:09,497 INFO    =>  Step 3 succeeded.  [task_group_aggregator_actor.py:314]
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:317: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:12:09,498 INFO    =>  Workflow 46cdc530-d522-4a7c-bd0c-59091c5b419c Completed.  [task_group_aggregator_actor.py:426]
E:\Data\Flora\tasks\capability_actors\task_group_aggregator_actor.py:429: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:12:09,498 INFO    =>  Received ActorExitRequest, shutting down.  [result_aggregator_actor.py:113]
E:\Data\Flora\tasks\agents\agent_actor.py:463: RuntimeWarning: coroutine 'EventPublisher.publish_task_event' was never awaited 
  event_bus.publish_task_event(
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
2026-01-08 10:12:09,499 INFO    =>  Received ActorExitRequest, shutting down.  [task_group_aggregator_actor.py:73]
2026-01-08 10:12:09,499 INFO    =>  Child actor exited: ActorAddr-/A~a~a, reason: {'_childAddr': <thespian.actors.ActorAddress object at 0x0000027F257B94F0>}  [agent_actor.py:68]
2026-01-08 10:12:09,499 INFO    =>  Received ActorExitRequest, shutting down.  [leaf_actor.py:25]
2026-01-08 10:12:09,499 WARNING =>  Unknown message format: <class 'thespian.actors.ActorExitRequest'>  [execution_actor.py:56]