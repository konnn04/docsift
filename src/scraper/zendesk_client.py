from __future__ import annotations
import logging
from typing import Iterator

import requests

from src.config import settings
from src.scraper.models import Article

log = logging.getLogger(__name__)


class ZendeskAPIError(Exception):
    pass

class ZendeskClient:
    def __init__(self, base_url: str | None = None, locale: str | None = None):
        self.base_url = (base_url or settings.help_center_base).rstrip("/")
        self.locale = locale or settings.locale
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": settings.user_agent})
        self._sections: dict[int, str] = {}

    def fetch_articles(self, limit: int | None = None) -> list[Article]:
        self._load_sections()
        articles: list[Article] = []
        for raw in self._iter_raw_articles():
            articles.append(self._to_article(raw))
            if limit and len(articles) >= limit:
                break
        if not articles:
            raise ZendeskAPIError("Zendesk API returned zero articles")
        return articles

    def _load_sections(self) -> None:
        url = f"{self.base_url}/api/v2/help_center/{self.locale}/sections.json"
        try:
            for page in self._paginate(url, "sections"):
                for s in page:
                    self._sections[s["id"]] = s.get("name", "")
        except Exception as exc: 
            log.warning("Could not load section names: %s", exc)

    def _iter_raw_articles(self) -> Iterator[dict]:
        url = (
            f"{self.base_url}/api/v2/help_center/{self.locale}/articles.json"
            f"?page[size]={settings.page_size}&sort_by=updated_at&sort_order=desc"
        )
        for page in self._paginate(url, "articles"):
            yield from page

    def _paginate(self, url: str, key: str) -> Iterator[list[dict]]:
        next_url = url
        seen = 0
        while next_url:
            resp = self._session.get(next_url, timeout=settings.request_timeout)
            if resp.status_code != 200:
                raise ZendeskAPIError(
                    f"GET {next_url} -> HTTP {resp.status_code}: {resp.text[:200]}"
                )
            try:
                payload = resp.json()
            except ValueError as exc:
                raise ZendeskAPIError(f"Invalid JSON from {next_url}: {exc}") from exc

            items = payload.get(key, [])
            yield items
            seen += len(items)
            next_url = payload.get("next_page")
            if next_url and seen > 5000: 
                log.warning("Pagination guard triggered after %s items", seen)
                break

    def _to_article(self, raw: dict) -> Article:
        section_id = raw.get("section_id")
        return Article(
            id=str(raw["id"]),
            title=raw.get("title", "Untitled"),
            url=raw.get("html_url", ""),
            section=self._sections.get(section_id, "General"),
            updated_at=raw.get("updated_at", ""),
            html=raw.get("body") or "",
            source="api",
        )