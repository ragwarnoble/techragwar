from statistics import mean

from app.config import settings
from app.rag.evaluation import EVALUATION_CASES
from app.rag.ingest import load_chunks
from app.rag.openai_embeddings import embedding_service


EMBEDDING_MODEL = settings.embedding_model
LIMIT = 3

THRESHOLDS = [
    0.50,
    0.55,
    0.58,
    0.60,
    0.62,
    0.65,
    0.70,
]



def cosine_similarity(vector_a, vector_b):
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = sum(
        a * a
        for a in vector_a
    ) ** 0.5

    magnitude_b = sum(
        b * b
        for b in vector_b
    ) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


def retrieve_semantic(
    query_embedding,
    embedded_chunks,
    limit=LIMIT,
):
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


def apply_threshold(
    results,
    threshold,
):
    return [
        result
        for result in results
        if result["score"] >= threshold
    ]


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
        set(unique_sources(results))
        & expected_sources
    )


def source_recall_at_k(
    results,
    expected_sources,
):
    expected_sources = set(expected_sources)

    if not expected_sources:
        return 0.0

    retrieved = set(
        unique_sources(results)
    )

    return len(
        retrieved & expected_sources
    ) / len(expected_sources)


def source_precision_at_k(
    results,
    expected_sources,
):
    expected_sources = set(expected_sources)
    retrieved = set(
        unique_sources(results)
    )

    if not retrieved:
        return 0.0

    return len(
        retrieved & expected_sources
    ) / len(retrieved)


def chunk_precision_at_k(
    results,
    expected_sources,
):
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
        len(sources)
        - len(set(sources))
    ) / len(sources)


def reciprocal_rank(
    results,
    expected_sources,
):
    expected_sources = set(expected_sources)

    if not expected_sources:
        return 0.0

    for rank, result in enumerate(
        results,
        start=1,
    ):
        if result["source"] in expected_sources:
            return 1.0 / rank

    return 0.0


def evaluate(
    results,
    expected_sources,
):
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
        "duplicate_rate": duplicate_rate(
            results
        ),
        "mrr": reciprocal_rank(
            results,
            expected_sources,
        ),
    }


def main():
    print(
        "SEMANTIC RELEVANCE THRESHOLD EXPERIMENT"
    )
    print("=" * 70)
    print()

    print(
        f"Embedding model: {EMBEDDING_MODEL}"
    )

    chunks = load_chunks()

    print(
        f"Chunks evaluated: {len(chunks)}"
    )

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

    print()
    print("Embedding evaluation queries...")

    query_embeddings = embedding_service.embed_documents(
        [case["query"] for case in EVALUATION_CASES]
    )

    for index, case in enumerate(
        EVALUATION_CASES,
        start=1,
    ):
        print(
            f"  [{index}/{len(EVALUATION_CASES)}] "
            f"{case['query']}"
        )

    print()
    print("=" * 70)
    print("THRESHOLD RESULTS")
    print("=" * 70)

    for threshold in THRESHOLDS:
        evaluations = []

        for case, query_embedding in zip(
            EVALUATION_CASES,
            query_embeddings,
        ):
            raw_results = retrieve_semantic(
                query_embedding,
                embedded_chunks,
                LIMIT,
            )

            filtered_results = apply_threshold(
                raw_results,
                threshold,
            )

            metrics = evaluate(
                filtered_results,
                case["expected_sources"],
            )

            evaluations.append(metrics)

        hit_rate = mean(
            result["hit"]
            for result in evaluations
        )

        source_recall = mean(
            result["source_recall"]
            for result in evaluations
        )

        source_precision = mean(
            result["source_precision"]
            for result in evaluations
        )

        chunk_precision = mean(
            result["chunk_precision"]
            for result in evaluations
        )

        duplicate_rate = mean(
            result["duplicate_rate"]
            for result in evaluations
        )

        mrr = mean(
            result["mrr"]
            for result in evaluations
        )

        print()
        print(
            f"Threshold >= {threshold:.2f}"
        )
        print("-" * 40)

        print(
            f"Hit Rate@3:          {hit_rate:.3f}"
        )

        print(
            f"Source Recall@3:     {source_recall:.3f}"
        )

        print(
            f"Source Precision@3:  {source_precision:.3f}"
        )

        print(
            f"Chunk Precision@3:   {chunk_precision:.3f}"
        )

        print(
            f"Duplicate Rate@3:    {duplicate_rate:.3f}"
        )

        print(
            f"MRR@3:               {mrr:.3f}"
        )

    print()
    print("=" * 70)
    print("OUT-OF-SCOPE THRESHOLD ANALYSIS")
    print("=" * 70)

    out_of_scope_queries = {
        "What is the weather today?",
        "Who is the president of the United States?",
    }

    for threshold in THRESHOLDS:
        print()
        print(
            f"Threshold >= {threshold:.2f}"
        )

        for case, query_embedding in zip(
            EVALUATION_CASES,
            query_embeddings,
        ):
            if case["query"] not in out_of_scope_queries:
                continue

            raw_results = retrieve_semantic(
                query_embedding,
                embedded_chunks,
                LIMIT,
            )

            filtered_results = apply_threshold(
                raw_results,
                threshold,
            )

            print(
                f"  {case['query']}"
            )

            if not filtered_results:
                print(
                    "    Result: REJECTED"
                )
            else:
                print(
                    "    Result: ACCEPTED"
                )

                for result in filtered_results:
                    print(
                        f"      "
                        f"{result['source']}:{result['chunk']} "
                        f"score={result['score']:.4f}"
                    )


if __name__ == "__main__":
    main()
