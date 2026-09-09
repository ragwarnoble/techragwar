"""
Automated RAG regression evaluation.

Runs the semantic retrieval evaluation against the established
quality thresholds and verifies that known out-of-scope queries
are rejected by the semantic relevance threshold.
"""

from .evaluation import (
    EVALUATION_CASES,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)
from .semantic_evaluation import (
    embed_text,
    retrieve_semantic,
)


LIMIT = 3

# Empirically selected from the semantic threshold experiment.
# This is a project-specific retrieval policy, not a universal value.
SEMANTIC_THRESHOLD = 0.60

REGRESSION_THRESHOLDS = {
    "hit_rate": 0.90,
    "recall": 0.80,
    "precision": 0.60,
    "mrr": 0.80,
    "duplicate_rate": 0.05,
}


def retrieve_for_evaluation(
    query: str,
    embedded_chunks: list[dict],
    client,
) -> list[dict]:
    """Retrieve semantic results for a regression query."""

    query_embedding = embed_text(client, query)

    return retrieve_semantic(
        query_embedding,
        embedded_chunks,
        limit=LIMIT,
    )


def hit_rate(
    results_by_case: list[tuple[dict, list[dict]]],
) -> float:
    """Calculate hit rate across evaluation cases."""

    if not results_by_case:
        return 0.0

    hits = 0

    for case, results in results_by_case:
        expected_sources = case["expected_sources"]

        if not expected_sources:
            continue

        retrieved_sources = {
            result["source"]
            for result in results
        }

        if retrieved_sources & expected_sources:
            hits += 1

    scored_cases = sum(
        1
        for case, _ in results_by_case
        if case["expected_sources"]
    )

    if scored_cases == 0:
        return 0.0

    return hits / scored_cases


def duplicate_rate(
    results_by_case: list[tuple[dict, list[dict]]],
) -> float:
    """Calculate duplicate chunk rate across result lists."""

    if not results_by_case:
        return 0.0

    total_results = 0
    duplicate_results = 0

    for _, results in results_by_case:
        seen_chunks = set()

        for result in results:
            key = (
                result["source"],
                result["chunk"],
            )

            total_results += 1

            if key in seen_chunks:
                duplicate_results += 1
            else:
                seen_chunks.add(key)

    if total_results == 0:
        return 0.0

    return duplicate_results / total_results


