import re

from .ingest import load_chunks


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


def retrieve(query: str, limit: int = 3) -> list[dict]:
    """Retrieve portfolio chunks using deterministic keyword matching."""

    query_words = tokenize(query)

    if not query_words or limit <= 0:
        return []

    results = []

    for chunk in load_chunks():
        chunk_words = tokenize(chunk["content"])

        score = len(query_words & chunk_words)

        if score > 0:
            results.append(
                {
                    "source": chunk["source"],
                    "content": chunk["content"],
                    "chunk": chunk["chunk"],
                    "score": score,
                }
            )

    results.sort(
        key=lambda item: (
            -item["score"],
            item["source"],
            item["chunk"],
        )
    )

    return results[:limit]
