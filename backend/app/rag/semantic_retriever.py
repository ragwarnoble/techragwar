from functools import lru_cache

from sentence_transformers import SentenceTransformer

from .ingest import load_chunks


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Load the embedding model once per process."""
    return SentenceTransformer(MODEL_NAME)


def cosine_similarity(
    query_vector,
    document_vector,
) -> float:
    """Calculate cosine similarity between two vectors."""

    query_norm = (
        sum(value * value for value in query_vector)
        ** 0.5
    )

    document_norm = (
        sum(value * value for value in document_vector)
        ** 0.5
    )

    if query_norm == 0 or document_norm == 0:
        return 0.0

    dot_product = sum(
        query_value * document_value
        for query_value, document_value
        in zip(query_vector, document_vector)
    )

    return dot_product / (
        query_norm * document_norm
    )


@lru_cache(maxsize=1)
def build_index() -> list[dict]:
    """Embed all knowledge chunks once."""

    chunks = load_chunks()

    if not chunks:
        return []

    model = get_model()

    embeddings = model.encode(
        [
            chunk["content"]
            for chunk in chunks
        ],
        normalize_embeddings=True,
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
    limit: int = 3,
) -> list[dict]:
    """Retrieve chunks using semantic similarity."""

    if limit <= 0:
        return []

    if not query.strip():
        return []

    model = get_model()
    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    )

    scored = []

    for chunk in build_index():
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