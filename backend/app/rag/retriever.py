import re

from .ingest import load_markdown_documents


STOP_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "is",
    "are",
    "what",
    "does",
    "do",
    "how",
    "why",
    "where",
    "when",
    "who",
    "use",
    "used",
    "about",
    "tell",
    "me",
}


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())

    return {
        word
        for word in words
        if len(word) > 2 and word not in STOP_WORDS
    }


def load_documents() -> list[dict]:
    """Load documents through the RAG ingestion layer."""

    return load_markdown_documents()


def retrieve(query: str, limit: int = 3) -> list[dict]:
    """Retrieve portfolio documents using deterministic keyword matching."""

    query_words = tokenize(query)

    if not query_words or limit <= 0:
        return []

    results = []

    for document in load_documents():
        document_words = tokenize(document["content"])

        score = len(query_words & document_words)

        if score > 0:
            results.append(
                {
                    "source": document["source"],
                    "content": document["content"],
                    "score": score,
                }
            )

    results.sort(
        key=lambda item: (
            -item["score"],
            item["source"],
        )
    )

    return results[:limit]
