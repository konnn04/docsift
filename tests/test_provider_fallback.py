from src.providers.base import KnowledgeBaseProvider, ProviderError, QueryResult, UploadResult
from src.providers.factory import with_fallback


class FakeFailingProvider(KnowledgeBaseProvider):
    name = "flaky-provider"

    def ensure_store(self):
        raise ProviderError("simulated outage")

    def upload_file(self, path, display_name):
        raise ProviderError("simulated outage")

    def delete_file(self, remote_file_id):
        pass

    def configure_assistant(self, system_prompt):
        pass

    def ask(self, question, system_prompt):
        raise ProviderError("simulated outage")


class FakeWorkingProvider(KnowledgeBaseProvider):
    name = "gemini"

    def ensure_store(self):
        return "store-123"

    def upload_file(self, path, display_name):
        return UploadResult(provider=self.name, remote_file_id="file-1")

    def delete_file(self, remote_file_id):
        pass

    def configure_assistant(self, system_prompt):
        pass

    def ask(self, question, system_prompt):
        return QueryResult(provider=self.name, answer="42", citations=["Article URL: x"])


def test_with_fallback_uses_next_provider_on_failure():
    providers = [FakeFailingProvider(), FakeWorkingProvider()]
    provider, result = with_fallback(providers, lambda p: p.ask("q", "sys"))
    assert provider.name == "gemini"
    assert result.answer == "42"


def test_with_fallback_raises_when_all_fail():
    providers = [FakeFailingProvider(), FakeFailingProvider()]
    try:
        with_fallback(providers, lambda p: p.ask("q", "sys"))
        assert False, "expected ProviderError"
    except ProviderError:
        pass
