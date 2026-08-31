import re
from collections import Counter

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


def _heading_text(content: str) -> str:
    headings = []

    for line in content.splitlines():
        if line.startswith("#"):
            headings.append(line)

    return " ".join(headings)


def _score_chunk(query: str, chunk: dict) -> int:
    query_words = tokenize(query)

    if not query_words:
        return 0

    content = chunk["content"]
    content_words = re.findall(
        r"[a-zA-Z0-9]+",
        content.lower(),
    )

    word_counts = Counter(content_words)

    score = 0

    for word in query_words:
        if word in word_counts:
            score += 1
            score += min(word_counts[word] - 1, 2)

    heading_words = tokenize(_heading_text(content))

    score += 3 * len(query_words & heading_words)

    normalized_query = " ".join(
        re.findall(r"[a-zA-Z0-9]+", query.lower())
    )

    normalized_content = " ".join(
        re.findall(r"[a-zA-Z0-9]+", content.lower())
    )

    if normalized_query and normalized_query in normalized_content:
        score += 5

    return score


def retrieve(
    query: str,
    limit: int = 3,
) -> list[dict]:
    """Retrieve portfolio chunks using deterministic weighted scoring."""

    query_words = tokenize(query)

    if not query_words or limit <= 0:
        return []

    results = []

    for chunk in load_chunks():
        score = _score_chunk(query, chunk)

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
