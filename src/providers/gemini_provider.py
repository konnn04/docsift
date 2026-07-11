from __future__ import annotations
import logging
import time
from typing import Callable, Iterator

from src.config import settings
from src.providers.base import KnowledgeBaseProvider, ProviderError, QueryResult, UploadResult

log = logging.getLogger(__name__)


class GeminiProvider(KnowledgeBaseProvider):
    name = "gemini"

    def __init__(self):
        if not settings.gemini_api_key:
            raise ProviderError("GEMINI_API_KEY is not set")
        try:
            from google import genai
        except ImportError as exc:
            raise ProviderError(f"google-genai package not installed: {exc}") from exc

        self._genai = genai
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._store_name: str | None = None

    def ensure_store(self) -> str:
        if self._store_name:
            return self._store_name
        try:
            for store in self._client.file_search_stores.list():
                if store.display_name == settings.gemini_store_name:
                    self._store_name = store.name
                    log.info("Reusing existing Gemini file search store %s", store.name)
                    return store.name
            store = self._client.file_search_stores.create(
                config={"display_name": settings.gemini_store_name}
            )
            self._store_name = store.name
            log.info("Created Gemini file search store %s", store.name)
            return store.name
        except Exception as exc:
            raise ProviderError(f"Failed to ensure file search store: {exc}") from exc

    def upload_file(self, path: str, display_name: str) -> UploadResult:
        store_name = self.ensure_store()
        try:
            op = self._client.file_search_stores.upload_to_file_search_store(
                file=path,
                file_search_store_name=store_name,
                config={"display_name": display_name},
            )
            waited = 0
            while not op.done and waited < settings.request_timeout * 6:
                time.sleep(2)
                waited += 2
                op = self._client.operations.get(op)
            if not op.done:
                raise ProviderError(f"Timed out indexing {display_name}")
            remote_id = getattr(op.response, "document_name", None) or op.name
            return UploadResult(provider=self.name, remote_file_id=remote_id)
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(f"Upload failed for {display_name}: {exc}") from exc

    def delete_file(self, remote_file_id: str) -> None:
        try:
            self._client.file_search_stores.documents.delete(
                name=remote_file_id, config={"force": True}
            )
        except Exception as exc:
            log.warning("Could not delete stale Gemini document %s: %s", remote_file_id, exc)

    def configure_assistant(self, system_prompt: str) -> None:
        return None  

    def ask(self, question: str, system_prompt: str) -> QueryResult:
        from google.genai import types

        store_name = self.ensure_store()
        try:
            resp = self._client.models.generate_content(
                model=settings.gemini_model,
                contents=question,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(file_search_store_names=[store_name])
                        )
                    ],
                ),
            )
        except Exception as exc:
            raise ProviderError(f"Query failed: {exc}") from exc

        answer = getattr(resp, "text", "") or ""
        citations = self._extract_citations(resp)
        return QueryResult(provider=self.name, answer=answer, citations=citations)

    def ask_stream(
        self,
        question: str,
        system_prompt: str,
        on_citations: Callable[[list[str]], None] | None = None,
    ) -> Iterator[str]:
        from google.genai import types

        store_name = self.ensure_store()
        citations: list[str] = []
        try:
            stream = self._client.models.generate_content_stream(
                model=settings.gemini_model,
                contents=question,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(file_search_store_names=[store_name])
                        )
                    ],
                ),
            )
            for chunk in stream:
                if chunk.text:
                    yield chunk.text
                citations.extend(c for c in self._extract_citations(chunk) if c not in citations)
        except Exception as exc:
            raise ProviderError(f"Streaming query failed: {exc}") from exc
        finally:
            if on_citations is not None:
                on_citations(citations)

    @staticmethod
    def _extract_citations(resp) -> list[str]:
        citations: list[str] = []
        try:
            for candidate in resp.candidates:
                gm = getattr(candidate, "grounding_metadata", None)
                for chunk in getattr(gm, "grounding_chunks", []) or []:
                    src = getattr(chunk, "retrieved_context", None)
                    if src and getattr(src, "title", None):
                        citations.append(src.title)
        except Exception:
            pass
        return citations
