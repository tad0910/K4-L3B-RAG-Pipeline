"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Trả lời chỉ từ context được cung cấp.
Mỗi khẳng định phải có citation. Nếu thiếu evidence, hãy từ chối xác minh."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context."""
    if len(chunks) <= 2:
        return list(chunks)
    return list(chunks[::2]) + list(chunks[1::2])[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk["metadata"]
        parts.append(
            f"[Document {index} | Title: {metadata['title']} | "
            f"Source: {metadata['source']}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def _get_secret_or_env(key: str, default: str = "") -> str:
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình."""
    provider = _get_secret_or_env("LLM_PROVIDER", "").lower().strip()
    gemini_key = _get_secret_or_env("GEMINI_API_KEY")
    openai_key = _get_secret_or_env("OPENAI_API_KEY")
    anthropic_key = _get_secret_or_env("ANTHROPIC_API_KEY")

    if not provider:
        if gemini_key:
            provider = "gemini"
        elif openai_key:
            provider = "openai"
        elif anthropic_key:
            provider = "anthropic"
        else:
            provider = "openai"

    # Phòng ngừa trường hợp người dùng đặt nhầm tên biến (ví dụ chọn gemini nhưng gán vào OPENAI_API_KEY)
    if provider == "gemini" and not gemini_key and openai_key:
        gemini_key = openai_key
    elif provider == "openai" and not openai_key and gemini_key:
        openai_key = gemini_key

    model = _get_secret_or_env("LLM_MODEL", LLM_MODEL).strip()

    if provider == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model=model or "gpt-4o-mini",
            temperature=TEMPERATURE,
            top_p=TOP_P,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or ""

    if provider == "gemini":
        from google import genai

        client = genai.Client(api_key=gemini_key)
        target_model = model or "gemini-2.5-flash"
        if target_model == "gemini-2.0-flash":
            target_model = "gemini-2.5-flash"

        # List of candidate models to try in case of deprecation/availability
        candidates = [target_model]
        for fallback in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-lite"]:
            if fallback not in candidates:
                candidates.append(fallback)

        last_err = None
        for cand in candidates:
            try:
                response = client.models.generate_content(
                    model=cand,
                    contents=f"{system_prompt}\n\n{user_message}",
                    config={"temperature": TEMPERATURE, "top_p": TOP_P},
                )
                return response.text or ""
            except Exception as e:
                last_err = e
                # If error is model not found or unavailable, continue to next fallback candidate
                err_str = str(e).lower()
                if "404" in str(e) or "not_found" in err_str or "not available" in err_str:
                    continue
                # For auth or other critical errors, raise immediately
                raise e
        if last_err:
            raise last_err

    if provider == "anthropic":
        from anthropic import Anthropic

        client = Anthropic(api_key=anthropic_key)
        response = client.messages.create(
            model=model or "claude-3-5-haiku-latest",
            max_tokens=1200,
            temperature=TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return "".join(block.text for block in response.content if hasattr(block, "text"))

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult."""
    refusal = "Tôi không thể xác minh thông tin này từ nguồn hiện có."
    if not query.strip() or top_k <= 0:
        return {"answer": refusal, "sources": [], "retrieval_source": "none"}

    try:
        chunks = retrieve(query, top_k=top_k)
    except (ImportError, KeyError, OSError, RuntimeError, ValueError):
        return {"answer": refusal, "sources": [], "retrieval_source": "none"}
    if not chunks:
        return {"answer": refusal, "sources": [], "retrieval_source": "none"}

    sources = list(chunks)
    context = format_context(reorder_for_llm(sources))
    user_message = (
        f"Context:\n{context}\n\nQuestion: {query}\n\n"
        "Trích dẫn khẳng định bằng [Document i]."
    )
    try:
        answer = call_llm(SYSTEM_PROMPT, user_message).strip()
    except Exception as err:
        print(f"[LLM Error] {err}", flush=True)
        answer = f"Tôi đã tìm thấy nguồn tham khảo nhưng chưa thể tạo câu trả lời lúc này (Chi tiết lỗi: {err})."
    if not answer:
        answer = refusal

    retrieval_source = sources[0].get("retrieval_method", "hybrid")
    if retrieval_source not in {"hybrid", "pageindex"}:
        retrieval_source = "hybrid"
    return {
        "answer": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    print(generate_with_citation("test query"))
