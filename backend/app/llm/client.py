import httpx
import os

# Point to the AI Node's vLLM server
VLLM_URL = os.getenv("VLLM_URL", "http://192.168.29.96:8001/v1/chat/completions")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen-27b")

def generate_rag_response(query: str, context: str) -> str:
    """
    Sends a prompt to the local Qwen 27B model with retrieved context.
    """
    system_prompt = (
        "You are an expert AI assistant for the Yukti Platform. "
        "Use the provided context to answer the user's question. "
        "If the answer is not in the context, state clearly that you don't know. "
        "Do not make up information."
    )
    
    user_prompt = f"Context:\n{context}\n\nQuestion: {query}"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }

    try:
        # We use a 60s timeout because LLM generation can be slow on CPU/Single GPU
        response = httpx.post(VLLM_URL, json=payload, timeout=60.0)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error communicating with AI Node: {str(e)}"
