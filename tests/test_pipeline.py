import os

from src.pipeline import run_pipeline
from src.providers.base import KnowledgeBaseProvider, UploadResult
from src.scraper.models import Article


class RecordingProvider(KnowledgeBaseProvider):
    name = "fake"

    def __init__(self):
        self.uploaded = []
        self.deleted = []

    def ensure_store(self):
        return "store-1"

    def upload_file(self, path, display_name):
        self.uploaded.append(display_name)
        return UploadResult(provider=self.name, remote_file_id=f"file-{len(self.uploaded)}")

    def delete_file(self, remote_file_id):
        self.deleted.append(remote_file_id)

    def configure_assistant(self, system_prompt):
        pass

    def ask(self, question, system_prompt):
        raise NotImplementedError


def _articles(n=2):
    return [
        Article(
            id=str(i),
            title=f"Article {i}",
            url=f"https://support.optisigns.com/a{i}",
            section="General",
            updated_at="2026-01-01T00:00:00Z",
            html=f"<div class='article-body'><p>Body {i}</p></div>",
        )
        for i in range(n)
    ]


def test_chunk_estimate_accumulates_for_any_provider(tmp_path, monkeypatch):
    monkeypatch.setattr("src.pipeline.scrape_articles", lambda *a, **k: (_articles(2), "zendesk_api"))
    provider = RecordingProvider()  # name="fake" -- estimate is provider-agnostic now

    report = run_pipeline(
        providers=[provider],
        articles_dir=str(tmp_path / "articles"),
        manifest_path=str(tmp_path / "manifest.json"),
    )

    assert report.embedded_files == 2
    assert report.embedded_chunks_estimate >= 2  # at least 1 chunk per file


def test_first_run_uploads_everything(tmp_path, monkeypatch):
    monkeypatch.setattr("src.pipeline.scrape_articles", lambda *a, **k: (_articles(2), "zendesk_api"))
    provider = RecordingProvider()

    report = run_pipeline(
        providers=[provider],
        articles_dir=str(tmp_path / "articles"),
        manifest_path=str(tmp_path / "manifest.json"),
    )

    assert report.added == 2
    assert report.updated == 0
    assert report.skipped == 0
    assert len(provider.uploaded) == 2
    assert os.path.exists(tmp_path / "manifest.json")
    # Chunk estimation is provider-agnostic (see src/utils.py), so it's
    # populated regardless of which provider handled the upload.
    assert report.embedded_files == 2
    assert report.embedded_chunks_estimate >= 2


def test_second_run_with_no_changes_skips_everything(tmp_path, monkeypatch):
    monkeypatch.setattr("src.pipeline.scrape_articles", lambda *a, **k: (_articles(2), "zendesk_api"))
    provider = RecordingProvider()
    common = dict(
        providers=[provider],
        articles_dir=str(tmp_path / "articles"),
        manifest_path=str(tmp_path / "manifest.json"),
    )
    run_pipeline(**common)
    provider.uploaded.clear()

    report = run_pipeline(**common)
    assert report.skipped == 2
    assert report.added == 0
    assert report.updated == 0
    assert provider.uploaded == []


def test_changed_article_is_reuploaded_and_old_file_deleted(tmp_path, monkeypatch):
    provider = RecordingProvider()
    common = dict(
        providers=[provider],
        articles_dir=str(tmp_path / "articles"),
        manifest_path=str(tmp_path / "manifest.json"),
    )

    monkeypatch.setattr("src.pipeline.scrape_articles", lambda *a, **k: (_articles(1), "zendesk_api"))
    run_pipeline(**common)

    changed = [
        Article(id="0", title="Article 0", url="https://support.optisigns.com/a0",
                 section="General", updated_at="2026-02-01T00:00:00Z",
                 html="<div class='article-body'><p>Body 0 CHANGED</p></div>")
    ]
    monkeypatch.setattr("src.pipeline.scrape_articles", lambda *a, **k: (changed, "zendesk_api"))
    report = run_pipeline(**common)

    assert report.updated == 1
    assert report.added == 0
    assert len(provider.deleted) == 1  # old file_id was cleaned up


def test_removed_article_is_deleted_from_manifest_and_store(tmp_path, monkeypatch):
    provider = RecordingProvider()
    common = dict(
        providers=[provider],
        articles_dir=str(tmp_path / "articles"),
        manifest_path=str(tmp_path / "manifest.json"),
    )
    monkeypatch.setattr("src.pipeline.scrape_articles", lambda *a, **k: (_articles(2), "zendesk_api"))
    run_pipeline(**common)

    monkeypatch.setattr("src.pipeline.scrape_articles", lambda *a, **k: (_articles(1), "zendesk_api"))
    report = run_pipeline(**common)

    assert report.deleted == 1
    assert len(provider.deleted) == 1


def test_removed_article_local_md_file_is_deleted(tmp_path, monkeypatch):
    provider = RecordingProvider()
    articles_dir = tmp_path / "articles"
    common = dict(
        providers=[provider],
        articles_dir=str(articles_dir),
        manifest_path=str(tmp_path / "manifest.json"),
    )
    monkeypatch.setattr("src.pipeline.scrape_articles", lambda *a, **k: (_articles(2), "zendesk_api"))
    run_pipeline(**common)
    removed_slug_path = articles_dir / "1-article-1.md"
    assert removed_slug_path.exists()

    monkeypatch.setattr("src.pipeline.scrape_articles", lambda *a, **k: (_articles(1), "zendesk_api"))
    run_pipeline(**common)

    assert not removed_slug_path.exists()


def test_renamed_article_drops_orphan_md_file(tmp_path, monkeypatch):
    provider = RecordingProvider()
    articles_dir = tmp_path / "articles"
    common = dict(
        providers=[provider],
        articles_dir=str(articles_dir),
        manifest_path=str(tmp_path / "manifest.json"),
    )
    monkeypatch.setattr("src.pipeline.scrape_articles", lambda *a, **k: (_articles(1), "zendesk_api"))
    run_pipeline(**common)
    old_path = articles_dir / "0-article-0.md"
    assert old_path.exists()

    renamed = [
        Article(id="0", title="Totally Renamed Title", url="https://support.optisigns.com/a0",
                 section="General", updated_at="2026-02-01T00:00:00Z",
                 html="<div class='article-body'><p>Body 0 renamed</p></div>")
    ]
    monkeypatch.setattr("src.pipeline.scrape_articles", lambda *a, **k: (renamed, "zendesk_api"))
    report = run_pipeline(**common)

    assert report.updated == 1
    assert not old_path.exists()  # orphan under the old slug is cleaned up
    assert (articles_dir / "0-totally-renamed-title.md").exists()
