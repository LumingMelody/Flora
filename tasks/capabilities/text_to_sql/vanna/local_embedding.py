# local_embedding.py
"""本地 ONNX 模型 embedding function，供 ChromaDB 使用"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def get_local_embedding_function():
    """获取使用本地 ONNX 模型的 embedding function"""

    # 获取本地模型路径
    model_path = os.environ.get(
        "EMBEDDING_MODEL_PATH",
        str(Path(__file__).parent.parent.parent.parent.parent / "all-MiniLM-L6-v2(1)" / "onnx")
    )

    logger.info(f"Loading local embedding model from: {model_path}")

    model_file = os.path.join(model_path, "model.onnx")
    tokenizer_file = os.path.join(model_path, "tokenizer.json")

    # 检查文件是否存在
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Model file not found: {model_file}")
    if not os.path.exists(tokenizer_file):
        raise FileNotFoundError(f"Tokenizer file not found: {tokenizer_file}")

    # 直接实现 embedding function，不继承 ONNXMiniLM_L6_V2（避免父类初始化问题）
    from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
    import numpy as np

    class LocalONNXEmbeddingFunction(EmbeddingFunction[Documents]):
        """完全自定义的本地 ONNX embedding function"""

        def __init__(self):
            self._model = None
            self._tokenizer = None
            self._model_path = model_path

        def _ensure_model_loaded(self):
            """延迟加载模型"""
            if self._model is None:
                import onnxruntime as ort
                from tokenizers import Tokenizer

                self._model = ort.InferenceSession(
                    model_file,
                    providers=["CPUExecutionProvider"]
                )
                self._tokenizer = Tokenizer.from_file(tokenizer_file)
                self._tokenizer.enable_truncation(max_length=256)
                self._tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=256)
                logger.info(f"Loaded ONNX model and tokenizer from {model_path}")

        def __call__(self, input: Documents) -> Embeddings:
            """生成 embeddings"""
            self._ensure_model_loaded()

            # Tokenize
            encoded = [self._tokenizer.encode(doc) for doc in input]

            # 准备输入
            input_ids = np.array([e.ids for e in encoded], dtype=np.int64)
            attention_mask = np.array([e.attention_mask for e in encoded], dtype=np.int64)
            token_type_ids = np.zeros_like(input_ids, dtype=np.int64)

            # 运行模型
            outputs = self._model.run(
                None,
                {
                    "input_ids": input_ids,
                    "attention_mask": attention_mask,
                    "token_type_ids": token_type_ids
                }
            )

            # 获取 embeddings (使用 mean pooling)
            embeddings = outputs[0]  # [batch_size, seq_len, hidden_size]

            # Mean pooling with attention mask
            attention_mask_expanded = np.expand_dims(attention_mask, axis=-1)
            sum_embeddings = np.sum(embeddings * attention_mask_expanded, axis=1)
            sum_mask = np.clip(np.sum(attention_mask_expanded, axis=1), a_min=1e-9, a_max=None)
            mean_embeddings = sum_embeddings / sum_mask

            # Normalize
            norms = np.linalg.norm(mean_embeddings, axis=1, keepdims=True)
            normalized_embeddings = mean_embeddings / np.clip(norms, a_min=1e-9, a_max=None)

            return normalized_embeddings.tolist()

    return LocalONNXEmbeddingFunction()
