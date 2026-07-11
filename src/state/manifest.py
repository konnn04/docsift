from __future__ import annotations
import hashlib
import json
import os
from dataclasses import dataclass, field
from enum import Enum


class DeltaKind(str, Enum):
    ADDED = "added"
    UPDATED = "updated"
    UNCHANGED = "skipped"


@dataclass
class DeltaEntry:
    article_id: str
    kind: DeltaKind
    path: str


def content_hash(markdown: str) -> str:
    return hashlib.sha256(markdown.encode("utf-8")).hexdigest()


class Manifest:
    def __init__(self, path: str):
        self.path = path
        self._data: dict = {}
        self.load()

    def load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = {}

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, sort_keys=True)

    def diff(self, article_id: str, new_hash: str, updated_at: str = "") -> DeltaKind:
        prev = self._data.get(article_id)
        if prev is None:
            return DeltaKind.ADDED
        if updated_at and prev.get("updated_at") == updated_at:
            return DeltaKind.UNCHANGED
        if prev.get("hash") != new_hash:
            return DeltaKind.UPDATED
        return DeltaKind.UNCHANGED

    def update(
        self,
        article_id: str,
        *,
        hash_: str,
        path: str,
        url: str,
        updated_at: str,
        vector_file_ids: dict | None = None,
    ) -> None:
        entry = self._data.get(article_id, {})
        entry.update(
            {
                "hash": hash_,
                "path": path,
                "url": url,
                "updated_at": updated_at,
            }
        )
        if vector_file_ids:
            merged = entry.get("vector_file_ids", {})
            merged.update(vector_file_ids)
            entry["vector_file_ids"] = merged
        self._data[article_id] = entry

    def get(self, article_id: str) -> dict | None:
        return self._data.get(article_id)

    def known_ids(self) -> set[str]:
        return set(self._data.keys())

    def remove(self, article_id: str) -> dict | None:
        return self._data.pop(article_id, None)

    def as_dict(self) -> dict:
        return self._data
