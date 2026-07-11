from src.scraper.markdown_converter import article_to_markdown


def test_article_to_markdown_includes_article_url(sample_article):
    md = article_to_markdown(sample_article)
    assert f"Article URL: {sample_article.url}" in md


def test_article_to_markdown_strips_nav(sample_article):
    md = article_to_markdown(sample_article)
    assert "skip me" not in md


def test_article_to_markdown_preserves_heading(sample_article):
    md = article_to_markdown(sample_article)
    assert "## Steps" in md


def test_article_to_markdown_preserves_relative_link(sample_article):
    md = article_to_markdown(sample_article)
    assert "/hc/en-us/articles/999" in md
    assert "[Add Content]" in md


def test_article_to_markdown_preserves_code_block(sample_article):
    md = article_to_markdown(sample_article)
    assert "```" in md
    assert "console.log" in md


def test_article_to_markdown_normalizes_blank_lines():
    from src.scraper.models import Article

    a = Article(
        id="x",
        title="T",
        url="https://example.com/x",
        section="S",
        updated_at="",
        html="<p>a</p>" + "\n" * 10 + "<p>b</p>",
    )
    md = article_to_markdown(a)
    assert "\n\n\n" not in md
