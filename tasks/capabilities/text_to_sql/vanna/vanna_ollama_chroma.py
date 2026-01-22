# vanna_ollama_chroma.py

from typing import List, Any, Optional
import requests
import json
from vanna.base import VannaBase
from vanna.chromadb import ChromaDB_VectorStore
from .ivanna_service import IVannaService
from .vanna_factory import register_vanna
from .local_embedding import get_local_embedding_function

@register_vanna("ollama-chroma")
class OllamaVanna(ChromaDB_VectorStore, VannaBase, IVannaService):
    def __init__(
        self,
        business_id: str,
        model: str = "qwen2:7b",  # 或 "llama3", "mistral", etc.
        ollama_host: str = "http://localhost:11434",
        chroma_path: str = "./chroma",
        **kwargs
    ):
        # 使用本地 ONNX 模型作为 embedding function
        embedding_function = get_local_embedding_function()
        ChromaDB_VectorStore.__init__(self, config={
            "path": chroma_path,
            "collection": business_id,
            "embedding_function": embedding_function
        })
        self.business_id = business_id
        self.model = model
        self.ollama_url = f"{ollama_host.rstrip('/')}/api/chat"

    def system_message(self, message: str) -> Any:
        return {"role": "system", "content": message}

    def user_message(self, message: str) -> Any:
        return {"role": "user", "content": message}

    def assistant_message(self, message: str) -> Any:
        return {"role": "assistant", "content": message}

    def submit_prompt(self, messages: List[Any]) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 512,
            }
        }
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"Failed to call Ollama API at {self.ollama_url}: {e}")

    def train_ddl_with_database(self, database: str, table: str, ddl: str = None):
        if ddl is None:
            from .data_actor import get_mysql_ddl
            ddl = get_mysql_ddl(database, table)
        if f"`{database}`.`{table}`" not in ddl:
            ddl = ddl.replace(f"`{table}`", f"`{database}`.`{table}`")
        self.train(ddl=ddl)