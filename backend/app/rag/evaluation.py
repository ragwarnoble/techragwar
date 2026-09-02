from .retriever import retrieve


EVALUATION_CASES = [
    {
        "query": "What tools are used for server-side development?",
        "expected_sources": {"about.md", "skills.md"},
    },
    {
        "query": "What technologies are used to build the frontend?",
        "expected_sources": {"skills.md", "about.md"},
    },
    {
        "query": "How does the AI system obtain information?",
        "expected_sources": {"architecture.md", "projects.md"},
    },
    {
        "query": "What kind of software architecture does Ragwar Tech prefer?",
        "expected_sources": {"architecture.md", "skills.md"},
    },
]


def evaluate_case(
    query: str,
    expected_sources: set[str],
    limit: int = 3,
) -> dict:
    results = retrieve(query, limit=limit)

    retrieved_sources = [
        result["source"]
        for result in results
    ]

    relevant = [
        source
        for source in retrieved_sources
        if source in expected_sources
    ]

    return {
        "query": query,
        "expected_sources": expected_sources,
        "retrieved_sources": retrieved_sources,
        "relevant_count": len(relevant),
        "hit": bool(relevant),
    }


def evaluate(
    cases: list[dict] | None = None,
    limit: int = 3,
) -> list[dict]:
    if cases is None:
        cases = EVALUATION_CASES

    return [
        evaluate_case(
            query=case["query"],
            expected_sources=case["expected_sources"],
            limit=limit,
        )
        for case in cases
    ]


def recall_at_k(
    results: list[dict],
    expected_sources: set[str],
) -> float:
    if not expected_sources:
        return 0.0

    retrieved = {
        result["source"]
        for result in results
    }

    return len(
        retrieved & expected_sources
    ) / len(expected_sources)


def reciprocal_rank(
    results: list[dict],
    expected_sources: set[str],
) -> float:
    for position, result in enumerate(results, start=1):
        if result["source"] in expected_sources:
            return 1.0 / position

    return 0.0


def mean_reciprocal_rank(
    cases: list[dict] | None = None,
    limit: int = 3,
) -> float:
    if cases is None:
        cases = EVALUATION_CASES

    if not cases:
        return 0.0

    scores = []

    for case in cases:
        results = retrieve(
            case["query"],
            limit=limit,
        )

        scores.append(
            reciprocal_rank(
                results,
                case["expected_sources"],
            )
        )

    return sum(scores) / len(scores)

def precision_at_k(
    results: list[dict],
    expected_sources: set[str],
) -> float:
    if not results:
        return 0.0

    relevant = sum(
        1
        for result in results
        if result["source"] in expected_sources
    )

    return relevant / len(results)


def unique_source_count(results: list[dict]) -> int:
    return len({
        result["source"]
        for result in results
    })


def duplicate_source_count(results: list[dict]) -> int:
    return len(results) - unique_source_count(results)

if __name__ == "__main__":
    results = evaluate()

    print("RAG RETRIEVAL EVALUATION")
    print("=" * 60)

    reciprocal_ranks = []

    for result in results:
        query = result["query"]
        expected = result["expected_sources"]

        retrieved = retrieve(query, limit=3)

        recall = recall_at_k(
            retrieved,
            expected,
        )

        precision = precision_at_k(
            retrieved,
            expected,
        )

        rr = reciprocal_rank(
            retrieved,
            expected,
        )

        reciprocal_ranks.append(rr)

        print(f"\nQUESTION: {query}")
        print(f"Expected:  {sorted(expected)}")
        print(f"Retrieved: {[r['source'] for r in retrieved]}")
        print(f"Recall@3:  {recall:.3f}")
        print(f"Precision@3: {precision:.3f}")
        print(f"RR:        {rr:.3f}")

    hit_rate = (
        sum(result["hit"] for result in results) / len(results)
        if results
        else 0.0
    )

    mrr = (
        sum(reciprocal_ranks) / len(reciprocal_ranks)
        if reciprocal_ranks
        else 0.0
    )

    print("\n" + "=" * 60)
    print(f"Cases:       {len(results)}")
    print(f"Hit Rate:    {hit_rate:.3f}")
    print(f"MRR:         {mrr:.3f}")
    print(f"Unique sources: " f"{unique_source_count(retrieved)}")
    print(f"Duplicate sources: " f"{duplicate_source_count(retrieved)}")