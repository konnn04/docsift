from __future__ import annotations
import re

from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_md

from src.scraper.models import Article

STRIP_SELECTORS = [
    "script", "style", "nav", "header", "footer", "aside",
    ".article-votes", ".article-comments", ".breadcrumbs", ".sidenav",
    ".social-share", "[class*='cookie']", "[id*='cookie']",
]


def clean_html(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html or "", "html.parser")
    for sel in STRIP_SELECTORS:
        for tag in soup.select(sel):
            tag.decompose()
    for pre in soup.select("pre code[class]"):
        classes = " ".join(pre.get("class", []))
        m = re.search(r"language-(\w+)", classes)
        if m:
            pre["data-lang"] = m.group(1)
    return str(soup)


def _postprocess(md: str) -> str:
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"data-lang=\"(\w+)\"", "", md)
    return md.strip() + "\n"


def article_to_markdown(article: Article) -> str:
    cleaned = clean_html(article.html)
    body_md = html_to_md(
        cleaned,
        heading_style="ATX",
        bullets="-",
        code_language="",
        strip=["img"], 
    )
    body_md = _postprocess(body_md)

    front_matter = (
        f"# {article.title}\n\n"
        f"Article URL: {article.url}\n"
        f"Section: {article.section}\n"
    )
    if article.updated_at:
        front_matter += f"Last Updated: {article.updated_at}\n"
    front_matter += "\n---\n\n"

    return front_matter + body_md