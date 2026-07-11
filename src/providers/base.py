from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Iterator


@dataclass
class UploadResult:
    provider: str
    remote_file_id: str


@dataclass
class QueryResult:
    provider: str
    answer: str
    citations: list[str]


class ProviderError(Exception):
    """Raised for any provider failure (auth, network, quota...) so the
    pipeline can catch it and try the next provider in the fallback chain."""


class KnowledgeBaseProvider(ABC):
    name: str

    @abstractmethod
    def ensure_store(self) -> str:
        """Create the vector store / file-search store if it doesn't exist
        yet, and return its id."""

    @abstractmethod
    def upload_file(self, path: str, display_name: str) -> UploadResult:
        """Upload a single markdown file into the store."""

    @abstractmethod
    def delete_file(self, remote_file_id: str) -> None:
        """Remove a stale file from the store (used on article updates)."""

    @abstractmethod
    def configure_assistant(self, system_prompt: str) -> None:
        """Bind the system prompt to the model config used for querying
        (for Gemini this is passed per-request via system_instruction).
        Kept as an explicit step so the pipeline logs it and so a
        UI-created Assistant/Prompt could be swapped in later without
        changing call sites."""

    @abstractmethod
    def ask(self, question: str, system_prompt: str) -> QueryResult:
        """Ask a grounded question against the store, mirroring the
        Playground/AI Studio sanity check step."""

    def ask_stream(
        self,
        question: str,
        system_prompt: str,
        on_citations: Callable[[list[str]], None] | None = None,
    ) -> Iterator[str]:
        result = self.ask(question, system_prompt)
        if on_citations is not None:
            on_citations(result.citations)
        yield result.answer
