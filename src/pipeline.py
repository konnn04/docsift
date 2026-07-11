from __future__ import annotations
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from src.config import settings
from src.scraper.html_fallback import HTMLFallbackError, HTMLFallbackScraper
from src.scraper.markdown_converter import article_to_markdown
from src.scraper.models import Article
from src.scraper.zendesk_client import ZendeskAPIError, ZendeskClient
from src.state.manifest import DeltaKind, Manifest, content_hash
from src.providers.base import KnowledgeBaseProvider, ProviderError
from src.providers.factory import build_providers
from src.utils import estimate_chunks

log = logging.getLogger(__name__)


@dataclass
class RunReport:
    source_used: str = ""
    provider_used: str = ""
    total_articles: int = 0
    added: int = 0
    updated: int = 0
    skipped: int = 0
    deleted: int = 0
    embedded_files: int = 0       
    embedded_chunks_estimate: int = 0
    errors: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"source={self.source_used} provider={self.provider_used} "
            f"total={self.total_articles} added={self.added} "
            f"updated={self.updated} skipped={self.skipped} "
            f"deleted={self.deleted} embedded_files={self.embedded_files} "
            f"embedded_chunks_estimate={self.embedded_chunks_estimate} "
            f"errors={len(self.errors)}"
        )


def scrape_articles(
    min_articles: int | None = None,
    limit: int | None = None,
    source: str = "auto",
) -> tuple[list[Article], str]:
    min_articles = min_articles or settings.min_articles

    if source == "html":
        try:
            return HTMLFallbackScraper().fetch_articles(limit=limit), "html_fallback"
        except HTMLFallbackError as exc:
            raise RuntimeError(f"HTML fallback scrape failed: {exc}") from exc

    try:
        articles = ZendeskClient().fetch_articles(limit=limit)
        if limit is None and len(articles) < min_articles:
            log.warning(
                "Zendesk API returned only %s articles (< %s); trying HTML fallback too",
                len(articles), min_articles,
            )
            raise ZendeskAPIError("below minimum article threshold")
        return articles, "zendesk_api"
    except ZendeskAPIError as exc:
        if source == "api":
            raise RuntimeError(
                f"Zendesk API failed and fallback is disabled (--source api): {exc}"
            ) from exc
        log.warning("Zendesk API path failed (%s); falling back to HTML scraping", exc)

    try:
        articles = HTMLFallbackScraper().fetch_articles(limit=limit)
        return articles, "html_fallback"
    except HTMLFallbackError as exc:
        raise RuntimeError(f"Both Zendesk API and HTML fallback failed: {exc}") from exc


