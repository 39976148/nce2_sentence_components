from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AiConfig:
    api_base: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = "gpt-4o-mini"
    enabled: bool = False

    def is_ready(self) -> bool:
        return self.enabled and bool(self.api_key.strip())


def load_ai_config(root: Path) -> AiConfig:
    path = root / "config" / "ai.json"
    cfg = AiConfig()
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        cfg.api_base = data.get("api_base", cfg.api_base).rstrip("/")
        cfg.api_key = data.get("api_key", "")
        cfg.model = data.get("model", cfg.model)
        cfg.enabled = bool(data.get("enabled", False))

    cfg.api_key = os.environ.get("NCE2_AI_API_KEY", cfg.api_key)
    cfg.api_base = os.environ.get("NCE2_AI_API_BASE", cfg.api_base).rstrip("/")
    cfg.model = os.environ.get("NCE2_AI_MODEL", cfg.model)
    if os.environ.get("NCE2_AI_ENABLED", "").lower() in ("1", "true", "yes"):
        cfg.enabled = True
    return cfg


def save_ai_config(root: Path, cfg: AiConfig) -> None:
    path = root / "config" / "ai.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "api_base": cfg.api_base,
                "api_key": cfg.api_key,
                "model": cfg.model,
                "enabled": cfg.enabled,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
