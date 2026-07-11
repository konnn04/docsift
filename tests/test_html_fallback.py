import responses

from src.scraper.html_fallback import HTMLFallbackError, HTMLFallbackScraper

BASE = "https://support.optisigns.com"
SITEMAP = f"""<?xml version="1.0"?>
<urlset>
<url><loc>{BASE}/hc/fr/articles/1-getting-started</loc></url>
<url><loc>{BASE}/hc/en-us/articles/1-getting-started</loc></url>
</urlset>"""
ARTICLE_PAGE = """
<html><head><title>Getting Started</title></head>
<body>
<nav>site nav junk</nav>
<h1>Getting Started</h1>
<div class="article-body"><p>Welcome to the docs.</p></div>
</body></html>
"""


@responses.activate
def test_fallback_scrapes_articles_from_sitemap():
    responses.add(responses.GET, f"{BASE}/hc/sitemap.xml", body=SITEMAP, status=200)
    responses.add(
        responses.GET,
        f"{BASE}/hc/en-us/articles/1-getting-started",
        body=ARTICLE_PAGE,
        status=200,
    )

    articles = HTMLFallbackScraper(base_url=BASE).fetch_articles()
    assert len(articles) == 1
    assert articles[0].title == "Getting Started"
    assert "Welcome to the docs" in articles[0].html
    assert articles[0].source == "html_fallback"


@responses.activate
def test_fallback_ignores_other_locale_urls_in_sitemap():
    responses.add(responses.GET, f"{BASE}/hc/sitemap.xml", body=SITEMAP, status=200)
    responses.add(
        responses.GET,
        f"{BASE}/hc/en-us/articles/1-getting-started",
        body=ARTICLE_PAGE,
        status=200,
    )
    articles = HTMLFallbackScraper(base_url=BASE).fetch_articles()
    assert len(articles) == 1
    assert all("/hc/fr/" not in a.url for a in articles)


@responses.activate
def test_fallback_raises_when_sitemap_missing():
    responses.add(responses.GET, f"{BASE}/hc/sitemap.xml", status=404)

    try:
        HTMLFallbackScraper(base_url=BASE).fetch_articles()
        assert False, "expected HTMLFallbackError"
    except HTMLFallbackError:
        pass


@responses.activate
def test_fallback_skips_pages_without_article_body():
    responses.add(responses.GET, f"{BASE}/hc/sitemap.xml", body=SITEMAP, status=200)
    responses.add(
        responses.GET,
        f"{BASE}/hc/en-us/articles/1-getting-started",
        body="<html><body><p>no article container here</p></body></html>",
        status=200,
    )
    try:
        HTMLFallbackScraper(base_url=BASE).fetch_articles()
        assert False, "expected HTMLFallbackError"
    except HTMLFallbackError:
        pass
