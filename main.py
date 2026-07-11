from __future__ import annotations
import argparse
import logging
import sys

from src.config import settings
from src.pipeline import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("main")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape OptiSigns docs and sync them to the AI provider.")
    parser.add_argument(
        "--source",
        choices=["auto", "api", "html"],
        default="auto",
        help="auto: Zendesk API, falling back to HTML on failure (default). "
        "api: Zendesk API only, no fallback. "
        "html: skip the API, force the HTML fallback scraper.",
    )
    parser.add_argument(
        "--only-scraper",
        action="store_true",
        help="Scrape + write markdown files only. Skips the AI provider "
        "entirely (no API key needed, no upload, manifest untouched).",
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Cap the number of articles scraped/synced."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=None,
        help="Scrape + diff but skip real uploads/deletes (overrides DRY_RUN env var).",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    try:
        report = run_pipeline(
            source=args.source,
            scrape_only=args.only_scraper,
            limit=args.limit,
            dry_run=args.dry_run,
        )
    except Exception as exc:
        log.error("Pipeline run failed: %s", exc)
        return 1

    log.info(
        "added=%s updated=%s skipped=%s deleted=%s errors=%s",
        report.added,
        report.updated,
        report.skipped,
        report.deleted,
        len(report.errors),
    )
    if not args.only_scraper:
        log.info(
            "Embedded %s file(s) into the '%s' vector store this run "
            "(~%s chunks estimated; estimate assumes %s/%s token chunk/overlap, "
            "since Gemini's actual chunking is managed server-side)",
            report.embedded_files,
            report.provider_used,
            report.embedded_chunks_estimate,
            settings.gemini_chunk_size_estimate_tokens,
            settings.gemini_chunk_overlap_estimate_tokens,
        )
    print(report.summary())

    if report.errors:
        for e in report.errors:
            log.error("Per-article error: %s", e)
        if report.added == 0 and report.updated == 0 and report.skipped == 0:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
