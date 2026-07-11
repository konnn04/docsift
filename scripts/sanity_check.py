from __future__ import annotations
import logging
import sys

from src.config import settings
from src.providers.factory import build_providers, with_fallback

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

QUESTION = "How do I add a YouTube video?"


def main() -> int:
    providers = build_providers()
    provider, result = with_fallback(providers, lambda p: p.ask(QUESTION, settings.system_prompt), "sanity check")

    print(f"\nProvider used: {result.provider}")
    print(f"Question: {QUESTION}\n")
    print("Answer:\n" + result.answer)
    if result.citations:
        print("\nCitations:")
        for c in result.citations:
            print(f"  - {c}")
    else:
        print("\n(No citation metadata returned by the SDK for this call.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
