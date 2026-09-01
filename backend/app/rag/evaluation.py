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