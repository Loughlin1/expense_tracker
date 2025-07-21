# llama_runner.py
from llama_cpp import Llama
import os


def setup_llm(model_path, context_window=2048):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")

    # Disable logging, streaming, or anything external
    return Llama(
        model_path=model_path,
        n_ctx=context_window,
        verbose=False,
        embedding=False,
        use_mlock=True,  # ⛓️ Lock model into RAM (avoid swap)
        logits_all=False,  # 🚫 Don't return unnecessary internal data
    )
