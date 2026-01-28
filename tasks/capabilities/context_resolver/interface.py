from abc import abstractmethod
from typing import Dict, Any, List
from ..capability_base import CapabilityBase

class IContextResolverCapbility(CapabilityBase):
    """
    上下文解析能力的抽象定义
    定义了外界如何与上下文解析器交互，而不关心具体是基于树查找还是其他方式。
    """

    def get_capability_type(self) -> str:
        return 'context_resolver'

    @abstractmethod
    def set_dependencies(self, registry: Any, llm_client: Any = None) -> None:
        """
        注入外部依赖（因为 initialize 只接收 config）
        """
        pass

    @abstractmethod
    def resolve_context(self, context_requirements: Dict[str, str], agent_id: str) -> Dict[str, Any]:
        """
        核心方法：根据需求描述解析上下文变量

        Args:
            context_requirements: 需求字典 { "变量名": "自然语言描述" }
            agent_id: 请求发起者的 Agent ID (作为搜索起点)
        Returns:
            Dict[str, Any]: 解析结果 { "变量名": 节点元数据/具体值 }
        """
        pass

    @abstractmethod
    def extract_context(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从任务原始数据中提取基础上下文（保留原有功能）
        """
        pass


    @abstractmethod
    def enhance_param_descriptions_with_context(self,
        base_param_descriptions: dict,
        current_inputs: dict
        ) -> dict:
        """
        基于当前输入和基础参数描述，增强参数描述（保留原有功能）
        """
        pass

    @abstractmethod
    def pre_fill_known_params_with_llm(self,
        base_param_descriptions: dict,
        current_context_str: str
        ) -> tuple[dict, dict]:
        """
        使用 LLM 填充已知参数（保留原有功能）
        """
        pass

    # ----------------------------------------------------------
    # Schema 摘要 + 按需展开：统一参数解析接口
    # ----------------------------------------------------------

    @abstractmethod
    def build_schema_summary(self, data: Any) -> Any:
        """
        从实际数据自动生成 Schema 摘要（类型信息）

        用于让 LLM 快速了解数据结构，而不需要看完整内容。

        Args:
            data: 任意数据

        Returns:
            Schema 摘要，保留结构但用类型替代值
        """
        pass

    @abstractmethod
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
            上下文快照，包含 _schema 和 _ref/_data 字段
        """
        pass

    @abstractmethod
    def resolve_params_for_tool(
        self,
        tool_schema: Dict[str, Any],
        context_snapshot: Dict[str, Any],
        step_results: Dict[str, Any],
        task_description: str = ""
    ) -> Dict[str, Any]:
        """
        为工具调用解析参数（统一入口）

        工作流程：
        1. 将 tool_schema 和 context_snapshot._schema 交给 LLM
        2. LLM 返回参数映射
        3. 根据映射从实际数据中提取值

        Args:
            tool_schema: 工具的参数定义
            context_snapshot: 带 Schema 摘要的上下文快照
            step_results: 完整的步骤执行结果（用于按需提取）
            task_description: 任务描述（可选）

        Returns:
            解析后的参数字典
        """
        pass

    @abstractmethod
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
            缺失参数列表，每项包含 name、description、type
        """
        pass