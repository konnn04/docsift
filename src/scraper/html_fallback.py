from __future__ import annotations
import logging
import re
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.config import settings
from src.scraper.models import Article

log = logging.getLogger(__name__)

ARTICLE_BODY_SELECTORS = [
    "div.article-body",
    "div.article__body",
    'div[class*="article-body"]',
    "article .body",
    "article",
]
NOISE_SELECTORS = [
    "nav", "header", "footer", "script", "style", "aside",
    ".article-votes", ".article-comments", ".breadcrumbs", ".sidenav",
]


class HTMLFallbackError(Exception):
    pass


class HTMLFallbackScraper:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.help_center_base).rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": settings.user_agent})

    def fetch_articles(self, limit: int | None = None) -> list[Article]:
        urls = list(self._discover_article_urls())
        if not urls:
            raise HTMLFallbackError("Sitemap discovery found zero article URLs")
        if limit:
            urls = urls[:limit]

        articles: list[Article] = []
        for url in urls:
            try:
                articles.append(self._scrape_one(url))
            except Exception as exc:
                log.warning("Skipping %s (%s)", url, exc)
        if not articles:
            raise HTMLFallbackError("Could not scrape any article from discovered URLs")
        return articles

    def _discover_article_urls(self) -> Iterable[str]:
        sm_url = f"{self.base_url}/hc/sitemap.xml"
        locale_marker = f"/hc/{settings.locale}/articles/"
        try:
            resp = self._session.get(sm_url, timeout=settings.request_timeout)
            if resp.status_code != 200:
                return []
            urls = re.findall(r"<loc>(.*?)</loc>", resp.text)
            article_urls = [u for u in urls if locale_marker in u]
            return dict.fromkeys(article_urls)  
        except requests.RequestException as exc:
            log.warning("Sitemap fetch failed for %s: %s", sm_url, exc)
        return []

    def _scrape_one(self, url: str) -> Article:
        resp = self._session.get(url, timeout=settings.request_timeout)
        if resp.status_code != 200:
            raise HTMLFallbackError(f"HTTP {resp.status_code} for {url}")
        soup = BeautifulSoup(resp.text, "html.parser")

        title_tag = soup.select_one("h1") or soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else url.rsplit("/", 1)[-1]

        for sel in NOISE_SELECTORS:
            for tag in soup.select(sel):
                tag.decompose()

        body = None
        for sel in ARTICLE_BODY_SELECTORS:
            body = soup.select_one(sel)
            if body:
                break
        if body is None:
            raise HTMLFallbackError("No recognizable article body container")

        for tag, attr in (("a", "href"), ("img", "src")):
            for el in body.find_all(tag):
                if el.get(attr):
                    el[attr] = urljoin(url, el[attr])

        section_tag = soup.select_one(".breadcrumbs li:nth-last-child(2), nav.breadcrumbs a")
        section = section_tag.get_text(strip=True) if section_tag else "General"

        slug_id = re.sub(r"[^a-zA-Z0-9]+", "-", url.rstrip("/").rsplit("/", 1)[-1]).strip("-")

        return Article(
            id=slug_id or title,
            title=title,
            url=url,
            section=section,
            updated_at="",  
            html=str(body),
            source="html_fallback",
        )