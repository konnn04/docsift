import pytest

from src.scraper.models import Article


@pytest.fixture
def sample_article() -> Article:
    return Article(
        id="360000111222",
        title="How do I add a YouTube video?",
        url="https://support.optisigns.com/hc/en-us/articles/360000111222",
        section="Content Sources",
        updated_at="2026-01-15T10:00:00Z",
        html=(
            "<nav>skip me</nav>"
            "<div class='article-body'>"
            "<h2>Steps</h2>"
            "<p>Open the <strong>Editor</strong> and click "
            "<a href='/hc/en-us/articles/999'>Add Content</a>.</p>"
            "<pre><code class='language-js'>console.log('hi')</code></pre>"
            "</div>"
        ),
        source="api",
    )


@pytest.fixture
def zendesk_articles_page_1() -> dict:
    return {
        "articles": [
            {
                "id": 1,
                "title": "Getting started",
                "html_url": "https://support.optisigns.com/hc/en-us/articles/1",
                "section_id": 10,
                "updated_at": "2026-01-01T00:00:00Z",
                "body": "<div>Welcome to OptiSigns</div>",
            }
        ],
        "next_page": None,
    }


@pytest.fixture
def zendesk_sections_page() -> dict:
    return {"sections": [{"id": 10, "name": "Getting Started"}]}
