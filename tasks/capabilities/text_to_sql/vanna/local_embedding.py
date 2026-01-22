# local_embedding.py
"""本地 ONNX 模型 embedding function，供 ChromaDB 使用"""

import os
from pathlib import Path


def get_local_embedding_function():
    """获取使用本地 ONNX 模型的 embedding function"""
    from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

    # 获取本地模型路径
    model_path = os.environ.get(
        "EMBEDDING_MODEL_PATH",
        str(Path(__file__).parent.parent.parent.parent.parent / "all-MiniLM-L6-v2(1)" / "onnx")
    )

    # 创建自定义的 embedding function
    class LocalONNXEmbeddingFunction(ONNXMiniLM_L6_V2):
        def __init__(self):
            # 设置模型路径，避免下载
            self._model_dir = model_path
            self._download_path = Path(model_path)
            super().__init__(preferred_providers=["CPUExecutionProvider"])

        def _download_model_if_not_exists(self):
            # 跳过下载，直接使用本地模型
            if not hasattr(self, '_model') or self._model is None:
                self._init_model_from_local()

        def _init_model_from_local(self):
            import onnxruntime as ort
            from tokenizers import Tokenizer

            model_file = os.path.join(model_path, "model.onnx")
            tokenizer_file = os.path.join(model_path, "tokenizer.json")

            if not os.path.exists(model_file):
                raise FileNotFoundError(f"Model file not found: {model_file}")
            if not os.path.exists(tokenizer_file):
                raise FileNotFoundError(f"Tokenizer file not found: {tokenizer_file}")

            self._model = ort.InferenceSession(
                model_file,
                providers=self._preferred_providers
            )
            self._tokenizer = Tokenizer.from_file(tokenizer_file)
            self._tokenizer.enable_truncation(max_length=256)
            self._tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=256)

    return LocalONNXEmbeddingFunction()
