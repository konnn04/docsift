import responses

from src.scraper.zendesk_client import ZendeskAPIError, ZendeskClient


BASE = "https://support.optisigns.com"


@responses.activate
def test_fetch_articles_success(zendesk_articles_page_1, zendesk_sections_page):
    responses.add(
        responses.GET,
        f"{BASE}/api/v2/help_center/en-us/sections.json",
        json=zendesk_sections_page,
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/api/v2/help_center/en-us/articles.json",
        json=zendesk_articles_page_1,
        status=200,
        match_querystring=False,
    )

    client = ZendeskClient(base_url=BASE)
    articles = client.fetch_articles()

    assert len(articles) == 1
    assert articles[0].title == "Getting started"
    assert articles[0].section == "Getting Started"
    assert articles[0].source == "api"


@responses.activate
def test_fetch_articles_paginates(zendesk_sections_page):
    page1 = {
        "articles": [{"id": 1, "title": "A", "html_url": "u1", "section_id": 10,
                       "updated_at": "", "body": "<p>1</p>"}],
        "next_page": f"{BASE}/api/v2/help_center/en-us/articles.json?page=2",
    }
    page2 = {
        "articles": [{"id": 2, "title": "B", "html_url": "u2", "section_id": 10,
                       "updated_at": "", "body": "<p>2</p>"}],
        "next_page": None,
    }
    responses.add(responses.GET, f"{BASE}/api/v2/help_center/en-us/sections.json",
                   json=zendesk_sections_page, status=200)
    responses.add(responses.GET, f"{BASE}/api/v2/help_center/en-us/articles.json",
                   json=page1, status=200, match_querystring=False)
    responses.add(responses.GET, f"{BASE}/api/v2/help_center/en-us/articles.json?page=2",
                   json=page2, status=200, match_querystring=False)

    articles = ZendeskClient(base_url=BASE).fetch_articles()
    assert [a.id for a in articles] == ["1", "2"]


@responses.activate
def test_fetch_articles_paginates_cursor_style(zendesk_sections_page):
    # Zendesk's newer Help Center API uses cursor pagination (`links.next` +
    # `meta.has_more`) instead of the legacy `next_page` field.
    page1 = {
        "articles": [{"id": 1, "title": "A", "html_url": "u1", "section_id": 10,
                       "updated_at": "", "body": "<p>1</p>"}],
        "meta": {"has_more": True},
        "links": {"next": f"{BASE}/api/v2/help_center/en-us/articles.json?page%5Bafter%5D=abc"},
    }
    page2 = {
        "articles": [{"id": 2, "title": "B", "html_url": "u2", "section_id": 10,
                       "updated_at": "", "body": "<p>2</p>"}],
        "meta": {"has_more": False},
        "links": {"next": None},
    }
    responses.add(responses.GET, f"{BASE}/api/v2/help_center/en-us/sections.json",
                   json=zendesk_sections_page, status=200)
    responses.add(responses.GET, f"{BASE}/api/v2/help_center/en-us/articles.json",
                   json=page1, status=200, match_querystring=False)
    responses.add(responses.GET, f"{BASE}/api/v2/help_center/en-us/articles.json?page%5Bafter%5D=abc",
                   json=page2, status=200, match_querystring=False)

    articles = ZendeskClient(base_url=BASE).fetch_articles()
    assert [a.id for a in articles] == ["1", "2"]


@responses.activate
def test_fetch_articles_raises_on_http_error(zendesk_sections_page):
    responses.add(responses.GET, f"{BASE}/api/v2/help_center/en-us/sections.json",
                   json=zendesk_sections_page, status=200)
    responses.add(responses.GET, f"{BASE}/api/v2/help_center/en-us/articles.json",
                   json={"error": "rate limited"}, status=429, match_querystring=False)

    try:
        ZendeskClient(base_url=BASE).fetch_articles()
        assert False, "expected ZendeskAPIError"
    except ZendeskAPIError:
        pass


@responses.activate
def test_fetch_articles_raises_on_empty_result(zendesk_sections_page):
    responses.add(responses.GET, f"{BASE}/api/v2/help_center/en-us/sections.json",
                   json=zendesk_sections_page, status=200)
    responses.add(responses.GET, f"{BASE}/api/v2/help_center/en-us/articles.json",
                   json={"articles": [], "next_page": None}, status=200, match_querystring=False)

    try:
        ZendeskClient(base_url=BASE).fetch_articles()
        assert False, "expected ZendeskAPIError"
    except ZendeskAPIError:
        pass
