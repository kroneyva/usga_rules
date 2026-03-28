import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path
    dataset_path: Path
    seed_path: Path
    ollama_base_url: str
    ollama_chat_url: str
    ollama_model: str | None
    ollama_timeout: int
    ollama_num_predict: int
    ollama_api_key: str | None


def load_settings(project_root: Path | None = None) -> Settings:
    root = project_root or Path(__file__).resolve().parents[2]
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    return Settings(
        project_root=root,
        dataset_path=root / "data" / "rules_dataset.json",
        seed_path=root / "data" / "rules_seed.json",
        ollama_base_url=base_url,
        ollama_chat_url=f"{base_url}/api/chat",
        ollama_model=os.getenv("OLLAMA_MODEL"),
        ollama_timeout=int(os.getenv("OLLAMA_TIMEOUT", "300")),
        ollama_num_predict=int(os.getenv("OLLAMA_NUM_PREDICT", "160")),
        ollama_api_key=os.getenv("OLLAMA_API_KEY") or None,
    )
