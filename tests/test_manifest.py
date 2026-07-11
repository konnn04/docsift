import json
import os

from src.state.manifest import DeltaKind, Manifest, content_hash


def test_new_article_is_added(tmp_path):
    m = Manifest(str(tmp_path / "manifest.json"))
    assert m.diff("a1", content_hash("hello")) == DeltaKind.ADDED


def test_unchanged_article_is_skipped(tmp_path):
    path = str(tmp_path / "manifest.json")
    m = Manifest(path)
    h = content_hash("hello")
    m.update("a1", hash_=h, path="articles/a1.md", url="https://x", updated_at="")
    m.save()

    m2 = Manifest(path)
    assert m2.diff("a1", h) == DeltaKind.UNCHANGED


def test_changed_content_is_updated(tmp_path):
    path = str(tmp_path / "manifest.json")
    m = Manifest(path)
    m.update("a1", hash_=content_hash("v1"), path="articles/a1.md", url="https://x", updated_at="")
    m.save()

    m2 = Manifest(path)
    assert m2.diff("a1", content_hash("v2")) == DeltaKind.UPDATED


def test_vector_file_ids_persist_per_provider(tmp_path):
    path = str(tmp_path / "manifest.json")
    m = Manifest(path)
    m.update(
        "a1", hash_="h", path="p", url="u", updated_at="",
        vector_file_ids={"gemini": "fileSearchStores/abc/documents/1"},
    )
    m.update(
        "a1", hash_="h", path="p", url="u", updated_at="",
        vector_file_ids={"some-other-provider": "files/xyz"},
    )
    entry = m.get("a1")
    assert entry["vector_file_ids"] == {
        "gemini": "fileSearchStores/abc/documents/1",
        "some-other-provider": "files/xyz",
    }


def test_manifest_survives_reload(tmp_path):
    path = str(tmp_path / "manifest.json")
    m = Manifest(path)
    m.update("a1", hash_="h", path="p", url="u", updated_at="2026-01-01")
    m.save()
    assert os.path.exists(path)

    with open(path) as f:
        data = json.load(f)
    assert data["a1"]["updated_at"] == "2026-01-01"


def test_remove_and_known_ids(tmp_path):
    m = Manifest(str(tmp_path / "manifest.json"))
    m.update("a1", hash_="h", path="p", url="u", updated_at="")
    m.update("a2", hash_="h2", path="p2", url="u2", updated_at="")
    assert m.known_ids() == {"a1", "a2"}
    m.remove("a1")
    assert m.known_ids() == {"a2"}
