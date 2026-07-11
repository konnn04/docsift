from __future__ import annotations
from dotenv import load_dotenv
import os
from dataclasses import dataclass, field

load_dotenv()

def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "y"}


@dataclass(frozen=True)
class Settings:
    help_center_base: str = os.getenv("HELP_CENTER_BASE", "https://support.optisigns.com")
    locale: str = os.getenv("HELP_CENTER_LOCALE", "en-us")
    min_articles: int = int(os.getenv("MIN_ARTICLES", "30"))
    page_size: int = int(os.getenv("PAGE_SIZE", "100"))

    articles_dir: str = os.getenv("ARTICLES_DIR", "articles")
    manifest_path: str = os.getenv("MANIFEST_PATH", "data/manifest.json")

    ai_provider_order: tuple = tuple(
        p.strip().lower()
        for p in os.getenv("AI_PROVIDER_ORDER", "gemini").split(",")
        if p.strip()
    )
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
    gemini_store_name: str = os.getenv("GEMINI_STORE_NAME", "docsift-kb")

    gemini_chunk_size_estimate_tokens: int = int(
        os.getenv("GEMINI_CHUNK_SIZE_ESTIMATE_TOKENS", "800")
    )
    gemini_chunk_overlap_estimate_tokens: int = int(
        os.getenv("GEMINI_CHUNK_OVERLAP_ESTIMATE_TOKENS", "100")
    )

    system_prompt: str = (
        "You are OptiBot, the customer-support bot for OptiSigns.com.\n"
        "\u2022 Tone: helpful, factual, concise.\n"
        "\u2022 Only answer using the uploaded docs.\n"
        "\u2022 Max 5 bullet points; else link to the doc.\n"
        '\u2022 Cite up to 3 "Article URL:" lines per reply.'
    )

    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "20"))
    user_agent: str = os.getenv(
        "SCRAPER_USER_AGENT", "docsift-kb-bot/1.0 (+https://github.com/)"
    )
    dry_run: bool = field(default_factory=lambda: _bool("DRY_RUN", False))

    smoke_test_limit: int | None = (
        int(os.getenv("SMOKE_TEST_LIMIT")) if os.getenv("SMOKE_TEST_LIMIT") else None
    )

    upload_concurrency: int = int(os.getenv("UPLOAD_CONCURRENCY", "8"))


settings = Settings()
