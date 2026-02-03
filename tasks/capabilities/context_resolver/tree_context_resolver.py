"""上下文解析器实现"""
from typing import Dict, Any, List, Optional, Tuple
from ..capability_base import CapabilityBase
import logging
import json
import re
from .interface import IContextResolverCapbility 
import logging
logger = logging.getLogger(__name__)

class TreeContextResolver(IContextResolverCapbility):
    """
    具体的实现类：
    与 TreeManager 集成，利用树形结构进行语义化的层级搜索。
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = {}
        
        # 依赖项：现在使用 tree_manager
        self.tree_manager = None 
        self.llm_client = None
        
        self.variable_pattern = re.compile(r'\$\{([^}]+)\}')
        self.context_templates = {}

    def get_capability_type(self) -> str:
        return 'tree_context_resolver'

    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.logger.info("TreeContextResolver initialized with config.")

    def shutdown(self) -> None:
        self.context_templates.clear()
        self.tree_manager = None
        self.logger.info("TreeContextResolver shutdown.")

    def set_dependencies(self, tree_manager: Any=None, llm_client: Any = None) -> None:
        """
        注入 TreeManager 单例和 LLM 客户端
        """
        if tree_manager:
            self.tree_manager = tree_manager
        else:
            from agents.tree.tree_manager import treeManager
            self.tree_manager=treeManager
        if llm_client:
            self.llm_client = llm_client
        else:
            from ..llm.interface import ILLMCapability
            from .. import get_capability
            self.llm_client:ILLMCapability = get_capability("llm",ILLMCapability)
        
        self.logger.info("Dependencies (TreeManager, LLM) injected.")

    # ----------------------------------------------------------
    # 核心逻辑：基于 TreeManager 的寻址
    # ----------------------------------------------------------

    def resolve_context(self, context_requirements: Dict[str, str], agent_id: str) -> Dict[str, Any]:
        """
        解析上下文需求：
        1. 先通过 _resolve_kv_via_layered_search 定位数据所在位置（库/表/列）；
        2. 若定位成功，则使用 VannaTextToSQL 执行真实查询，返回实际数据。
        """
        if not self.tree_manager or not self.llm_client:
            self.set_dependencies()

        result = {}
        try:
            path = self.tree_manager.get_full_path(agent_id)
            path_str = " -> ".join(path)
        except:
            path_str = agent_id

        self.logger.info(f"Start resolving context for agent: {agent_id} (Path: {path_str})")

        # 获取当前 Agent 的基础元信息（用于 fallback 或日志）
        base_agent_meta = {}
        try:
            base_agent_meta = self.tree_manager.get_agent_meta(agent_id) or {}
        except Exception as e:
            self.logger.warning(f"Could not retrieve base agent meta for {agent_id}: {e}")

        for key, value_desc in context_requirements.items():
            try:
                query = f"需查找数据: '{key}', 业务描述: '{value_desc}'"
                
                # Step 1: 定位数据位置（库、表、列等）
                leaf_meta = self._resolve_kv_via_layered_search(agent_id, query, key)
                if not leaf_meta:
                    leaf_meta = self._resolve_kv_globally(query)

                
                if not leaf_meta:
                    self.logger.warning(f"❌ Unresolved '{key}' (Desc: {value_desc}) – no location found")
                    result[key] = None
                    continue

                # Step 2: 如果定位成功，尝试用 Vanna 查询真实数据
                self.logger.info(f"📍 Located '{key}' at: {leaf_meta}")
                
                # 构造 Vanna 所需的 agent_meta 格式：database = "db.table"
                db_name = leaf_meta.get("database") or leaf_meta.get("db")
                table_name = leaf_meta.get("table") or leaf_meta.get("tbl")

                # Some nodes store "db.table" in database field.
                if db_name and not table_name and "." in str(db_name):
                    parts = str(db_name).split(".", 1)
                    db_name = parts[0].strip() or None
                    table_name = parts[1].strip() or None

                if not db_name or not table_name:
                    db_name, table_name = self._extract_db_table_from_meta(leaf_meta)
                
                if not db_name or not table_name:
                    self.logger.warning(f"⚠️ Incomplete location info for '{key}': {leaf_meta}, skip Vanna query")
                    result[key] = None
                    continue

                vanna_agent_meta = {
                    "database": f"{db_name}.{table_name}",
                    "database_type": leaf_meta.get("database_type", base_agent_meta.get("database_type", "mysql"))
                }

                # 初始化 Vanna 能力
                from .. import get_capability
                from ..text_to_sql.text_to_sql import ITextToSQLCapability
                try:
                    text_to_sql_cap: ITextToSQLCapability = get_capability(
                        "text_to_sql", ITextToSQLCapability
                    )
                except Exception as e:
                    self.logger.warning(f"Text-to-SQL capability unavailable: {e}")
                    result[key] = None
                    continue

                text_to_sql_cap.initialize({
                    "agent_id": agent_id,
                    "agent_meta": vanna_agent_meta
                })

                try:
                    # 使用原始业务描述作为查询语句
                    response = text_to_sql_cap.execute_query(user_query=value_desc, context=None)
                    records = response.get("result", [])
                    
                    if records:
                        # 使用 LLM 从查询结果中提取符合业务需求的值
                        resolved_value = self._extract_value_from_records(
                            key=key,
                            value_desc=value_desc,
                            records=records
                        )
                        result[key] = resolved_value
                        self.logger.info(f"✅ Resolved '{key}' with real data (rows: {len(records)}, extracted: {type(resolved_value).__name__})")
                    else:
                        self.logger.warning(f"🔍 Located but no data returned for '{key}'")
                        result[key] = None  # 或保留 leaf_meta，视业务而定
                        
                finally:
                    # 确保释放资源
                    text_to_sql_cap.shutdown()

            except Exception as e:
                self.logger.error(f"Error resolving key '{key}': {str(e)}", exc_info=True)
                result[key] = None

        return result

    def _extract_db_table_from_meta(self, meta: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """
        Try to extract database/table info from datascope or other metadata.
        """
        db_name = None
        table_name = None
        datascope = meta.get("datascope") or meta.get("data_scope")

        if isinstance(datascope, str) and datascope.strip():
            try:
                datascope = json.loads(datascope)
            except Exception:
                # Fallback: allow "db.table" literal in datascope string.
                if "." in datascope:
                    parts = datascope.split(".", 1)
                    db_name = parts[0].strip() or None
                    table_name = parts[1].strip() or None

        if isinstance(datascope, dict):
            db_name = db_name or datascope.get("database") or datascope.get("db") or datascope.get("schema")
            table_name = (
                table_name
                or datascope.get("table")
                or datascope.get("tbl")
                or datascope.get("table_name")
            )
            # Allow database value to be "db.table".
            if db_name and not table_name and "." in str(db_name):
                parts = str(db_name).split(".", 1)
                db_name = parts[0].strip() or None
                table_name = parts[1].strip() or None

        return db_name, table_name
    
    def _extract_value_from_records(
        self,
        key: str,
        value_desc: str,
        records: list
    ) -> Any:
        """
        使用 LLM 从 SQL 查询结果中提取符合业务需求的值。

        Args:
            key: 参数名称，如 "user_id"
            value_desc: 业务描述，如 "当前登录用户的ID"
            records: SQL 查询返回的记录列表

        Returns:
            提取后的值，可能是单值、列表或字典
        """
        # 快速路径：单行单列直接返回
        if len(records) == 1:
            row = records[0]
            if isinstance(row, dict) and len(row) == 1:
                # 单行单列，直接返回值
                return list(row.values())[0]
            elif not isinstance(row, dict):
                # 单个值
                return row

        # 快速路径：单列多行，返回值列表
        if records and isinstance(records[0], dict) and len(records[0]) == 1:
            col_name = list(records[0].keys())[0]
            values = [r.get(col_name) for r in records if r.get(col_name) is not None]
            if len(values) == 1:
                return values[0]
            return values

        # 复杂情况：多行多列，使用 LLM 提取
        if not self.llm_client:
            self.set_dependencies()
            if not self.llm_client:
                self.logger.warning("LLM client unavailable, returning first record")
                return records[0] if len(records) == 1 else records

        # 限制记录数量，避免 prompt 过长
        max_records = 20
        truncated = records[:max_records]
        truncated_note = f"（仅展示前 {max_records} 条，共 {len(records)} 条）" if len(records) > max_records else ""
        logger.info(f"LLM prompting with {truncated} records")

        # 格式化记录为可读文本（处理不可序列化的类型）
        def make_json_serializable(obj):
            """递归处理不可 JSON 序列化的类型"""
            if isinstance(obj, bytes):
                # bytes 转为字符串（尝试 UTF-8 解码，失败则用 hex）
                try:
                    return obj.decode('utf-8')
                except UnicodeDecodeError:
                    return obj.hex()
            elif isinstance(obj, dict):
                return {k: make_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [make_json_serializable(item) for item in obj]
            elif hasattr(obj, 'isoformat'):
                # datetime/date/time 对象
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):
                # 其他对象尝试转为字典
                return make_json_serializable(obj.__dict__)
            else:
                return obj

        serializable_records = make_json_serializable(truncated)
        records_text = json.dumps(serializable_records, ensure_ascii=False, indent=2)

        prompt = f"""你是一个数据提取助手。请根据业务需求，从 SQL 查询结果中提取出最合适的值。

