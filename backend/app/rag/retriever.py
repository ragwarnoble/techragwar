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
    "ragwar",
    "tech",
    "software",
    "portfolio",
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

    content_words = tokenize(chunk["content"])

    matched_words = query_words & content_words

    # Base score: unique query-term matches.
    score = len(matched_words)

    # Reward chunks that cover multiple query concepts.
    if len(matched_words) >= 2:
        score += 2

    # Heading matches indicate stronger topical relevance.
    heading_words = tokenize(_heading_text(chunk["content"]))
    score += 3 * len(query_words & heading_words)

    normalized_query = " ".join(
        re.findall(r"[a-zA-Z0-9]+", query.lower())
    )

    normalized_content = " ".join(
        re.findall(r"[a-zA-Z0-9]+", chunk["content"].lower())
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
