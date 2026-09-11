"""Hybrid lexical and semantic RAG retrieval."""

from __future__ import annotations

import re

from .ingest import load_chunks
from .semantic_retriever import (
    build_index,
    retrieve_semantic,
)


SEMANTIC_THRESHOLD = 0.60

CANDIDATE_K = 5
FINAL_K = 3

RRF_K = 60

LEXICAL_WEIGHT = 1.0
SEMANTIC_WEIGHT = 1.0


HYBRID_STOP_WORDS = {
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
}


def _hybrid_tokens(text: str) -> set[str]:
    """Tokenize text for the hybrid lexical signal."""

    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower(),
    )

    return {
        word
        for word in words
        if len(word) > 2
        and word not in HYBRID_STOP_WORDS
    }


def _hybrid_lexical_score(
    query: str,
    content: str,
) -> int:
    """Calculate lexical concept overlap."""

    query_words = _hybrid_tokens(query)
    content_words = _hybrid_tokens(content)

    if not query_words:
        return 0

    return len(
        query_words & content_words
    )


def _lexical_candidates(
    query: str,
    limit: int = CANDIDATE_K,
) -> list[dict]:
    """Retrieve lexical candidates."""

    if limit <= 0:
        return []

    if not query or not query.strip():
        return []

    results = []

    for chunk in load_chunks():
        score = _hybrid_lexical_score(
            query,
            chunk["content"],
        )

        if score <= 0:
            continue

        results.append(
            {
                "source": chunk["source"],
                "content": chunk["content"],
                "chunk": chunk["chunk"],
                "lexical_score": score,
            }
        )

    results.sort(
        key=lambda item: (
            -item["lexical_score"],
            item["source"],
            item["chunk"],
        )
    )

    return results[:limit]


def _semantic_candidates(
    query: str,
    embedded_chunks: list[dict],
    limit: int = CANDIDATE_K,
) -> list[dict]:
    """Retrieve semantic candidates."""

    if limit <= 0:
        return []

    return retrieve_semantic(
        query,
        embedded_chunks,
        limit=limit,
    )


def _rank_map(
    results: list[dict],
) -> dict[tuple[str, int], int]:
    """Map each chunk to its 1-based retrieval rank."""

    return {
        (
            result["source"],
            result["chunk"],
        ): rank
        for rank, result in enumerate(
            results,
            start=1,
        )
    }


def _fuse_results(
    lexical_results: list[dict],
    semantic_results: list[dict],
) -> list[dict]:
    """
    Fuse lexical and semantic rankings using
    Reciprocal Rank Fusion (RRF).

    RRF avoids directly combining incompatible
    score scales.
    """

    lexical_ranks = _rank_map(
        lexical_results
    )

    semantic_ranks = _rank_map(
        semantic_results
    )

    candidates = {}

    for result in lexical_results:
        key = (
            result["source"],
            result["chunk"],
        )

        candidates[key] = {
            "source": result["source"],
            "content": result["content"],
            "chunk": result["chunk"],
            "lexical_score": result[
                "lexical_score"
            ],
            "semantic_score": 0.0,
        }

    for result in semantic_results:
        key = (
            result["source"],
            result["chunk"],
        )

        if key not in candidates:
            candidates[key] = {
                "source": result["source"],
                "content": result["content"],
                "chunk": result["chunk"],
                "lexical_score": 0,
                "semantic_score": result["score"],
            }
        else:
            candidates[key][
                "semantic_score"
            ] = result["score"]

    fused = []

    for key, result in candidates.items():
        lexical_rank = lexical_ranks.get(key)
        semantic_rank = semantic_ranks.get(key)

        lexical_rrf = (
            LEXICAL_WEIGHT
            / (RRF_K + lexical_rank)
            if lexical_rank is not None
            else 0.0
        )

        semantic_rrf = (
            SEMANTIC_WEIGHT
            / (RRF_K + semantic_rank)
            if semantic_rank is not None
            else 0.0
        )

        rrf_score = (
            lexical_rrf
            + semantic_rrf
        )

        fused.append(
            {
                **result,
                "lexical_rank": lexical_rank,
                "semantic_rank": semantic_rank,
                "lexical_rrf": lexical_rrf,
                "semantic_rrf": semantic_rrf,
                "hybrid_score": rrf_score,
            }
        )

    fused.sort(
        key=lambda item: (
            -item["hybrid_score"],
            item["source"],
            item["chunk"],
        )
    )

    return fused


def _apply_semantic_gate(
    results: list[dict],
    threshold: float = SEMANTIC_THRESHOLD,
) -> list[dict]:
    """Reject candidates below the semantic relevance threshold."""

    return [
        result
        for result in results
        if result["semantic_score"] >= threshold
    ]


def _select_distinct_sources(
    results: list[dict],
    limit: int = FINAL_K,
) -> list[dict]:
    """Prefer one result per source."""

    if limit <= 0:
        return []

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


def build_embedded_chunks() -> list[dict]:
    """
    Build the semantic index for the portfolio knowledge base.

    Document embeddings are generated by the configured
    OpenAI embedding service through semantic_retriever.
    """

    return build_index()


def retrieve_hybrid(
    query: str,
    embedded_chunks: list[dict] | None = None,
    limit: int = FINAL_K,
) -> list[dict]:
    """
    Hybrid retrieval using:

        lexical retrieval
        semantic retrieval
        reciprocal rank fusion
        semantic relevance gate
        source diversity
    """

    if limit <= 0:
        return []

    if not query or not query.strip():
        return []

    if embedded_chunks is None:
        embedded_chunks = build_embedded_chunks()

    if not embedded_chunks:
        return []

    lexical_results = _lexical_candidates(
        query,
        limit=CANDIDATE_K,
    )

    semantic_results = _semantic_candidates(
        query,
        embedded_chunks,
        limit=CANDIDATE_K,
    )

    fused = _fuse_results(
        lexical_results,
        semantic_results,
    )

    gated = _apply_semantic_gate(
        fused,
        threshold=SEMANTIC_THRESHOLD,
    )

    return _select_distinct_sources(
        gated,
        limit=limit,
    )