【业务需求】
参数名: {key}
描述: {value_desc}

【SQL 查询结果】{truncated_note}
{records_text}

【提取规则】
1. 根据业务描述判断需要的是单个值、多个值还是完整记录
2. 如果需要单个值（如 ID、名称），直接输出该值
3. 如果需要多个值（如 ID 列表），输出 JSON 数组格式
4. 如果需要完整记录，输出 JSON 对象或数组
5. 如果查询结果与业务需求不匹配，输出 null

【输出格式】
只输出提取的值，不要任何解释。如果是字符串直接输出，如果是复杂结构输出 JSON。
"""

        try:
            response = self.llm_client.generate(prompt=prompt)
            result_text = response.strip() if isinstance(response, str) else str(response).strip()

            # 尝试解析为 JSON
            if result_text.lower() == "null":
                return None

            # 尝试 JSON 解析
            try:
                parsed = json.loads(result_text)
                return parsed
            except json.JSONDecodeError:
                # 不是 JSON，作为字符串返回
                # 去除可能的引号
                if result_text.startswith('"') and result_text.endswith('"'):
                    return result_text[1:-1]
                if result_text.startswith("'") and result_text.endswith("'"):
                    return result_text[1:-1]
                return result_text

        except Exception as e:
            self.logger.error(f"LLM extraction failed for '{key}': {e}")
            # 降级：返回第一条记录或全部
            return records[0] if len(records) == 1 else records


    def _resolve_kv_via_layered_search(self, start_agent_id: str, query: str, key: str) -> Optional[Dict]:
        """
        适配 TreeManager 的层级搜索算法
        """
        # 1. 初始定位：获取 start_agent 的父节点，以确定初始的"兄弟层"
        parent_id = self.tree_manager.get_parent(start_agent_id)
        
        # 用于防止死循环（虽然 TreeManager 内部有防环，但搜索逻辑层也保留一份保险）
        visited_layers = set()
        
        # 记录当前视角的节点，用于向上回溯时定位
        current_focus_node = start_agent_id

        while True:
            # --- 1. 确定当前搜索层 (Layer) ---
            if parent_id is None:
                # 核心变更：利用 TreeManager.get_root_agents() 获取根层
                self.logger.debug(f"Searching Root Layer for: {key}")
                current_layer = self.tree_manager.get_root_agents()
                
                # 如果当前聚焦的节点本身就是根节点，且在根层也找不到，循环通常会在后面 Break
            else:
                # 获取父节点的所有子节点（即当前层）
                current_layer = self.tree_manager.get_children(parent_id)

            # --- 防死循环检查 ---
            layer_sig = tuple(sorted(current_layer))
            if layer_sig in visited_layers:
                self.logger.warning("Cycle detected in search layer. Stopping.")
                break
            visited_layers.add(layer_sig)

            # --- 2. 在当前层进行语义匹配 ---
            matched_node_id = self._semantic_match_for_layer(query, current_layer)

            # --- 3. 匹配结果处理 ---
            if matched_node_id:
                # >> 命中分支 >>
                # 使用 TreeManager 获取元数据
                node_meta = self.tree_manager.get_agent_meta(matched_node_id)
                
                # 使用 TreeManager 判断是否叶子
                is_leaf = self.tree_manager.is_leaf_agent(matched_node_id)
                
                self.logger.debug(f"Match found: {matched_node_id} (Is Leaf: {is_leaf})")

                if is_leaf:
                    # 情况 A: 找到叶子节点 -> 成功
                    return node_meta
                else:
                    # 情况 B: 中间节点 -> 向下钻取 (Drill Down)
                    children = self.tree_manager.get_children(matched_node_id)
                    if not children:
                        break # 死胡同
                    
                    # 视角下沉：新的父节点是刚才匹配到的节点
                    parent_id = matched_node_id
                    # (current_focus_node 在向下钻取时其实不重要，因为下一轮直接取 parent 的 children)
                    continue
            else:
                # >> 未命中分支 >>
                # 情况 C: 当前层无匹配 -> 向上回溯 (Bubble Up)
                if parent_id is None:
                    # 已经在根层且未命中 -> 搜索全面失败
                    self.logger.debug("Reached root layer with no match.")
                    break
                
                # 移动视角向上：
                # 我们要找 parent 的兄弟，所以将视角聚焦到 parent
                current_focus_node = parent_id
                # 获取 parent 的 parent
                parent_id = self.tree_manager.get_parent(current_focus_node)
                continue
        
        return None
    
    
    def _resolve_kv_globally(self, query: str) -> Optional[Dict]:
        """
        全局兜底：在所有节点中进行关键词匹配，避免层级搜索无法定位时直接失败。
        """
        try:
            node_service = getattr(self.tree_manager, "node_service", None)
            if not node_service:
                return None
            nodes = node_service.get_all_nodes()
            node_ids = []
            for node in nodes:
                agent_id = node.get("agent_id")
                if not agent_id:
                    continue
                if any(
                    node.get(field)
                    for field in ("database", "db", "table", "tbl", "datascope", "data_scope")
                ):
                    node_ids.append(agent_id)
            if not node_ids:
                return None
            matched_node_id = self._semantic_match_for_layer(query, node_ids)
            if not matched_node_id:
                matched_node_id = self._fallback_keyword_match(query, node_ids)
            if not matched_node_id:
                return None
            return self.tree_manager.get_agent_meta(matched_node_id)
        except Exception as e:
            self.logger.warning(f"Global fallback failed: {e}")
            return None

    def _semantic_match_for_layer(self, query: str, node_ids: List[str]) -> Optional[str]:
        """
        [重构后] 使用 DashScope Qwen 判断当前层中哪个节点匹配 query。
        
        Args:
            query: 自然语言查询，如 "需查找数据: 'user_id', 业务描述: '当前登录用户'"
            node_ids: 当前层的节点ID列表 (List[str])
        
        Returns:
            匹配的 node_id (str)，若无匹配返回 None
        """
        if not node_ids:
            return None

        # 1. 准备候选节点数据
        candidates_text = []
        valid_node_ids = [] # 用于后续校验 LLM 返回的 ID 是否合法

        for nid in node_ids:
            # 从 TreeManager 获取元数据
            meta = self.tree_manager.get_agent_meta(nid)
            if not meta:
                continue

            # 提取关键信息，构建语义描述
            # 优先取 datascope，其次是 capability，最后是 description
            ds = meta.get("datascope") or meta.get("data_scope") or "无数据域定义"
            caps = meta.get("capability") or meta.get("capabilities") or []
            desc_text = meta.get("description", "")

            # 格式化各个字段
            ds_str = str(ds) if isinstance(ds, (dict, list)) else str(ds)
            cap_str = ", ".join(caps) if isinstance(caps, list) else str(caps)

            # 组合成一段利于 LLM 理解的文本
            # 格式: [ID] 数据: ...; 能力: ...; 描述: ...
            node_desc = (
                f"候选节点ID: {nid}\n"
                f"  - 数据范围: {ds_str}\n"
                f"  - 能力声明: {cap_str}\n"
                f"  - 节点描述: {desc_text}"
            )
            
            candidates_text.append(node_desc)
            valid_node_ids.append(nid)

        if not candidates_text:
            return None

        candidates_block = "\n\n".join(candidates_text)

        # 2. 构造 Prompt
        prompt = f"""你是一个分布式系统的数据路由语义匹配引擎。请根据以下数据需求，从候选节点列表中选择**最匹配的一个**。