def evaluate_retrieval(
    embedded_chunks: list[dict],
    client,
) -> dict:
    """Run the complete semantic retrieval regression evaluation."""

    results_by_case = []

    for case in EVALUATION_CASES:
        results = retrieve_for_evaluation(
            case["query"],
            embedded_chunks,
            client,
        )

        results_by_case.append(
            (case, results)
        )

    scored_cases = [
        (case, results)
        for case, results in results_by_case
        if case["expected_sources"]
    ]

    recall_scores = []
    precision_scores = []
    reciprocal_ranks = []

    for case, results in scored_cases:
        expected_sources = case["expected_sources"]

        recall_scores.append(
            recall_at_k(
                results,
                expected_sources,
            )
        )

        precision_scores.append(
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

    metrics = {
        "hit_rate": hit_rate(results_by_case),
        "recall": (
            sum(recall_scores) / len(recall_scores)
            if recall_scores
            else 0.0
        ),
        "precision": (
            sum(precision_scores) / len(precision_scores)
            if precision_scores
            else 0.0
        ),
        "mrr": (
            sum(reciprocal_ranks) / len(reciprocal_ranks)
            if reciprocal_ranks
            else 0.0
        ),
        "duplicate_rate": duplicate_rate(results_by_case),
    }

    return metrics


def evaluate_oos(
    embedded_chunks: list[dict],
    client,
) -> bool:
    """
    Verify that known out-of-scope queries are rejected
    by the semantic relevance threshold.

    The raw semantic retriever always returns top-K candidates.
    Therefore, OOS rejection is evaluated after applying the
    project's semantic relevance threshold.
    """

    oos_queries = [
        "What is the weather today?",
        "Who is the president of the United States?",
    ]

    passed = True

    for query in oos_queries:
        results = retrieve_for_evaluation(
            query,
            embedded_chunks,
            client,
        )

        relevant_results = [
            result
            for result in results
            if result["score"] >= SEMANTIC_THRESHOLD
        ]

        if relevant_results:
            print(
                f"FAIL: OOS query exceeded relevance threshold: "
                f"{query}"
            )

            for result in relevant_results:
                print(
                    f"  {result['source']}:{result['chunk']} "
                    f"score={result['score']:.4f}"
                )

            passed = False
        else:
            print(
                f"PASS: Rejected OOS query: {query}"
            )

    return passed


def check_thresholds(metrics: dict) -> bool:
    """Check regression metrics against minimum quality thresholds."""

    passed = True

    print()
    print("REGRESSION THRESHOLDS")

    checks = [
        (
            "Hit Rate",
            metrics["hit_rate"],
            REGRESSION_THRESHOLDS["hit_rate"],
            ">=",
        ),
        (
            "Recall",
            metrics["recall"],
            REGRESSION_THRESHOLDS["recall"],
            ">=",
        ),
        (
            "Precision",
            metrics["precision"],
            REGRESSION_THRESHOLDS["precision"],
            ">=",
        ),
        (
            "MRR",
            metrics["mrr"],
            REGRESSION_THRESHOLDS["mrr"],
            ">=",
        ),
        (
            "Duplicate Rate",
            metrics["duplicate_rate"],
            REGRESSION_THRESHOLDS["duplicate_rate"],
            "<=",
        ),
    ]

    for name, actual, threshold, operator in checks:
        if operator == ">=":
            check_passed = actual >= threshold
        else:
            check_passed = actual <= threshold

        if check_passed:
            print(
                f"PASS: {name} "
                f"{actual:.3f} {operator} {threshold:.3f}"
            )
        else:
            print(
                f"FAIL: {name} "
                f"{actual:.3f} {operator} {threshold:.3f}"
            )
            passed = False

    return passed


def main() -> int:
    """Run the regression suite."""

    print("RAG REGRESSION EVALUATION")
    print("=" * 70)
    print()
    print(f"Embedding model: gemini-embedding-001")
    print(f"Evaluation cases: {len(EVALUATION_CASES)}")
    print(f"Top-K: {LIMIT}")
    print(f"Semantic threshold: {SEMANTIC_THRESHOLD:.2f}")
    print()

    print("Initializing Gemini client...")

    try:
        from google import genai
        from app.config import settings

        client = genai.Client(
            api_key=settings.google_api_key
        )

    except Exception as exc:
        print(f"ERROR: Failed to initialize Gemini client: {exc}")
        return 1

    print("Building embeddings...")

    try:
        from .hybrid_retriever import build_embedded_chunks

        embedded_chunks = build_embedded_chunks(client)

    except Exception as exc:
        print(f"ERROR: Failed to build embeddings: {exc}")
        return 1

    print(
        f"Embedded chunks: {len(embedded_chunks)}"
    )

    print()
    print("Running retrieval evaluation...")

    try:
        metrics = evaluate_retrieval(
            embedded_chunks,
            client,
        )

    except Exception as exc:
        print(
            f"ERROR: Retrieval evaluation failed: {exc}"
        )
        return 1

    print()
    print("METRICS")
    print("-" * 70)

    print(
        f"Hit Rate@{LIMIT}:       "
        f"{metrics['hit_rate']:.3f}"
    )

    print(
        f"Recall@{LIMIT}:         "
        f"{metrics['recall']:.3f}"
    )

    print(
        f"Precision@{LIMIT}:      "
        f"{metrics['precision']:.3f}"
    )

    print(
        f"MRR@{LIMIT}:            "
        f"{metrics['mrr']:.3f}"
    )

    print(
        f"Duplicate Rate@{LIMIT}: "
        f"{metrics['duplicate_rate']:.3f}"
    )

    thresholds_passed = check_thresholds(metrics)

    print()
    print("OUT-OF-SCOPE REJECTION")

    try:
        oos_passed = evaluate_oos(
            embedded_chunks,
            client,
        )

    except Exception as exc:
        print(
            f"ERROR: OOS evaluation failed: {exc}"
        )
        return 1

    regression_passed = (
        thresholds_passed
        and oos_passed
    )

    print()
    print(
        "REGRESSION RESULT: "
        f"{'PASS' if regression_passed else 'FAIL'}"
    )

    return 0 if regression_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())