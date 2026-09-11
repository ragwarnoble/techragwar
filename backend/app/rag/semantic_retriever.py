"""Semantic retrieval using OpenAI embeddings."""

from __future__ import annotations

from .ingest import load_chunks
from .openai_embeddings import embedding_service


def cosine_similarity(
    query_vector: list[float],
    document_vector: list[float],
) -> float:
    """Calculate cosine similarity between two vectors."""

    if not query_vector or not document_vector:
        return 0.0

    query_norm = sum(
        value * value
        for value in query_vector
    ) ** 0.5

    document_norm = sum(
        value * value
        for value in document_vector
    ) ** 0.5

    if query_norm == 0 or document_norm == 0:
        return 0.0

    dot_product = sum(
        query_value * document_value
        for query_value, document_value in zip(
            query_vector,
            document_vector,
        )
    )

    return dot_product / (
        query_norm * document_norm
    )


def build_index(
    chunks: list[dict] | None = None,
) -> list[dict]:
    """
    Build an in-memory semantic index.

    Document embeddings are generated through the
    configured OpenAI embedding service.
    """

    if chunks is None:
        chunks = load_chunks()

    if not chunks:
        return []

    texts = [
        chunk["content"]
        for chunk in chunks
    ]

    embeddings = embedding_service.embed_documents(
        texts
    )

    return [
        {
            **chunk,
            "embedding": embedding,
        }
        for chunk, embedding in zip(
            chunks,
            embeddings,
        )
    ]


def retrieve_semantic(
    query: str,
    embedded_chunks: list[dict] | None = None,
    limit: int = 3,
) -> list[dict]:
    """Retrieve chunks using semantic similarity."""

    if limit <= 0:
        return []

    if not query or not query.strip():
        return []

    if embedded_chunks is None:
        embedded_chunks = build_index()

    if not embedded_chunks:
        return []

    query_embedding = embedding_service.embed_query(
        query
    )

    scored = []

    for chunk in embedded_chunks:
        score = cosine_similarity(
            query_embedding,
            chunk["embedding"],
        )

        scored.append(
            {
                "source": chunk["source"],
                "content": chunk["content"],
                "chunk": chunk["chunk"],
                "score": float(score),
            }
        )

    scored.sort(
        key=lambda item: (
            -item["score"],
            item["source"],
            item["chunk"],
        )
    )

    return scored[:limit]
