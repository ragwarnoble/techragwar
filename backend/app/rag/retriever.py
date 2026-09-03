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
    "for",
    "of",
    "to",
    "in",
    "on",
    "with",
    "portfolio",
    "ragwar",
    "tech",

    # Generic query-intent words.
    "tools",
    "technology",
    "technologies",
    "building",
    "software",
    "kind",
    "type",
    "prefer",
    "system",
}

QUERY_EXPANSIONS = {
    "server-side": "backend",
    "server side": "backend",
    "built": "build",
}


def normalize(text: str) -> str:
    normalized = text.lower()

    for phrase, replacement in QUERY_EXPANSIONS.items():
        normalized = normalized.replace(phrase, replacement)

    return normalized


def tokenize(text: str) -> list[str]:
    normalized = normalize(text)

    words = re.findall(
        r"[a-zA-Z0-9]+",
        normalized,
    )

    return [
        word
        for word in words
        if len(word) > 2 and word not in STOP_WORDS
    ]


def _heading_text(content: str) -> str:
    return " ".join(
        line.lstrip("#").strip()
        for line in content.splitlines()
        if line.startswith("#")
    )


def _score_chunk(query: str, chunk: dict) -> int:
    query_words = set(tokenize(query))

    if not query_words:
        return 0

    content = normalize(chunk["content"])
    content_words = set(tokenize(content))

    matched_words = query_words & content_words

    if not matched_words:
        return 0

    score = 0

    # ---------------------------------------------------------
    # 1. Term coverage
    # ---------------------------------------------------------
    score += len(matched_words) * 2

    # ---------------------------------------------------------
    # 2. Reward chunks matching most/all query concepts
    # ---------------------------------------------------------
    coverage = len(matched_words) / len(query_words)

    if coverage >= 0.75:
        score += 4
    elif coverage >= 0.5:
        score += 2

    # ---------------------------------------------------------
    # 3. Heading matches are strong signals
    # ---------------------------------------------------------
    heading_words = set(
        tokenize(
            _heading_text(chunk["content"])
        )
    )

    heading_matches = query_words & heading_words

    score += len(heading_matches) * 8

    # ---------------------------------------------------------
    # 4. Exact phrase match
    # ---------------------------------------------------------
    normalized_query = normalize(query)

    query_tokens = re.findall(
        r"[a-zA-Z0-9]+",
        normalized_query,
    )

    if len(query_tokens) >= 2:
        phrase = " ".join(query_tokens)

        if phrase in content:
            score += 8

    # ---------------------------------------------------------
    # 5. Reward matching terms appearing near each other
    # ---------------------------------------------------------
    words = tokenize(content)

    positions = {
        word: index
        for index, word in enumerate(words)
        if word in query_words
    }

    if len(positions) >= 2:
        indexes = sorted(positions.values())

        distance = indexes[-1] - indexes[0]

        if distance <= 5:
            score += 3
        elif distance <= 10:
            score += 1

    return score


def retrieve(
    query: str,
    limit: int = 3,
) -> list[dict]:
    """Retrieve portfolio chunks using deterministic weighted scoring."""

    if limit <= 0:
        return []

    if not tokenize(query):
        return []

    results = []

    for chunk in load_chunks():
        score = _score_chunk(
            query,
            chunk,
        )

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

    # Prefer distinct sources so top-k represents multiple
    # independent knowledge documents when available.
    selected = []
    seen_sources = set()

    for result in results:
        if result["source"] in seen_sources:
            continue

        selected.append(result)
        seen_sources.add(result["source"])

        if len(selected) >= limit:
            break

    return selected
