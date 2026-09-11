"""OpenAI embedding service for semantic RAG retrieval."""

from __future__ import annotations

from openai import OpenAI

from ..config import settings


class OpenAIEmbeddingService:
    """Generate embeddings using the configured OpenAI embedding model."""

    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        self.model = settings.embedding_model
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    @property
    def available(self) -> bool:
        """Return True when an OpenAI client is configured."""
        return self.client is not None

    def embed_query(self, text: str) -> list[float]:
        """Generate an embedding for a single search query."""
        if not text or not text.strip():
            raise ValueError("Embedding text cannot be empty.")

        if not self.client:
            raise RuntimeError("OpenAI embedding service is not configured.")

        response = self.client.embeddings.create(
            model=self.model,
            input=text.strip(),
        )

        return response.data[0].embedding

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple documents."""
        if not texts:
            return []

        cleaned_texts = [text.strip() for text in texts]

        if any(not text for text in cleaned_texts):
            raise ValueError("Document embedding text cannot be empty.")

        if not self.client:
            raise RuntimeError("OpenAI embedding service is not configured.")

        response = self.client.embeddings.create(
            model=self.model,
            input=cleaned_texts,
        )

        return [item.embedding for item in response.data]


embedding_service = OpenAIEmbeddingService()
