"""Compare lexical and semantic RAG retrieval."""

from .evaluation import (
    EVALUATION_CASES,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)
from .retriever import retrieve
from .semantic_retriever import (
    build_index,
    retrieve_semantic,
)


SEMANTIC_THRESHOLD = 0.60
TOP_K = 3


def build_embedded_chunks() -> list[dict]:
    """Build the semantic knowledge-base index once."""
    print("\nEmbedding knowledge base chunks...")

    embedded_chunks = build_index()

    for index, chunk in enumerate(
        embedded_chunks,
        start=1,
    ):
        print(
            f"  [{index}/{len(embedded_chunks)}] "
            f"{chunk['source']}:{chunk['chunk']}"
        )

    return embedded_chunks


def semantic_results(
    query: str,
    embedded_chunks: list[dict],
) -> list[dict]:
    """Perform semantic retrieval for a query."""

    return retrieve_semantic(
        query,
        embedded_chunks,
        limit=TOP_K,
    )


def apply_threshold(
    results: list[dict],
    threshold: float,
) -> list[dict]:
    """Keep only results meeting the semantic relevance threshold."""

    return [
        result
        for result in results
        if result["score"] >= threshold
    ]


def metrics_for_case(
    results: list[dict],
    expected_sources: set[str],
) -> dict:
    """Calculate metrics for one evaluation case."""

    if expected_sources:
        hit = any(
            result["source"] in expected_sources
            for result in results
        )
    else:
        hit = not results

    return {
        "hit": hit,
        "recall": recall_at_k(
            results,
            expected_sources,
        ),
        "precision": precision_at_k(
            results,
            expected_sources,
        ),
        "mrr": reciprocal_rank(
            results,
            expected_sources,
        ),
    }


def evaluate_lexical() -> dict:
    """Evaluate the existing lexical retriever."""

    cases = []

    for case in EVALUATION_CASES:
        results = retrieve(
            case["query"],
            limit=TOP_K,
        )

        metrics = metrics_for_case(
            results,
            case["expected_sources"],
        )

        cases.append(
            {
                "query": case["query"],
                "expected": case["expected_sources"],
                "results": results,
                **metrics,
            }
        )

    return {
        "name": "lexical",
        "cases": cases,
    }


def evaluate_semantic(
    embedded_chunks: list[dict],
) -> dict:
    """Evaluate semantic retrieval with relevance threshold."""

    cases = []

    for case in EVALUATION_CASES:
        results = semantic_results(
            case["query"],
            embedded_chunks,
        )

        results = apply_threshold(
            results,
            SEMANTIC_THRESHOLD,
        )

        metrics = metrics_for_case(
            results,
            case["expected_sources"],
        )

        cases.append(
            {
                "query": case["query"],
                "expected": case["expected_sources"],
                "results": results,
                **metrics,
            }
        )

    return {
        "name": "semantic",
        "cases": cases,
    }


def aggregate(evaluation: dict) -> dict:
    """Aggregate metrics across evaluation cases."""

    cases = evaluation["cases"]

    if not cases:
        return {
            "hit_rate": 0.0,
            "recall": 0.0,
            "precision": 0.0,
            "mrr": 0.0,
        }

    return {
        "hit_rate": sum(
            case["hit"]
            for case in cases
        ) / len(cases),
        "recall": sum(
            case["recall"]
            for case in cases
        ) / len(cases),
        "precision": sum(
            case["precision"]
            for case in cases
        ) / len(cases),
        "mrr": sum(
            case["mrr"]
            for case in cases
        ) / len(cases),
    }


def print_summary(evaluation: dict) -> None:
    """Print aggregate retrieval metrics."""

    metrics = aggregate(evaluation)

    print(
        f"\n{evaluation['name'].upper()} RETRIEVAL"
    )
    print("-" * 40)

    print(
        f"Hit Rate@3:       "
        f"{metrics['hit_rate']:.3f}"
    )

    print(
        f"Recall@3:         "
        f"{metrics['recall']:.3f}"
    )

    print(
        f"Precision@3:      "
        f"{metrics['precision']:.3f}"
    )

    print(
        f"MRR@3:            "
        f"{metrics['mrr']:.3f}"
    )


def print_query_comparison(
    lexical: dict,
    semantic: dict,
) -> None:
    """Print cases where lexical and semantic disagree."""

    print("\n" + "=" * 70)
    print("QUERY-LEVEL COMPARISON")
    print("=" * 70)

    for lexical_case, semantic_case in zip(
        lexical["cases"],
        semantic["cases"],
    ):
        if lexical_case["hit"] == semantic_case["hit"]:
            continue

        query = lexical_case["query"]

        print(f"\nQuery: {query}")

        print(
            "  Lexical:  "
            + (
                "HIT"
                if lexical_case["hit"]
                else "MISS"
            )
        )

        print(
            "  Semantic: "
            + (
                "HIT"
                if semantic_case["hit"]
                else "MISS"
            )
        )

        print("  Lexical sources:")

        for result in lexical_case["results"]:
            print(
                f"    {result['source']}:"
                f"{result['chunk']}"
            )

        print("  Semantic sources:")

        for result in semantic_case["results"]:
            print(
                f"    {result['source']}:"
                f"{result['chunk']}"
                f" score={result['score']:.4f}"
            )


def print_oos_analysis(
    lexical: dict,
    semantic: dict,
) -> None:
    """Compare out-of-scope rejection behavior."""

    print("\n" + "=" * 70)
    print("OUT-OF-SCOPE COMPARISON")
    print("=" * 70)

    for lexical_case, semantic_case in zip(
        lexical["cases"],
        semantic["cases"],
    ):
        if lexical_case["expected"]:
            continue

        print(
            f"\n{lexical_case['query']}"
        )

        print(
            "  Lexical:  "
            + (
                "REJECTED"
                if not lexical_case["results"]
                else "ACCEPTED"
            )
        )

        print(
            "  Semantic: "
            + (
                "REJECTED"
                if not semantic_case["results"]
                else "ACCEPTED"
            )
        )

        if semantic_case["results"]:
            for result in semantic_case["results"]:
                print(
                    f"    {result['source']}:"
                    f"{result['chunk']}"
                    f" score={result['score']:.4f}"
                )


def main() -> None:
    """Run the lexical-versus-semantic comparison."""

    print("LEXICAL VS SEMANTIC RETRIEVAL")
    print("=" * 70)

    print(f"Top K: {TOP_K}")
    print(
        f"Semantic threshold: "
        f"{SEMANTIC_THRESHOLD:.2f}"
    )

    embedded_chunks = build_embedded_chunks()

    print("\nEvaluating lexical retrieval...")
    lexical = evaluate_lexical()

    print("\nEvaluating semantic retrieval...")
    semantic = evaluate_semantic(
        embedded_chunks,
    )

    print_summary(lexical)
    print_summary(semantic)

    print_query_comparison(
        lexical,
        semantic,
    )

    print_oos_analysis(
        lexical,
        semantic,
    )


if __name__ == "__main__":
    main()