def write_markdown_files(articles: list[Article], out_dir: str) -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    rendered: dict[str, str] = {}
    for a in articles:
        md = article_to_markdown(a)
        path = os.path.join(out_dir, f"{a.slug}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        rendered[a.id] = md
    return rendered


def select_provider(providers: list[KnowledgeBaseProvider]) -> KnowledgeBaseProvider:
    last_exc: Exception | None = None
    for p in providers:
        try:
            p.ensure_store()
            return p
        except ProviderError as exc:
            log.warning("Provider '%s' unreachable, trying next: %s", p.name, exc)
            last_exc = exc
    raise ProviderError(f"No provider reachable: {last_exc}")


@dataclass
class _SyncOutcome:
    added: bool
    chunks: int
    error: str | None = None


def _sync_article(
    article: Article,
    md: str,
    hash_: str,
    kind: DeltaKind,
    path: str,
    provider: KnowledgeBaseProvider,
    manifest: Manifest,
    dry_run: bool,
) -> _SyncOutcome:
    try:
        if kind == DeltaKind.UPDATED:
            prev = manifest.get(article.id) or {}
            old_remote_id = (prev.get("vector_file_ids") or {}).get(provider.name)
            if old_remote_id:
                provider.delete_file(old_remote_id)
            old_path = prev.get("path")
            if old_path and old_path != path and os.path.exists(old_path):
                os.remove(old_path) 

        if dry_run:
            remote_id = f"dry-run-{article.id}"
        else:
            result = provider.upload_file(path, display_name=f"{article.slug}.md")
            remote_id = result.remote_file_id

        manifest.update(
            article.id,
            hash_=hash_,
            path=path,
            url=article.url,
            updated_at=article.updated_at,
            vector_file_ids={provider.name: remote_id},
        )
        chunks = estimate_chunks(
            md,
            settings.gemini_chunk_size_estimate_tokens,
            settings.gemini_chunk_overlap_estimate_tokens,
        )
        return _SyncOutcome(added=kind == DeltaKind.ADDED, chunks=chunks)
    except ProviderError as exc:
        return _SyncOutcome(added=False, chunks=0, error=f"{article.id} ({article.title}): {exc}")


def _remove_stale(
    stale_id: str, provider: KnowledgeBaseProvider, manifest: Manifest, dry_run: bool
) -> None:
    entry = manifest.remove(stale_id) or {}
    remote_id = (entry.get("vector_file_ids") or {}).get(provider.name)
    if remote_id and not dry_run:
        provider.delete_file(remote_id)
    stale_path = entry.get("path")
    if stale_path and os.path.exists(stale_path):
        os.remove(stale_path)


def run_pipeline(
    providers: list[KnowledgeBaseProvider] | None = None,
    articles_dir: str | None = None,
    manifest_path: str | None = None,
    limit: int | None = None,
    source: str = "auto",
    scrape_only: bool = False,
    dry_run: bool | None = None,
) -> RunReport:
    articles_dir = articles_dir or settings.articles_dir
    manifest_path = manifest_path or settings.manifest_path
    limit = limit if limit is not None else settings.smoke_test_limit
    dry_run = settings.dry_run if dry_run is None else dry_run
    report = RunReport()

    articles, source_used = scrape_articles(limit=limit, source=source)
    report.source_used = source_used
    report.total_articles = len(articles)

    if scrape_only:
        write_markdown_files(articles, articles_dir)
        log.info(
            "scrape-only: wrote %s markdown file(s); provider/manifest steps skipped",
            len(articles),
        )
        log.info("Run complete: %s", report.summary())
        return report

    manifest = Manifest(manifest_path)

    providers = providers or build_providers()
    provider = select_provider(providers)
    report.provider_used = provider.name
    provider.configure_assistant(settings.system_prompt)

    seen_ids = {a.id for a in articles}

    needs_render: list[Article] = []
    for a in articles:
        prev = manifest.get(a.id)
        local_file_present = bool(prev) and os.path.exists(prev.get("path", ""))
        if (
            prev is not None
            and local_file_present
            and a.updated_at
            and prev.get("updated_at") == a.updated_at
        ):
            report.skipped += 1
            continue
        needs_render.append(a)

    rendered = write_markdown_files(needs_render, articles_dir)

    to_sync: list[tuple[Article, str, str, DeltaKind, str]] = []
    for a in needs_render:
        md = rendered[a.id]
        h = content_hash(md)
        kind = manifest.diff(a.id, h, updated_at=a.updated_at)
        if kind == DeltaKind.UNCHANGED:
            report.skipped += 1
            continue
        path = os.path.join(articles_dir, f"{a.slug}.md")
        to_sync.append((a, md, h, kind, path))

    if to_sync:
        with ThreadPoolExecutor(max_workers=settings.upload_concurrency) as pool:
            futures = [
                pool.submit(_sync_article, a, md, h, kind, path, provider, manifest, dry_run)
                for a, md, h, kind, path in to_sync
            ]
            for future in as_completed(futures):
                outcome = future.result()
                if outcome.error:
                    log.error("Upload failed for %s", outcome.error)
                    report.errors.append(outcome.error)
                    continue
                report.added += 1 if outcome.added else 0
                report.updated += 0 if outcome.added else 1
                report.embedded_files += 1
                report.embedded_chunks_estimate += outcome.chunks

    if limit is None:
        stale_ids = manifest.known_ids() - seen_ids
        if stale_ids:
            with ThreadPoolExecutor(max_workers=settings.upload_concurrency) as pool:
                futures = [
                    pool.submit(_remove_stale, stale_id, provider, manifest, dry_run)
                    for stale_id in stale_ids
                ]
                for _ in as_completed(futures):
                    pass
            report.deleted += len(stale_ids)

    manifest.save()
    log.info("Run complete: %s", report.summary())
    return report
