"""Runtime configuration from environment variables (see .env.example)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env(name: str, default: str | None = None) -> str | None:
    v = os.environ.get(name)
    return v if v not in (None, "") else default


@dataclass
class Settings:
    db_path: str = field(default_factory=lambda: _env("ZHOL_DB", "data/zhol.db"))
    timezone: str = field(default_factory=lambda: _env("ZHOL_TZ", "Europe/Rome"))
    # human-in-the-loop: every alert waits for a reviewer before it is sent
    review_alerts: bool = field(default_factory=lambda: _env("ZHOL_REVIEW_ALERTS", "1") == "1")
    # LLM extraction (Claude). Without credentials zhol falls back to the rule-based extractor.
    llm_enabled: bool = field(default_factory=lambda: _env("ZHOL_LLM", "auto") != "off")
    llm_model: str = field(default_factory=lambda: _env("ZHOL_LLM_MODEL", "claude-opus-5-5"))
    llm_effort: str = field(default_factory=lambda: _env("ZHOL_LLM_EFFORT", "low"))
    # WhatsApp Cloud API
    wa_token: str | None = field(default_factory=lambda: _env("WHATSAPP_TOKEN"))
    wa_phone_number_id: str | None = field(default_factory=lambda: _env("WHATSAPP_PHONE_NUMBER_ID"))
    wa_app_secret: str | None = field(default_factory=lambda: _env("WHATSAPP_APP_SECRET"))
    wa_verify_token: str | None = field(default_factory=lambda: _env("WHATSAPP_VERIFY_TOKEN", "zhol-dev-verify"))
    wa_api_version: str = field(default_factory=lambda: _env("WHATSAPP_API_VERSION", "v21.0"))
    admin_token: str | None = field(default_factory=lambda: _env("ZHOL_ADMIN_TOKEN"))


settings = Settings()
