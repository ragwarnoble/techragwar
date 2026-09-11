from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from app.rag.openai_embeddings import OpenAIEmbeddingService


def test_service_without_api_key_is_unavailable():
    with patch(
        "app.rag.openai_embeddings.settings.openai_api_key",
        "",
    ):
        service = OpenAIEmbeddingService()

    assert service.client is None
    assert service.available is False


def test_service_with_api_key_is_available():
    mock_client = Mock()

    with (
        patch(
            "app.rag.openai_embeddings.settings.openai_api_key",
            "test-key",
        ),
        patch(
            "app.rag.openai_embeddings.OpenAI",
            return_value=mock_client,
        ),
    ):
        service = OpenAIEmbeddingService()

    assert service.client is mock_client
    assert service.available is True


def test_embed_query_rejects_empty_text():
    service = OpenAIEmbeddingService()
    service.client = Mock()

    with pytest.raises(ValueError, match="Embedding text cannot be empty"):
        service.embed_query("")


def test_embed_query_rejects_whitespace():
    service = OpenAIEmbeddingService()
    service.client = Mock()

    with pytest.raises(ValueError, match="Embedding text cannot be empty"):
        service.embed_query("   ")


def test_embed_query_requires_configured_client():
    service = OpenAIEmbeddingService()
    service.client = None

    with pytest.raises(
        RuntimeError,
        match="OpenAI embedding service is not configured",
    ):
        service.embed_query("hello")


def test_embed_query_strips_text_and_returns_embedding():
    service = OpenAIEmbeddingService()
    mock_client = Mock()

    mock_client.embeddings.create.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(embedding=[0.1, 0.2, 0.3]),
        ]
    )

    service.client = mock_client
    service.model = "text-embedding-3-small"

    result = service.embed_query("  hello world  ")

    mock_client.embeddings.create.assert_called_once_with(
        model="text-embedding-3-small",
        input="hello world",
    )
    assert result == [0.1, 0.2, 0.3]


def test_embed_documents_empty_list_returns_empty_list():
    service = OpenAIEmbeddingService()
    service.client = Mock()

    assert service.embed_documents([]) == []

    service.client.embeddings.create.assert_not_called()


def test_embed_documents_rejects_blank_document():
    service = OpenAIEmbeddingService()
    service.client = Mock()

    with pytest.raises(
        ValueError,
        match="Document embedding text cannot be empty",
    ):
        service.embed_documents(["hello", "   "])


def test_embed_documents_requires_configured_client():
    service = OpenAIEmbeddingService()
    service.client = None

    with pytest.raises(
        RuntimeError,
        match="OpenAI embedding service is not configured",
    ):
        service.embed_documents(["hello"])


def test_embed_documents_strips_inputs_and_preserves_order():
    service = OpenAIEmbeddingService()
    mock_client = Mock()

    mock_client.embeddings.create.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(embedding=[0.1, 0.2]),
            SimpleNamespace(embedding=[0.3, 0.4]),
        ]
    )

    service.client = mock_client
    service.model = "text-embedding-3-small"

    result = service.embed_documents(
        [
            "  first document  ",
            "second document   ",
        ]
    )

    mock_client.embeddings.create.assert_called_once_with(
        model="text-embedding-3-small",
        input=["first document", "second document"],
    )

    assert result == [
        [0.1, 0.2],
        [0.3, 0.4],
    ]
