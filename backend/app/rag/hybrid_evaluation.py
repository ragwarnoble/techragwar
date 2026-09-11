from .evaluation import (
    EVALUATION_CASES,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)
from .hybrid_retriever import (
    build_embedded_chunks,
    retrieve_hybrid,
)
from .retriever import retrieve
from .semantic_retriever import retrieve_semantic

LIMIT = 3


def chunk_id(result: dict) -> tuple[str, int]:
    return (
        result["source"],
        result["chunk"],
    )


def duplicate_rate(results: list[dict]) -> float:
    """
    Measure duplicate chunk rate.

    Returns the proportion of results that duplicate
    another chunk in the same result set.
    """

    if not results:
        return 0.0

    unique = len({chunk_id(result) for result in results})

    return 1.0 - (unique / len(results))


def evaluate_retriever(
    retriever_name: str,
    retrieval_function,
    evaluation_cases: list[dict],
) -> dict:
    """Evaluate a retriever against the common evaluation set."""

    hits = []
    recalls = []
    precisions = []
    reciprocal_ranks = []
    duplicate_rates = []

    for case in evaluation_cases:
        results = retrieval_function(case["query"])

        expected_sources = case["expected_sources"]

        # For normal in-scope queries, a hit means
        # at least one expected source was retrieved.
        #
        # For OOS queries, an empty result is the
        # correct behavior and is not counted as a hit.
        if expected_sources:
            hits.append(any(result["source"] in expected_sources for result in results))
        else:
            hits.append(False)

        recalls.append(
            recall_at_k(
                results,
                expected_sources,
            )
        )

        precisions.append(
            precision_at_k(
                results,
                expected_sources,
            )
        )

        reciprocal_ranks.append(
            reciprocal_rank(
                results,
                expected_sources,
            )
        )

        duplicate_rates.append(duplicate_rate(results))

    return {
        "name": retriever_name,
        "hit_rate": (sum(hits) / len(hits) if hits else 0.0),
        "recall": (sum(recalls) / len(recalls) if recalls else 0.0),
        "precision": (sum(precisions) / len(precisions) if precisions else 0.0),
        "mrr": (
            sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
        ),
        "duplicate_rate": (
            sum(duplicate_rates) / len(duplicate_rates) if duplicate_rates else 0.0
        ),
    }


def print_metrics(metrics: dict) -> None:
    """Print metrics for one retriever."""

    print(f"\n{metrics['name'].upper()} RETRIEVAL")
    print("-" * 40)

    print(f"Hit Rate@{LIMIT}:       {metrics['hit_rate']:.3f}")

    print(f"Recall@{LIMIT}:         {metrics['recall']:.3f}")

    print(f"Precision@{LIMIT}:      {metrics['precision']:.3f}")

    print(f"MRR@{LIMIT}:            {metrics['mrr']:.3f}")

    print(f"Duplicate Rate@{LIMIT}: {metrics['duplicate_rate']:.3f}")