数据需求:
{query}

候选节点列表:
---
{candidates_block}
---

请严格按照以下规则回答：
1. 分析哪个节点的"数据范围"或"节点描述"能覆盖上述数据需求。
2. 如果有匹配项，请只输出对应的 **节点ID** (例如: user_agent_01)。
3. 如果没有一个候选能合理满足该需求，或者相关性极低，请只输出 "none"。
4. 不要解释，不要加标点，不要包含任何多余文字。
"""

        # 3. 调用 LLM
        try:
            # 假设 self.llm_client 已经初始化并注入
            # 如果你用的是 requests 或特定的 SDK，在这里替换即可
            if not self.llm_client:
                self.logger.warning("LLM client missing, falling back to keyword match.")
                return self._fallback_keyword_match(query, valid_node_ids)

            # 调用大模型 (这里模拟你的 call_qwen 逻辑)
            # answer = self.call_qwen(prompt) 
            answer = self.llm_client.generate(prompt) 
            
            # 清理结果
            answer = answer.strip().replace("'", "").replace('"', "").replace("`", "")
            
            self.logger.info(f"Qwen semantic match result: '{answer}' for query: '{query}'")

            # 4. 结果校验
            if answer.lower() == "none":
                return None

            if answer in valid_node_ids:
                return answer
            else:
                self.logger.warning(f"Qwen returned invalid node_id: '{answer}'. Expected one of: {valid_node_ids}")
                return None

        except Exception as e:
            self.logger.error(f"Exception calling LLM/DashScope: {e}", exc_info=True)
            # 降级策略
            return self._fallback_keyword_match(query, valid_node_ids)

    def _fallback_keyword_match(self, query: str, node_ids: List[str]) -> Optional[str]:
        """
        简单的关键词匹配兜底策略
        """
        import re
        # 提取查询中的关键词（忽略标点）
        keywords = set(re.findall(r'[\w\u4e00-\u9fa5]+', query))
        best_node = None
        max_score = 0

        for nid in node_ids:
            meta = self.tree_manager.get_agent_meta(nid) or {}
            # 将所有元数据转为字符串进行搜索
            content = (
                str(meta.get("datascope", "")) + 
                str(meta.get("description", "")) + 
                str(meta.get("capability", ""))
            ).lower()
            
            score = sum(1 for kw in keywords if kw.lower() in content)
            
            if score > max_score:
                max_score = score
                best_node = nid
        
        return best_node if max_score > 0 else None





    def enhance_param_descriptions_with_context(
        self,
        base_param_descriptions: dict,
        current_inputs: dict
        ) -> dict:
        """
        使用 LLM 将基础参数描述增强为“带上下文”的描述。
        
        Args:
            base_param_descriptions: dict, e.g. {"template_id": "海报模板ID"}
            current_inputs: dict, e.g. {"tenant_id": "t_abc", "activity_id": "act_123"}
        
        Returns:
            dict: {"template_id": "海报模板ID，属于租户 t_abc 和活动 act_123"}
        """
        if not base_param_descriptions:
            return {}
        
        if not self.tree_manager or not self.llm_client:
            self.set_dependencies()

        # 构建上下文字符串（只保留非空、非敏感字段，可扩展过滤逻辑）
        context_items = []
        for k, v in current_inputs.items():
                
            # 2. 类型安全检查
            if not v or not isinstance(v, (str, int, float, bool)):
                continue
                
            v_str = str(v)
            
            # 3. 放宽长度限制：建议从 100 提升到 500 或 1000
            # 这样既能防住几万字的超大文本，又能容纳 URL 和 业务描述
            if len(v_str) < 1000:  
                context_items.append(f"{k}: {v_str}")
            else:
                # 可选：对于超长文本，截取前 100 个字符作为“摘要”放进去
                # 这样 LLM 至少知道有这个字段存在
                context_items.append(f"{k}: {v_str[:100]}... (content too long)")
        
        context_str = "\n".join(context_items) if context_items else "无可用上下文"

        # 构建参数列表字符串
        params_list = "\n".join([
            f"- {name}: {desc}" 
            for name, desc in base_param_descriptions.items()
        ])

        # === 构建 LLM Prompt ===
        prompt = f"""你是一个智能参数描述增强器。请根据以下信息，为每个参数生成增强版的中文描述。

    要求：
    - 输出必须是严格的 JSON 格式：{{ "参数名": "增强后的描述" }}
    - 在原始描述基础上，**自然融入所有可用的上下文信息**（如 tenant_id、activity_id 等）
    - 上下文信息用于帮助后续系统精准查询该参数值，请明确写出归属（例如：“属于租户xxxx 的活动 xxxx”）
    - 如果某个上下文与参数明显无关，可不强行加入
    - 描述要简洁、专业、可被自动化系统理解
    - **不要编造不存在的上下文**
    - **不要改变参数名**
    - 只输出 JSON，不要任何其他文字

    【可用上下文】
    {context_str}

    【待增强的参数及基础描述】
    {params_list}
    """

        # === 调用 LLM ===
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                parse_json=True,
            )
            result = response


            # 保证输出 key 与输入一致（防止 LLM 改名）
            aligned_result = {}
            for param_name in base_param_descriptions:
                if param_name in result:
                    aligned_result[param_name] = str(result[param_name]).strip()
                else:
                    # 回退：用原始描述 + 上下文拼接（保守策略）
                    fallback_desc = base_param_descriptions[param_name]
                    if context_items:
                        fallback_desc += "，上下文：" + "；".join(context_items)
                    aligned_result[param_name] = fallback_desc

            return aligned_result

        except Exception as e:
            print(f"[WARN] LLM 增强失败，使用回退策略: {e}")
            # 全部回退到基础描述 + 上下文拼接
            fallback = {}
            context_suffix = "（上下文：" + "；".join(context_items) + "）" if context_items else ""
            for name, desc in base_param_descriptions.items():
                fallback[name] = desc + context_suffix
            return fallback



    def pre_fill_known_params_with_llm(
        self,
        base_param_descriptions: dict,
        current_context_str: str
    ) -> tuple[dict, dict]:
        """
        使用 LLM 从自由文本上下文中提取可识别的参数值。

        Args:
            base_param_descriptions: {"user_id": "用户ID", "tenant_id": "租户ID", ...}
            current_context_str: 任意上下文，如 "当前用户是 test_admin_001，属于租户 test_tenant_001"

        Returns:
            (filled_values, remaining_params)
        """
        if not base_param_descriptions:
            return {}, {}

        if not self.tree_manager or not self.llm_client:
            self.set_dependencies()

        filled = {}

        # === 预处理：解析特殊格式的 user_id ===
        # 格式如: <user_id:1,tenant_id:1> 或 <user_id:1>,<tenant_id:1>
        parsed_ids = self._parse_user_id_format(current_context_str)
        if parsed_ids:
            for param_name in base_param_descriptions:
                if param_name in parsed_ids:
                    filled[param_name] = parsed_ids[param_name]
                    logger.info(f"Pre-filled '{param_name}' from special format: {parsed_ids[param_name]}")

        # 检查是否还有剩余参数需要 LLM 处理
        remaining_for_llm = {
            k: v for k, v in base_param_descriptions.items()
            if k not in filled
        }

        if not remaining_for_llm:
            return filled, {}

        # 构建参数说明
        params_info = "\n".join([
            f"- {name}: {desc}"
            for name, desc in remaining_for_llm.items()
        ])

        prompt = f"""你是一个参数值提取器。请从以下上下文中，尽可能提取出与目标参数匹配的具体值。

    要求：
    - 只提取明确提及或可合理推断的值；
    - 如果某个参数无法确定，不要猜测，直接跳过；
    - 输出必须是严格 JSON 格式：{{ "参数名": "提取的值" }}
    - 值必须是字符串；
    - 不要输出任何其他文字，包括解释、markdown、前缀。

    【目标参数定义】
    {params_info}

    【当前上下文】
    {current_context_str}
    """

        try:
            response = self.llm_client.generate(
                prompt=prompt,
                parse_json=True,
            )
            # text = response.output.text.strip()

            # 提取 JSON
            # json_match = re.search(r"\{.*\}", text, re.DOTALL)
            json_match = response
            if json_match:
                # extracted = json.loads(json_match.group(0))
                extracted = json_match
                # 只保留合法参数名 + 字符串值
                for k, v in extracted.items():
                    if k in remaining_for_llm and isinstance(v, str) and v.strip():
                        filled[k] = v.strip()
        except Exception as e:
            print(f"[WARN] LLM 预填充失败，跳过: {e}")

        # 分离已填充和剩余参数
        remaining = {
            k: v for k, v in base_param_descriptions.items()
            if k not in filled
        }

        return filled, remaining

    def _parse_user_id_format(self, context: any) -> dict:
        """
        解析特殊格式的 user_id 字符串

        支持格式:
        - <user_id:1,tenant_id:1>
        - <user_id:1>,<tenant_id:1>
        - 嵌套在字典中的 '_user_id': '<user_id:1,tenant_id:1>'

        Args:
            context: 上下文，可以是字符串或字典

        Returns:
            dict: 解析出的参数，如 {"user_id": "1", "tenant_id": "1"}
        """
        result = {}

        # 将 context 转换为字符串进行搜索
        # 使用安全的序列化方法，处理 ContextEntry 等不可序列化的对象
        context_str = self._safe_serialize_for_parsing(context)

        # 匹配模式: <key:value> 或 <key:value,key2:value2>
        # 模式1: <user_id:1,tenant_id:1>
        pattern1 = r'<([a-zA-Z_]+):([^,>]+)(?:,([a-zA-Z_]+):([^>]+))?>'
        matches = re.findall(pattern1, context_str)

        for match in matches:
            if match[0] and match[1]:
                result[match[0]] = match[1].strip()
            if match[2] and match[3]:
                result[match[2]] = match[3].strip()

        # 模式2: 单独的 <key:value>
        pattern2 = r'<([a-zA-Z_]+):([^<>]+)>'
        matches2 = re.findall(pattern2, context_str)
        for key, value in matches2:
            if key not in result:
                result[key] = value.strip()

        return result

    def _safe_serialize_for_parsing(self, obj: any) -> str:
        """
        安全地将对象序列化为字符串，用于正则匹配解析

        处理 ContextEntry、Pydantic BaseModel 等不可直接 JSON 序列化的对象

        Args:
            obj: 任意对象

        Returns:
            str: 序列化后的字符串
        """
        from pydantic import BaseModel

        def make_serializable(item: any) -> any:
            if item is None:
                return None
            if isinstance(item, (str, int, float, bool)):
                return item
            if isinstance(item, BaseModel):
                return item.model_dump()
            if isinstance(item, dict):
                return {k: make_serializable(v) for k, v in item.items()}
            if isinstance(item, (list, tuple)):
                return [make_serializable(i) for i in item]
            # 其他类型转为字符串
            try:
                return str(item)
            except Exception:
                return repr(item)

        try:
            serializable = make_serializable(obj)
            return json.dumps(serializable, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to serialize context for parsing: {e}")
            return str(obj)
    



    # ----------------------------------------------------------
    # 辅助功能
    # ----------------------------------------------------------

    def extract_context(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """保留原有基础提取逻辑"""
        base_ctx = {}
        fields = ['task_id', 'task_type', 'user_id', 'content', 'query', 'payload']
        for f in fields:
            if f in task_data:
                base_ctx[f] = task_data[f]
        return base_ctx

    def register_context_template(self, name: str, template: Dict) -> None:
        self.context_templates[name] = template

    def enrich_context_from_result(
        self, 
        msg: 'TaskMessage', 
        result: Any, 
        task_name: str = ""
    ) -> None:
        """
        从任务执行结果中富集上下文
        
        Args:
            msg: TaskMessage 对象，包含上下文信息
            result: 任务执行结果
            task_name: 任务名称（可选）
        """
        # 示例：从 result 中提取结构化字段
        if isinstance(result, dict):
            for key, value in result.items():
                # 自定义过滤逻辑：只保留基本类型和非空值
                if value is not None and isinstance(value, (str, int, float, bool, list, dict)):
                    # 生成安全键名，包含任务路径前缀
                    safe_key = f"{msg.task_path.replace('/', '_')}.{key}"
                    msg.enriched_context[safe_key] = value
        elif isinstance(result, (list, tuple)):
            # 处理列表结果，添加索引
            for i, item in enumerate(result[:10]):  # 最多取前10个元素
                if isinstance(item, dict):
                    for key, value in item.items():
                        if value is not None and isinstance(value, (str, int, float, bool)):
                            safe_key = f"{msg.task_path.replace('/', '_')}.item_{i}.{key}"
                            msg.enriched_context[safe_key] = value
        elif isinstance(result, (str, int, float, bool)):
            # 处理单个基本类型结果
            safe_key = f"{msg.task_path.replace('/', '_')}.result"
            msg.enriched_context[safe_key] = result

    def extract_params_for_capability(
        self, 
        capability: str, 
        enriched_context: Dict[str, Any], 
        global_context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        为特定能力智能提取参数
        
        Args:
            capability: 能力名称
            enriched_context: 富上下文
            global_context: 全局上下文
            
        Returns:
            (可用参数, 缺失参数列表)
        """
        # 这里需要根据实际的 CAPABILITY_SPECS 进行实现
        # 示例实现：基于简单的参数映射
        spec = self._get_capability_spec(capability)
        if not spec:
            return {}, []
            
        params = {}
        missing = []

        for param_name, config in spec["parameters"].items():
            found = False

            # 1. 优先从 enriched_context 匹配（支持别名）
            for alias in [param_name] + config.get("aliases", []):
                if alias in enriched_context:
                    params[param_name] = enriched_context[alias]
                    found = True
                    break

            # 2. 尝试从 global_context 获取（如 user_id）
            if not found and param_name in global_context:
                params[param_name] = global_context[param_name]
                found = True

            # 3. 仍缺失？
            if not found:
                missing.append(param_name)

        return params, missing
    
    def _get_capability_spec(self, capability: str) -> Optional[Dict[str, Any]]:
        """
        获取能力的参数规格
        
        Args:
            capability: 能力名称
            
        Returns:
            能力规格字典，包含 parameters 字段
        """
        # 这里需要根据实际系统中的能力规格进行实现
        # 示例：返回一个简单的默认规格
        return {
            "parameters": {
                # 默认参数规格，实际系统中应该从配置或注册中心获取
                "query": {"aliases": ["q", "question", "prompt"]},
                "user_id": {"aliases": ["uid", "user"]},
                "tenant_id": {"aliases": ["tid", "tenant"]}
            }
        }
    
    # ----------------------------------------------------------
    # 语义指针补全：消解代词歧义
    # ----------------------------------------------------------

    # 常见的模糊引用模式
    AMBIGUOUS_PATTERNS = [
        # 代词
        r'\b(他|她|它|他们|她们|它们)\b',
        r'\b(这个|那个|这些|那些|该|此|其)\b',
        # 指示性引用
        r'\b(上述|前述|所述|上面的|之前的|刚才的)\b',
        r'\b(该用户|该客户|该订单|该商品|该记录)\b',
        r'\b(当前用户|当前客户|当前订单)\b',
        # 英文代词
        r'\b(this|that|these|those|the)\s+(user|customer|order|item|record)\b',
        r'\b(he|she|it|they|him|her|them)\b',
    ]

    def resolve_semantic_pointers(
        self,
        param_descriptions: Dict[str, str],
        current_context: Dict[str, Any],
        agent_id: str,
        user_id: str,
        max_ancestor_levels: int = 3
    ) -> Dict[str, Dict[str, Any]]:
        """
        将模糊的参数描述转化为语义指针，消解代词歧义。

        核心机制：
        1. 检测参数描述中的模糊引用（代词、指示词）
        2. 沿树向上回溯父级 Agent 的业务记忆
        3. 使用 LLM 将局部意图与父级记忆进行语义对齐
        4. 生成自包含的语义指针

        Args:
            param_descriptions: 参数名 -> 原始描述，如 {"client_id": "该用户的ID"}
            current_context: 当前任务上下文，包含 content, description, global_context, enriched_context
            agent_id: 当前 Agent ID
            user_id: 用户 ID
            max_ancestor_levels: 最大回溯层数

        Returns:
            Dict[str, Dict]: 参数名 -> 语义指针信息
            {
                "client_id": {
                    "original_desc": "该用户的ID",
                    "resolved_desc": "昨天第二个需要退款资格检查的客户的ID",
                    "confidence": 0.9,
                    "resolution_chain": ["父级任务目标：处理昨天的第二个客户的投诉"],
                    "has_ambiguity": True
                }
            }
        """
        if not param_descriptions:
            return {}

        if not self.tree_manager or not self.llm_client:
            self.set_dependencies()

        result = {}

        # 1. 检测哪些参数包含模糊引用
        params_with_ambiguity = {}
        params_without_ambiguity = {}

        for param_name, desc in param_descriptions.items():
            if self._detect_ambiguous_references(desc):
                params_with_ambiguity[param_name] = desc
            else:
                params_without_ambiguity[param_name] = desc

        # 2. 对于没有模糊引用的参数，直接返回原始描述
        for param_name, desc in params_without_ambiguity.items():
            result[param_name] = {
                "original_desc": desc,
                "resolved_desc": desc,
                "confidence": 1.0,
                "resolution_chain": [],
                "has_ambiguity": False
            }

        # 3. 如果没有需要解析的参数，直接返回
        if not params_with_ambiguity:
            return result

        # 4. 获取父级上下文
        ancestor_context_summary = ""
        try:
            from ..llm_memory.unified_memory import UnifiedMemory
            from ..llm_memory.interface import IMemoryCapability
            from .. import get_capability

            memory_cap = get_capability("llm_memory", expected_type=IMemoryCapability)
            if hasattr(memory_cap, '_memory_manager') and memory_cap._memory_manager:
                ancestor_context_summary = memory_cap._memory_manager.build_ancestor_context_summary(
                    user_id=user_id,
                    agent_id=agent_id,
                    tree_manager=self.tree_manager,
                    max_levels=max_ancestor_levels
                )
        except Exception as e:
            self.logger.warning(f"Failed to get ancestor context: {e}")

        # 5. 如果没有父级上下文，尝试从当前上下文中解析
        if not ancestor_context_summary:
            # 使用当前上下文进行增强
            for param_name, desc in params_with_ambiguity.items():
                enhanced = self._enhance_with_current_context(
                    param_name, desc, current_context
                )
                result[param_name] = enhanced
            return result

        # 6. 使用 LLM 批量解析模糊引用
        resolved = self._batch_resolve_ambiguities(
            params_with_ambiguity,
            current_context,
            ancestor_context_summary
        )

        result.update(resolved)
        return result

    def _detect_ambiguous_references(self, text: str) -> bool:
        """
        检测文本中是否包含模糊引用（代词、指示词等）

        Args:
            text: 待检测的文本

        Returns:
            bool: 是否包含模糊引用
        """
        if not text:
            return False

        text_lower = text.lower()

        for pattern in self.AMBIGUOUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _enhance_with_current_context(
        self,
        param_name: str,
        original_desc: str,
        current_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        使用当前上下文增强参数描述（无父级上下文时的降级方案）

        Args:
            param_name: 参数名
            original_desc: 原始描述
            current_context: 当前上下文

        Returns:
            Dict: 语义指针信息
        """
        # 从当前上下文中提取相关信息
        context_parts = []

        content = current_context.get("content", "")
        description = current_context.get("description", "")
        global_ctx = current_context.get("global_context", {})
        enriched_ctx = current_context.get("enriched_context", {})

        if content:
            context_parts.append(f"任务内容: {content[:200]}")
        if description:
            context_parts.append(f"任务描述: {description[:200]}")

        # 从 global_context 和 enriched_context 中提取相关字段
        for ctx in [global_ctx, enriched_ctx]:
            if isinstance(ctx, dict):
                for k, v in ctx.items():
                    if isinstance(v, (str, int, float)) and v:
                        # 检查是否与参数名相关
                        if param_name.lower() in k.lower() or k.lower() in param_name.lower():
                            context_parts.append(f"{k}: {v}")

        if context_parts:
            enhanced_desc = f"{original_desc}（上下文：{'; '.join(context_parts[:3])}）"
        else:
            enhanced_desc = original_desc

        return {
            "original_desc": original_desc,
            "resolved_desc": enhanced_desc,
            "confidence": 0.5,  # 较低置信度，因为没有父级上下文
            "resolution_chain": context_parts[:3],
            "has_ambiguity": True
        }

    def _batch_resolve_ambiguities(
        self,
        params_with_ambiguity: Dict[str, str],
        current_context: Dict[str, Any],
        ancestor_context_summary: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        使用 LLM 批量解析模糊引用

        Args:
            params_with_ambiguity: 包含模糊引用的参数
            current_context: 当前上下文
            ancestor_context_summary: 父级上下文摘要

        Returns:
            Dict: 参数名 -> 语义指针信息
        """
        if not self.llm_client:
            # 降级：返回原始描述
            return {
                param_name: {
                    "original_desc": desc,
                    "resolved_desc": desc,
                    "confidence": 0.3,
                    "resolution_chain": [],
                    "has_ambiguity": True
                }
                for param_name, desc in params_with_ambiguity.items()
            }

        # 构建当前上下文摘要
        current_context_str = ""
        content = current_context.get("content", "")
        description = current_context.get("description", "")
        if content:
            current_context_str += f"任务内容: {content[:300]}\n"
        if description:
            current_context_str += f"任务描述: {description[:300]}\n"

        # 构建参数列表
        params_list = "\n".join([
            f"- {name}: {desc}"
            for name, desc in params_with_ambiguity.items()
        ])

        # 构建 Prompt
        prompt = f"""你是一个语义消歧助手。请根据父级业务上下文，将模糊的参数描述转化为精确的语义描述。

【当前任务上下文】
{current_context_str}

【父级业务记忆】（从近到远）
{ancestor_context_summary}

【待解析的参数】（包含模糊引用如"该用户"、"他"、"这个"等）
{params_list}

【任务】
1. 分析每个参数描述中的模糊引用
2. 从父级记忆中找到对应的精确信息
3. 生成自包含的语义描述，使得仅凭此描述就能精确定位数据

【输出格式】
严格输出 JSON，格式如下：
{{
    "参数名1": {{
        "resolved_desc": "完整的语义描述",
        "confidence": 0.0-1.0,
        "resolution_chain": ["从父级获取的关键信息1", "关键信息2"]
    }},
    "参数名2": {{
        ...
    }}
}}

【示例】
输入参数: client_id: "该用户的ID"
父级记忆: "任务目标：处理昨天的第二个客户的投诉"
输出:
{{
    "client_id": {{
        "resolved_desc": "昨天第二个需要处理投诉的客户的ID",
        "confidence": 0.9,
        "resolution_chain": ["父级任务目标：处理昨天的第二个客户的投诉"]
    }}
}}

注意：
- 如果无法从父级记忆中找到对应信息，confidence 设为 0.3-0.5
- resolved_desc 必须是自包含的，不能包含代词
- 只输出 JSON，不要任何解释
"""

        try:
            response = self.llm_client.generate(
                prompt=prompt,
                parse_json=True,
                max_tokens=1024
            )

            result = {}
            for param_name, original_desc in params_with_ambiguity.items():
                if param_name in response:
                    resolved_info = response[param_name]
                    result[param_name] = {
                        "original_desc": original_desc,
                        "resolved_desc": resolved_info.get("resolved_desc", original_desc),
                        "confidence": float(resolved_info.get("confidence", 0.5)),
                        "resolution_chain": resolved_info.get("resolution_chain", []),
                        "has_ambiguity": True
                    }
                else:
                    # LLM 未返回该参数，使用原始描述
                    result[param_name] = {
                        "original_desc": original_desc,
                        "resolved_desc": original_desc,
                        "confidence": 0.3,
                        "resolution_chain": [],
                        "has_ambiguity": True
                    }

            return result

        except Exception as e:
            self.logger.error(f"LLM batch resolve failed: {e}")
            # 降级：返回原始描述
            return {
                param_name: {
                    "original_desc": desc,
                    "resolved_desc": desc,
                    "confidence": 0.3,
                    "resolution_chain": [],
                    "has_ambiguity": True
                }
                for param_name, desc in params_with_ambiguity.items()
            }

    def enhance_param_descriptions_with_semantic_pointers(
        self,
        base_param_descriptions: Dict[str, str],
        current_context: Dict[str, Any],
        agent_id: str,
        user_id: str
    ) -> Dict[str, str]:
        """
        增强版参数描述：结合语义指针补全。

        这是 enhance_param_descriptions_with_context 的增强版本，
        会先进行语义指针补全，再进行上下文增强。

        Args:
            base_param_descriptions: 基础参数描述
            current_context: 当前上下文（包含 content, description, global_context, enriched_context）
            agent_id: 当前 Agent ID
            user_id: 用户 ID

        Returns:
            Dict[str, str]: 增强后的参数描述
        """
        if not base_param_descriptions:
            return {}

        # 1. 先进行语义指针补全
        semantic_pointers = self.resolve_semantic_pointers(
            param_descriptions=base_param_descriptions,
            current_context=current_context,
            agent_id=agent_id,
            user_id=user_id
        )

        # 2. 提取补全后的描述
        enhanced_descriptions = {}
        for param_name, pointer_info in semantic_pointers.items():
            # 使用补全后的描述
            resolved_desc = pointer_info.get("resolved_desc", base_param_descriptions.get(param_name, ""))
            confidence = pointer_info.get("confidence", 1.0)

            # 如果置信度较低，保留原始描述作为备注
            if confidence < 0.6 and pointer_info.get("has_ambiguity"):
                original = pointer_info.get("original_desc", "")
                if original and original != resolved_desc:
                    resolved_desc = f"{resolved_desc}（原始描述：{original}）"

            enhanced_descriptions[param_name] = resolved_desc

        # 3. 再进行常规的上下文增强（使用 enriched_context 中的具体值）
        current_inputs = {}
        enriched_ctx = current_context.get("enriched_context", {})
        global_ctx = current_context.get("global_context", {})

        if isinstance(enriched_ctx, dict):
            current_inputs.update(enriched_ctx)
        if isinstance(global_ctx, dict):
            current_inputs.update(global_ctx)

        if current_inputs:
            enhanced_descriptions = self.enhance_param_descriptions_with_context(
                enhanced_descriptions,
                current_inputs
            )

        return enhanced_descriptions

    # ----------------------------------------------------------
    # Schema 摘要 + 按需展开：统一参数解析
    # ----------------------------------------------------------

    def build_schema_summary(self, data: Any) -> Any:
        """
        从实际数据自动生成 Schema 摘要（类型信息）

        用于让 LLM 快速了解数据结构，而不需要看完整内容。

        Args:
            data: 任意数据

        Returns:
            Schema 摘要，保留结构但用类型替代值

        Example:
            输入: {"user_id": "123", "profile": {"name": "张三", "age": 25}}
            输出: {"user_id": "string", "profile": {"name": "string", "age": "int"}}
        """
        if data is None:
            return "null"

        if isinstance(data, str):
            # 对于较长的字符串，显示长度信息
            if len(data) > 100:
                return f"string(len={len(data)})"
            return "string"

        if isinstance(data, bool):
            return "bool"

        if isinstance(data, int):
            return "int"

        if isinstance(data, float):
            return "float"

        if isinstance(data, dict):
            if not data:
                return "{}"
            # 递归处理字典的每个字段
            return {k: self.build_schema_summary(v) for k, v in data.items()}

        if isinstance(data, (list, tuple)):
            if not data:
                return "list[]"
            # 取第一个元素的 schema 作为列表元素类型
            first_schema = self.build_schema_summary(data[0])
            if len(data) > 1:
                return f"list[{first_schema}](len={len(data)})"
            return f"list[{first_schema}]"

        # Pydantic BaseModel
        try:
            from pydantic import BaseModel
            if isinstance(data, BaseModel):
                return self.build_schema_summary(data.model_dump())
        except ImportError:
            pass

        # 其他类型
        return type(data).__name__

    def build_context_snapshot(
        self,
        step_results: Dict[str, Any],
        global_context: Dict[str, Any] = None,
        enriched_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        构建带 Schema 摘要的上下文快照

        Args:
            step_results: 各步骤的完整执行结果
            global_context: 全局上下文
            enriched_context: 富化上下文

        Returns:
            上下文快照，包含 _schema 和 _ref 字段

        Example:
            {
                "global": {
                    "_schema": {"user_id": "string", "tenant_id": "string"},
                    "_data": {"user_id": "123", "tenant_id": "t1"}
                },
                "steps": {
                    "step_1": {
                        "_schema": {"profile": {"name": "string", "age": "int"}},
                        "_ref": "step_results.step_1"
                    }
                }
            }
        """
        snapshot = {}

        # 全局上下文（通常较小，直接包含数据）
        if global_context:
            snapshot["global"] = {
                "_schema": self.build_schema_summary(global_context),
                "_data": global_context  # 全局上下文直接包含数据
            }

        # 富化上下文
        if enriched_context:
            # 处理 ContextEntry 类型
            processed_enriched = {}
            for k, v in enriched_context.items():
                try:
                    from pydantic import BaseModel
                    if isinstance(v, BaseModel):
                        processed_enriched[k] = v.model_dump()
                    else:
                        processed_enriched[k] = v
                except ImportError:
                    processed_enriched[k] = v

            snapshot["enriched"] = {
                "_schema": self.build_schema_summary(processed_enriched),
                "_data": processed_enriched
            }

        # 步骤结果（可能较大，使用引用）
        if step_results:
            snapshot["steps"] = {}
            for step_key, step_data in step_results.items():
                snapshot["steps"][step_key] = {
                    "_schema": self.build_schema_summary(step_data),
                    "_ref": f"step_results.{step_key}"
                }

        return snapshot

    def resolve_params_for_tool(
        self,
        tool_schema: Dict[str, Any],
        context_snapshot: Dict[str, Any],
        step_results: Dict[str, Any],
        task_description: str = "",
        task_content: str = "",
        agent_id: str = ""
    ) -> Dict[str, Any]:
        """
        为工具调用解析参数（统一入口）

        增强版工作流程（ReAct 式）：
        1. 【ReAct 预填】LLM 通过思考-行动-观察循环，动态填充参数
           - INFER: 直接推断值（时间、数量等）
           - EXTRACT: 从上下文路径提取值
           - QUERY: 调用 resolve_context 查询数据库
        2. 【路径映射】对于未填充的参数，使用路径映射从上下文提取
        3. 合并结果

        Args:
            tool_schema: 工具的参数定义，格式：
                {
                    "parameters": {
                        "user_id": {"type": "string", "description": "用户ID"},
                        "limit": {"type": "int", "description": "返回数量", "default": 10}
                    },
                    "required": ["user_id"]
                }
            context_snapshot: 带 Schema 摘要的上下文快照
            step_results: 完整的步骤执行结果（用于按需提取）
            task_description: 任务描述（可选，帮助 LLM 理解意图）
            task_content: 任务内容（可选，业务需求的详细描述）
            agent_id: 当前 Agent ID（可选，用于 QUERY action）

        Returns:
            解析后的参数字典
        """
        if not self.llm_client:
            self.set_dependencies()

        if not tool_schema or "parameters" not in tool_schema:
            return {}

        resolved_params = {}

        # ========== Step 1: ReAct 式需求感知预填 ==========
        # LLM 通过思考-行动-观察循环，动态填充参数
        if task_content or task_description:
            inferred_params = self._llm_infer_param_values(
                tool_schema=tool_schema,
                task_content=task_content,
                task_description=task_description,
                context_snapshot=context_snapshot,
                agent_id=agent_id
            )
            if inferred_params:
                resolved_params.update(inferred_params)
                logger.info(f"[ReAct] Inferred params: {list(inferred_params.keys())}")

        # ========== Step 2: 路径映射提取 ==========
        # 对于未推断出的参数，使用路径映射从上下文提取
        remaining_params = {
            name: spec for name, spec in tool_schema["parameters"].items()
            if name not in resolved_params
        }

        if remaining_params:
            remaining_schema = {
                "parameters": remaining_params,
                "required": [p for p in tool_schema.get("required", []) if p in remaining_params]
            }

            param_mapping = self._llm_resolve_param_mapping(
                tool_schema=remaining_schema,
                context_snapshot=context_snapshot,
                task_description=task_description
            )

            if param_mapping:
                for param_name, path in param_mapping.items():
                    if path is None or path == "null" or path == "":
                        # 参数无法从上下文获取，检查是否有默认值
                        param_spec = tool_schema["parameters"].get(param_name, {})
                        if "default" in param_spec:
                            resolved_params[param_name] = param_spec["default"]
                        continue

                    value = self._extract_value_by_path(
                        path=path,
                        context_snapshot=context_snapshot,
                        step_results=step_results
                    )

                    if value is not None:
                        resolved_params[param_name] = value
                    else:
                        # 提取失败，检查默认值
                        param_spec = tool_schema["parameters"].get(param_name, {})
                        if "default" in param_spec:
                            resolved_params[param_name] = param_spec["default"]

        return resolved_params

    def _llm_infer_param_values(
        self,
        tool_schema: Dict[str, Any],
        task_content: str,
        task_description: str,
        context_snapshot: Dict[str, Any] = None,
        agent_id: str = ""
    ) -> Dict[str, Any]:
        """
        ReAct 式参数推断：LLM 通过思考-行动-观察循环，动态填充参数

        支持三种 Action：
        1. INFER: 直接推断值（如时间、数量）
        2. EXTRACT: 从上下文路径提取值
        3. QUERY: 调用 resolve_context 查询数据库

        例如：
        - 用户说"查一下这个产品"，schema 要求 product_id
        - ReAct: 分析需求 → 从上下文找到 product_name → 调用 QUERY 获取 ID

        Args:
            tool_schema: 工具参数定义
            task_content: 任务内容（业务需求详细描述）
            task_description: 任务描述（简短说明）
            context_snapshot: 上下文快照（可选）
            agent_id: 当前 Agent ID（用于 QUERY action）

        Returns:
            推断出的参数值字典
        """
        if not self.llm_client:
            return {}

        if not task_content and not task_description:
            return {}

        # 构建参数说明
        params_info = []
        required_params = tool_schema.get("required", [])

        for param_name, param_spec in tool_schema["parameters"].items():
            param_type = param_spec.get("type", "any")
            param_desc = param_spec.get("description", "")
            is_required = param_name in required_params
            has_default = "default" in param_spec

            req_mark = "[必填]" if is_required else "[可选]"
            default_mark = f"(默认: {param_spec['default']})" if has_default else ""

            params_info.append(f"- {param_name}: {param_type} {req_mark} {default_mark}\n  描述: {param_desc}")

        params_text = "\n".join(params_info)

        # 构建上下文摘要
        context_summary = self._build_context_summary_for_react(context_snapshot)

        # ReAct 循环
        max_iterations = 3
        resolved_params = {}
        action_history = []

        for iteration in range(max_iterations):
            # 构建 ReAct Prompt
            prompt = self._build_react_prompt(
                task_content=task_content,
                task_description=task_description,
                params_text=params_text,
                context_summary=context_summary,
                resolved_params=resolved_params,
                action_history=action_history,
                remaining_params=[p for p in tool_schema["parameters"] if p not in resolved_params]
            )

            try:
                response = self.llm_client.generate(
                    prompt=prompt,
                    parse_json=True,
                    max_tokens=800
                )

                if not isinstance(response, dict):
                    break

                # 解析 LLM 响应
                thought = response.get("thought", "")
                action = response.get("action", "")
                action_input = response.get("action_input", {})

                logger.info(f"[ReAct iter {iteration + 1}] Thought: {thought[:100]}...")
                logger.info(f"[ReAct iter {iteration + 1}] Action: {action}, Input: {action_input}")

                # 执行 Action
                if action == "FINISH":
                    # 完成，提取最终结果
                    final_params = response.get("final_params", {})
                    for param_name, value in final_params.items():
                        if param_name in tool_schema["parameters"]:
                            if value is not None and value != "" and value != "null":
                                resolved_params[param_name] = value
                    break

                elif action == "INFER":
                    # 直接推断值
                    for param_name, value in action_input.items():
                        if param_name in tool_schema["parameters"]:
                            if value is not None and value != "" and value != "null":
                                resolved_params[param_name] = value
                    action_history.append({
                        "action": "INFER",
                        "input": action_input,
                        "observation": f"已推断: {list(action_input.keys())}"
                    })

                elif action == "EXTRACT":
                    # 从上下文路径提取
                    extracted = {}
                    for param_name, path in action_input.items():
                        if param_name in tool_schema["parameters"] and path:
                            value = self._extract_value_by_path(
                                path=path,
                                context_snapshot=context_snapshot,
                                step_results=context_snapshot.get("steps", {}) if context_snapshot else {}
                            )
                            if value is not None:
                                extracted[param_name] = value
                                resolved_params[param_name] = value

                    action_history.append({
                        "action": "EXTRACT",
                        "input": action_input,
                        "observation": f"提取结果: {extracted}" if extracted else "未找到匹配数据"
                    })

                elif action == "QUERY":
                    # 调用 resolve_context 查询数据库
                    query_results = {}
                    if agent_id and action_input:
                        try:
                            query_results = self.resolve_context(
                                context_requirements=action_input,
                                agent_id=agent_id
                            )
                            for param_name, value in query_results.items():
                                if value is not None:
                                    resolved_params[param_name] = value
                        except Exception as e:
                            logger.warning(f"QUERY action failed: {e}")

                    action_history.append({
                        "action": "QUERY",
                        "input": action_input,
                        "observation": f"查询结果: {query_results}" if query_results else "查询无结果"
                    })

                else:
                    # 未知 action，跳过
                    logger.warning(f"Unknown action: {action}")
                    break

                # 检查是否所有必填参数都已填充
                missing_required = [
                    p for p in required_params
                    if p not in resolved_params
                ]
                if not missing_required:
                    logger.info(f"[ReAct] All required params filled after {iteration + 1} iterations")
                    break

            except Exception as e:
                logger.warning(f"ReAct iteration {iteration + 1} failed: {e}")
                break

        return resolved_params

    def _build_context_summary_for_react(self, context_snapshot: Dict[str, Any]) -> str:
        """构建用于 ReAct 的上下文摘要"""
        if not context_snapshot:
            return "无可用上下文"

        context_parts = []

        if "global" in context_snapshot:
            global_data = context_snapshot["global"].get("_data", {})
            if global_data:
                key_fields = {k: v for k, v in global_data.items()
                              if isinstance(v, (str, int, float, bool)) and v}
                if key_fields:
                    context_parts.append(f"【全局上下文 global】\n{json.dumps(key_fields, ensure_ascii=False, indent=2)}")

        if "enriched" in context_snapshot:
            enriched_data = context_snapshot["enriched"].get("_data", {})
            if enriched_data:
                key_fields = {}
                for k, v in enriched_data.items():
                    if isinstance(v, (str, int, float, bool)) and v:
                        v_str = str(v)
                        if len(v_str) < 200:
                            key_fields[k] = v
                if key_fields:
                    context_parts.append(f"【富化上下文 enriched】\n{json.dumps(key_fields, ensure_ascii=False, indent=2)}")

        if "steps" in context_snapshot:
            for step_key, step_info in context_snapshot["steps"].items():
                step_schema = step_info.get("_schema", {})
                context_parts.append(f"【步骤结果 {step_key}】Schema:\n{json.dumps(step_schema, ensure_ascii=False, indent=2)}")

        return "\n\n".join(context_parts) if context_parts else "无可用上下文"

    def _build_react_prompt(
        self,
        task_content: str,
        task_description: str,
        params_text: str,
        context_summary: str,
        resolved_params: Dict[str, Any],
        action_history: List[Dict],
        remaining_params: List[str]
    ) -> str:
        """构建 ReAct Prompt"""

        # 历史记录
        history_text = ""
        if action_history:
            history_parts = []
            for i, h in enumerate(action_history):
                history_parts.append(f"第 {i + 1} 轮:\n  Action: {h['action']}\n  Input: {h['input']}\n  Observation: {h['observation']}")
            history_text = "\n".join(history_parts)

        # 已填充参数
        resolved_text = json.dumps(resolved_params, ensure_ascii=False, indent=2) if resolved_params else "无"

        prompt = f"""你是一个智能参数填充 Agent。请通过 ReAct（思考-行动-观察）循环，为工具调用填充参数。

【业务需求】
任务内容: {task_content or "无"}
任务描述: {task_description or "无"}

【工具所需参数】
{params_text}

【可用上下文】
{context_summary}

【已填充参数】
{resolved_text}

【待填充参数】
{', '.join(remaining_params) if remaining_params else "无（全部已填充）"}

{f"【历史行动记录】{chr(10)}{history_text}" if history_text else ""}

【可用 Action】
1. **INFER**: 直接推断值（适用于时间、数量等可从业务需求推断的参数）
   - 输入格式: {{"param_name": "推断的值", ...}}
   - 示例: "过去一个季度" → {{"start_date": "2025-11-03"}}

2. **EXTRACT**: 从上下文路径提取值（适用于上下文中已有的数据）
   - 输入格式: {{"param_name": "context.path", ...}}
   - 路径格式: global.xxx / enriched.xxx / steps.step_N.xxx
   - 示例: {{"user_id": "global.user_id"}}

3. **QUERY**: 调用数据库查询（适用于需要根据名称/描述查找 ID 的场景）
   - 输入格式: {{"param_name": "查询描述", ...}}
   - 示例: {{"product_id": "名称为 iPhone 15 的产品ID"}}

4. **FINISH**: 完成填充，输出最终结果
   - 当所有必填参数都已填充，或无法继续填充时使用

【推断规则】
- 时间类: "过去一个季度"→3个月前, "最近一周"→7天前, "本月"→本月1日
- 数量类: "所有"→1000或-1, "前N个"→N
- ID类: 优先从上下文提取，其次用 QUERY 查询
- 今天日期: {self._get_today_date()}

【输出格式】
严格输出 JSON:
{{
    "thought": "分析当前情况，决定下一步行动",
    "action": "INFER/EXTRACT/QUERY/FINISH",
    "action_input": {{}},  // action 的输入参数
    "final_params": {{}}   // 仅 FINISH 时需要，输出所有已填充的参数
}}

注意：
1. 每次只执行一个 action
2. 优先使用 INFER 和 EXTRACT，QUERY 作为最后手段
3. 如果参数无法填充，在 thought 中说明原因，然后 FINISH
4. 只输出 JSON，不要任何解释
"""
        return prompt

    def _get_today_date(self) -> str:
        """获取今天的日期字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")

    def _llm_resolve_param_mapping(
        self,
        tool_schema: Dict[str, Any],
        context_snapshot: Dict[str, Any],
        task_description: str = ""
    ) -> Dict[str, str]:
        """
        使用 LLM 决定参数来源映射

        Args:
            tool_schema: 工具参数定义
            context_snapshot: 上下文快照（只包含 Schema）
            task_description: 任务描述

        Returns:
            参数映射：{"param_name": "path.to.value"} 或 {"param_name": null}
        """
        if not self.llm_client:
            return {}

        # 构建参数说明
        params_info = []
        required_params = tool_schema.get("required", [])

        for param_name, param_spec in tool_schema["parameters"].items():
            param_type = param_spec.get("type", "any")
            param_desc = param_spec.get("description", "")
            is_required = param_name in required_params
            has_default = "default" in param_spec

            req_mark = "[必填]" if is_required else "[可选]"
            default_mark = f"(默认: {param_spec['default']})" if has_default else ""

            params_info.append(f"- {param_name}: {param_type} {req_mark} {default_mark}\n  描述: {param_desc}")

        params_text = "\n".join(params_info)

        # 构建上下文 Schema 说明
        schema_parts = []

        if "global" in context_snapshot:
            global_schema = context_snapshot["global"].get("_schema", {})
            schema_parts.append(f"【全局上下文 global】\n{json.dumps(global_schema, ensure_ascii=False, indent=2)}")

        if "enriched" in context_snapshot:
            enriched_schema = context_snapshot["enriched"].get("_schema", {})
            schema_parts.append(f"【富化上下文 enriched】\n{json.dumps(enriched_schema, ensure_ascii=False, indent=2)}")

        if "steps" in context_snapshot:
            for step_key, step_info in context_snapshot["steps"].items():
                step_schema = step_info.get("_schema", {})
                schema_parts.append(f"【步骤结果 {step_key}】\n{json.dumps(step_schema, ensure_ascii=False, indent=2)}")

        schema_text = "\n\n".join(schema_parts) if schema_parts else "无可用上下文"

        # 构建 Prompt
        prompt = f"""你是一个智能参数映射器。请根据工具所需参数和可用上下文，决定每个参数应该从哪里获取。

【任务描述】
{task_description or "执行工具调用"}

【工具所需参数】
{params_text}

【可用上下文结构】
{schema_text}

【任务】
为每个参数指定数据来源路径。路径格式：
- global.xxx: 从全局上下文获取
- enriched.xxx: 从富化上下文获取
- steps.step_N.xxx: 从步骤结果获取
- null: 无法从上下文获取（需要用户输入或使用默认值）

【输出格式】
严格输出 JSON，格式如下：
{{
    "参数名1": "path.to.value",
    "参数名2": "global.user_id",
    "参数名3": null
}}

注意：
1. 只输出 JSON，不要任何解释
2. 路径必须与上下文结构匹配
3. 如果参数有默认值且上下文中没有，输出 null
4. 优先使用最近的数据（steps > enriched > global）
"""

        try:
            response = self.llm_client.generate(
                prompt=prompt,
                parse_json=True,
                max_tokens=500
            )

            if isinstance(response, dict):
                return response
            return {}

        except Exception as e:
            self.logger.error(f"LLM param mapping failed: {e}")
            return {}

    def _extract_value_by_path(
        self,
        path: str,
        context_snapshot: Dict[str, Any],
        step_results: Dict[str, Any]
    ) -> Any:
        """
        根据路径从上下文中提取实际值

        Args:
            path: 数据路径，如 "global.user_id" 或 "steps.step_1.profile.name"
            context_snapshot: 上下文快照
            step_results: 完整的步骤结果

        Returns:
            提取的值，如果路径无效返回 None
        """
        if not path or path == "null":
            return None

        parts = path.split(".")
        if not parts:
            return None

        root = parts[0]
        remaining_path = parts[1:]

        # 确定数据源
        if root == "global":
            data = context_snapshot.get("global", {}).get("_data", {})
        elif root == "enriched":
            data = context_snapshot.get("enriched", {}).get("_data", {})
        elif root == "steps":
            if not remaining_path:
                return None
            step_key = remaining_path[0]
            remaining_path = remaining_path[1:]
            # 从 step_results 获取完整数据
            data = step_results.get(step_key, {})
        else:
            # 尝试直接从 step_results 获取
            data = step_results.get(root, {})
            # 如果 root 不是 step key，remaining_path 需要包含 root 之后的部分

        # 沿路径提取值
        current = data
        for key in remaining_path:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, (list, tuple)):
                try:
                    idx = int(key)
                    current = current[idx] if 0 <= idx < len(current) else None
                except (ValueError, IndexError):
                    current = None
            else:
                current = None

            if current is None:
                break

        return current

    def get_missing_required_params(
        self,
        tool_schema: Dict[str, Any],
        resolved_params: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        获取缺失的必填参数列表

        Args:
            tool_schema: 工具参数定义
            resolved_params: 已解析的参数

        Returns:
            缺失参数列表，每项包含 name 和 description
        """
        missing = []
        required_params = tool_schema.get("required", [])

        for param_name in required_params:
            if param_name not in resolved_params:
                param_spec = tool_schema["parameters"].get(param_name, {})
                missing.append({
                    "name": param_name,
                    "description": param_spec.get("description", ""),
                    "type": param_spec.get("type", "string")
                })

        return missing

