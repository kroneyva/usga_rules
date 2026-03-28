import requests

from .config import Settings


def _auth_headers(settings: Settings) -> dict:
    if settings.ollama_api_key:
        return {"Authorization": f"Bearer {settings.ollama_api_key}"}
    return {}


def fetch_ollama_models(settings: Settings) -> list[str]:
    tags_url = f"{settings.ollama_base_url}/api/tags"
    response = requests.get(tags_url, headers=_auth_headers(settings), timeout=20)
    response.raise_for_status()
    models = response.json().get("models", [])
    return [m.get("name") for m in models if m.get("name")]


def resolve_ollama_model(settings: Settings) -> tuple[str, list[str], bool]:
    available = fetch_ollama_models(settings)
    if not available:
        raise RuntimeError("No local Ollama models found. Pull a model first, e.g. gemma3:4b")
    if settings.ollama_model:
        if settings.ollama_model in available:
            return settings.ollama_model, available, False
        return available[0], available, True
    return available[0], available, False


def build_chat_prompt(question: str, retrieved: list[dict]) -> list[dict]:
    context_blocks = []
    for item in retrieved:
        context_blocks.append(
            "\n".join(
                [
                    f"Rule ID: {item['id']}",
                    f"Title: {item['title']}",
                    f"Text: {item['text']}",
                    f"Source: {item['source'] or 'N/A'}",
                ]
            )
        )
    context = "\n\n".join(context_blocks) if context_blocks else "No matching rules found."

    system = (
        "You are a helpful assistant for USGA rules of golf. "
        "Use only the provided context to answer. "
        "Answer concisely in a few sentences. "
        "If the context is insufficient, say so clearly and recommend checking official USGA sources."
    )

    user = f"Question: {question}\n\nContext:\n{context}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def ask_ollama(settings: Settings, selected_model: str, messages: list[dict]) -> str:
    payload = {
        "model": selected_model,
        "messages": messages,
        "stream": False,
        "options": {"num_predict": settings.ollama_num_predict},
    }
    response = requests.post(
        settings.ollama_chat_url,
        json=payload,
        headers=_auth_headers(settings),
        timeout=settings.ollama_timeout,
    )
    response.raise_for_status()
    body = response.json()
    msg = body.get("message", {})
    answer = (msg.get("content") or "").strip() or (msg.get("thinking") or body.get("thinking") or "").strip()
    if answer:
        return answer
    return "The model returned no text output. Try again or use retrieval-only mode."
