import json

from .config import Settings


def load_rules(settings: Settings) -> list[dict]:
    if settings.dataset_path.exists():
        return json.loads(settings.dataset_path.read_text(encoding="utf-8"))
    if settings.seed_path.exists():
        return json.loads(settings.seed_path.read_text(encoding="utf-8"))
    return []
