from statistics import mean

from app.config import settings
from app.rag.evaluation import EVALUATION_CASES
from app.rag.ingest import load_chunks
from app.rag.openai_embeddings import embedding_service


EMBEDDING_MODEL = settings.embedding_model
LIMIT = 3


def cosine_similarity(vector_a, vector_b):
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    magnitude_a = sum(a * a for a in vector_a) ** 0.5
    magnitude_b = sum(b * b for b in vector_b) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def retrieve_raw(query_embedding, embedded_chunks, limit=LIMIT):
    scored = []

    for chunk in embedded_chunks:
        score = cosine_similarity(
            query_embedding,
            chunk["embedding"],
        )

        scored.append(
            {
                "source": chunk["source"],
                "chunk": chunk["chunk"],
                "content": chunk["content"],
                "score": score,
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


def diversify_results(results, limit=LIMIT):
    """
    Keep the highest-scoring chunk from each source.

    Results are assumed to already be sorted by semantic score.
    """
    diversified = []
    seen_sources = set()

    for result in results:
        source = result["source"]

        if source in seen_sources:
            continue

        diversified.append(result)
        seen_sources.add(source)

        if len(diversified) >= limit:
            break

    return diversified


def unique_sources(results):
    return list(
        dict.fromkeys(
            result["source"]
            for result in results
        )
    )


def hit_at_k(results, expected_sources):
    expected_sources = set(expected_sources)

    if not expected_sources:
        return len(results) == 0

    return bool(
        set(unique_sources(results)) & expected_sources
    )


def source_recall_at_k(results, expected_sources):
    expected_sources = set(expected_sources)

    if not expected_sources:
        return 0.0

    retrieved = set(unique_sources(results))

    return len(retrieved & expected_sources) / len(expected_sources)


def source_precision_at_k(results, expected_sources):
    expected_sources = set(expected_sources)
    retrieved = set(unique_sources(results))

    if not retrieved:
        return 0.0

    return len(retrieved & expected_sources) / len(retrieved)


def chunk_precision_at_k(results, expected_sources):
    expected_sources = set(expected_sources)

    if not results:
        return 0.0

    relevant = sum(
        result["source"] in expected_sources
        for result in results
    )

    return relevant / len(results)


def duplicate_rate(results):
    sources = [
        result["source"]
        for result in results
    ]

    if not sources:
        return 0.0

    return (
        len(sources) - len(set(sources))
    ) / len(sources)


def reciprocal_rank(results, expected_sources):
    expected_sources = set(expected_sources)

    if not expected_sources:
        return 0.0

    for rank, result in enumerate(results, start=1):
        if result["source"] in expected_sources:
            return 1.0 / rank

    return 0.0


def evaluate_results(results, expected_sources):
    return {
        "hit": hit_at_k(
            results,
            expected_sources,
        ),
        "source_recall": source_recall_at_k(
            results,
            expected_sources,
        ),
        "source_precision": source_precision_at_k(
            results,
            expected_sources,
        ),
        "chunk_precision": chunk_precision_at_k(
            results,
            expected_sources,
        ),
        "duplicate_rate": duplicate_rate(results),
        "reciprocal_rank": reciprocal_rank(
            results,
            expected_sources,
        ),
    }


def print_metrics(title, results):
    print(title)
    print("-" * len(title))

    print(
        f"Hit Rate@3:          "
        f"{mean(r['hit'] for r in results):.3f}"
    )

    print(
        f"Source Recall@3:     "
        f"{mean(r['source_recall'] for r in results):.3f}"
    )

    print(
        f"Source Precision@3:  "
        f"{mean(r['source_precision'] for r in results):.3f}"
    )

    print(
        f"Chunk Precision@3:   "
        f"{mean(r['chunk_precision'] for r in results):.3f}"
    )

    print(
        f"Duplicate Rate@3:    "
        f"{mean(r['duplicate_rate'] for r in results):.3f}"
    )

    print(
        f"MRR@3:               "
        f"{mean(r['reciprocal_rank'] for r in results):.3f}"
    )


def main():
    print("SEMANTIC SOURCE-DIVERSITY EXPERIMENT")
    print("=" * 70)
    print()
    print(f"Embedding model: {EMBEDDING_MODEL}")

    chunks = load_chunks()

    print(f"Chunks evaluated: {len(chunks)}")
    print()
    if not embedding_service.available:
        raise RuntimeError(
            "OpenAI embedding service is not configured. "
            "Check OPENAI_API_KEY in backend/.env."
        )

    print()
    print("Embedding knowledge base chunks...")

    embeddings = embedding_service.embed_documents(
        [chunk["content"] for chunk in chunks]
    )

    embedded_chunks = []

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings),
        start=1,
    ):
        print(
            f"  [{index}/{len(chunks)}] "
            f"{chunk['source']}:{chunk['chunk']}"
        )

        embedded_chunks.append(
            {
                **chunk,
                "embedding": embedding,
            }
        )

    raw_results = []
    diversified_results = []

    print()
    print("Evaluating queries...")
    print()

    for index, case in enumerate(
        EVALUATION_CASES,
        start=1,
    ):
        query = case["query"]
        expected_sources = set(
            case["expected_sources"]
        )

        print(
            f"[{index}/{len(EVALUATION_CASES)}] "
            f"{query}"
        )

        query_embedding = embedding_service.embed_query(
            query
        )

        raw = retrieve_raw(
            query_embedding,
            embedded_chunks,
            LIMIT,
        )

        diversified = diversify_results(
            raw,
            LIMIT,
        )

        raw_metrics = evaluate_results(
            raw,
            expected_sources,
        )

        diversified_metrics = evaluate_results(
            diversified,
            expected_sources,
        )

        raw_results.append(raw_metrics)
        diversified_results.append(
            diversified_metrics
        )

        print(
            f"  Raw:         "
            f"{[r['source'] for r in raw]}"
        )

        print(
            f"  Diversified: "
            f"{[r['source'] for r in diversified]}"
        )

        print()

    print("=" * 70)
    print("RAW SEMANTIC BASELINE")
    print("=" * 70)

    print_metrics(
        "Raw semantic retrieval",
        raw_results,
    )

    print()
    print("=" * 70)
    print("DIVERSIFIED SEMANTIC RESULTS")
    print("=" * 70)

    print_metrics(
        "Source-diversified retrieval",
        diversified_results,
    )

    print()
    print("=" * 70)
    print("METRIC DELTAS")
    print("=" * 70)

    metrics = [
        ("Hit Rate@3", "hit"),
        ("Source Recall@3", "source_recall"),
        ("Source Precision@3", "source_precision"),
        ("Chunk Precision@3", "chunk_precision"),
        ("Duplicate Rate@3", "duplicate_rate"),
        ("MRR@3", "reciprocal_rank"),
    ]

    for label, key in metrics:
        raw_value = mean(
            result[key]
            for result in raw_results
        )

        diversified_value = mean(
            result[key]
            for result in diversified_results
        )

        delta = diversified_value - raw_value

        print(
            f"{label:<22}"
            f"{raw_value:.3f} -> "
            f"{diversified_value:.3f} "
            f"(delta {delta:+.3f})"
        )


if __name__ == "__main__":
    main()
