from __future__ import annotations
import logging
from typing import Callable, TypeVar

from src.config import settings
from src.providers.base import KnowledgeBaseProvider, ProviderError

log = logging.getLogger(__name__)
T = TypeVar("T")


def build_providers() -> list[KnowledgeBaseProvider]:
    providers: list[KnowledgeBaseProvider] = []
    for key in settings.ai_provider_order:
        try:
            if key == "gemini":
                from src.providers.gemini_provider import GeminiProvider

                providers.append(GeminiProvider())
            else:
                log.warning(
                    "Provider '%s' in AI_PROVIDER_ORDER is not implemented, skipping", key
                )
        except ProviderError as exc:
            log.warning("Provider '%s' unavailable, skipping: %s", key, exc)
    if not providers:
        raise ProviderError(
            "No AI provider could be initialized. Set GEMINI_API_KEY in your environment."
        )
    return providers


def with_fallback(
    providers: list[KnowledgeBaseProvider],
    op: Callable[[KnowledgeBaseProvider], T],
    op_name: str = "operation",
) -> tuple[KnowledgeBaseProvider, T]:
    last_exc: Exception | None = None
    for provider in providers:
        try:
            return provider, op(provider)
        except ProviderError as exc:
            log.warning("%s failed on provider '%s': %s", op_name, provider.name, exc)
            last_exc = exc
    raise ProviderError(f"All providers failed for {op_name}: {last_exc}")