def main() -> None:

    print("HYBRID RETRIEVAL EVALUATION")
    print("=" * 70)
    print(f"Top K: {LIMIT}")

    from .hybrid_retriever import (
        LEXICAL_WEIGHT,
        SEMANTIC_THRESHOLD,
        SEMANTIC_WEIGHT,
    )

    print(f"Semantic threshold: {SEMANTIC_THRESHOLD:.2f}")

    print(f"Lexical weight: {LEXICAL_WEIGHT:.2f}")

    print(f"Semantic weight: {SEMANTIC_WEIGHT:.2f}")

    print("\nBuilding semantic knowledge-base index...")

    embedded_chunks = build_embedded_chunks()

    print(f"  Embedded {len(embedded_chunks)} chunks")

    # ------------------------------------------------------------
    # Lexical retrieval
    # ------------------------------------------------------------

    print("\nEvaluating lexical retrieval...")

    lexical_metrics = evaluate_retriever(
        "Lexical",
        lambda query: retrieve(
            query,
            limit=LIMIT,
        ),
        EVALUATION_CASES,
    )

    # ------------------------------------------------------------
    # Semantic retrieval
    # ------------------------------------------------------------

    print("Evaluating semantic retrieval...")

    def semantic_retrieve(
        query: str,
    ) -> list[dict]:

        return retrieve_semantic(
            query,
            embedded_chunks,
            limit=LIMIT,
        )

    semantic_metrics = evaluate_retriever(
        "Semantic",
        semantic_retrieve,
        EVALUATION_CASES,
    )

    # ------------------------------------------------------------
    # Hybrid retrieval
    # ------------------------------------------------------------

    print("Evaluating hybrid retrieval...")

    def hybrid_retrieve(
        query: str,
    ) -> list[dict]:

        return retrieve_hybrid(
            query,
            embedded_chunks,
            limit=LIMIT,
        )

    hybrid_metrics = evaluate_retriever(
        "Hybrid",
        hybrid_retrieve,
        EVALUATION_CASES,
    )

    # ------------------------------------------------------------
    # Individual metrics
    # ------------------------------------------------------------

    print_metrics(lexical_metrics)

    print_metrics(semantic_metrics)

    print_metrics(hybrid_metrics)

    # ------------------------------------------------------------
    # Side-by-side comparison
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("RETRIEVAL COMPARISON")
    print("=" * 70)

    print(f"\n{'Metric':<24}{'Lexical':>12}{'Semantic':>12}{'Hybrid':>12}")

    print("-" * 60)

    rows = [
        (
            "Hit Rate@3",
            lexical_metrics["hit_rate"],
            semantic_metrics["hit_rate"],
            hybrid_metrics["hit_rate"],
        ),
        (
            "Recall@3",
            lexical_metrics["recall"],
            semantic_metrics["recall"],
            hybrid_metrics["recall"],
        ),
        (
            "Precision@3",
            lexical_metrics["precision"],
            semantic_metrics["precision"],
            hybrid_metrics["precision"],
        ),
        (
            "MRR@3",
            lexical_metrics["mrr"],
            semantic_metrics["mrr"],
            hybrid_metrics["mrr"],
        ),
        (
            "Duplicate Rate@3",
            lexical_metrics["duplicate_rate"],
            semantic_metrics["duplicate_rate"],
            hybrid_metrics["duplicate_rate"],
        ),
    ]

    for (
        name,
        lexical,
        semantic,
        hybrid,
    ) in rows:
        print(f"{name:<24}{lexical:>12.3f}{semantic:>12.3f}{hybrid:>12.3f}")

    # ------------------------------------------------------------
    # Query-level comparison
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("HYBRID QUERY RESULTS")
    print("=" * 70)

    for case in EVALUATION_CASES:
        query = case["query"]
        expected_sources = case["expected_sources"]

        results = hybrid_retrieve(query)

        print(f"\nQuery: {query}")

        # Normal in-scope query.
        if expected_sources:
            hit = any(result["source"] in expected_sources for result in results)

            print("  Hybrid: " + ("HIT" if hit else "MISS"))

        # Out-of-scope query.
        else:
            if results:
                print("  Hybrid: FALSE POSITIVE")
            else:
                print("  Hybrid: CORRECT REJECTION")

        if not results:
            print("  Results: REJECTED")
            continue

        for result in results:
            lexical_rank = result.get("lexical_rank")

            semantic_rank = result.get("semantic_rank")

            lexical_rank_text = str(lexical_rank) if lexical_rank is not None else "-"

            semantic_rank_text = (
                str(semantic_rank) if semantic_rank is not None else "-"
            )

            print(
                f"  {result['source']}:"
                f"{result['chunk']} "
                f"lexical={result['lexical_score']} "
                f"semantic="
                f"{result['semantic_score']:.4f} "
                f"hybrid="
                f"{result['hybrid_score']:.6f} "
                f"lex_rank="
                f"{lexical_rank_text} "
                f"sem_rank="
                f"{semantic_rank_text}"
            )

    # ------------------------------------------------------------
    # Explicit OOS evaluation
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("OUT-OF-SCOPE HYBRID CHECK")
    print("=" * 70)

    oos_queries = [
        "What is the weather today?",
        "Who is the president of the United States?",
    ]

    for query in oos_queries:
        results = hybrid_retrieve(query)

        status = "FALSE POSITIVE" if results else "REJECTED"

        print(f"\n{query}")

        print(f"  Hybrid: {status}")

        if not results:
            continue

        for result in results:
            print(
                f"    {result['source']}:"
                f"{result['chunk']} "
                f"semantic="
                f"{result['semantic_score']:.4f} "
                f"hybrid="
                f"{result['hybrid_score']:.6f}"
            )


if __name__ == "__main__":
    main()
