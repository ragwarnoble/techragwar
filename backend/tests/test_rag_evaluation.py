from app.rag.evaluation import (
    EVALUATION_CASES,
    duplicate_chunk_count,
    duplicate_source_count,
    evaluate,
    evaluate_case,
    mean_reciprocal_rank,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    unique_chunk_count,
    unique_source_count,
)
from app.rag.retriever import retrieve


def test_evaluation_cases_exist():
    assert EVALUATION_CASES


def test_evaluate_case_returns_expected_structure():
    case = EVALUATION_CASES[0]

    result = evaluate_case(
        case["query"],
        case["expected_sources"],
    )

    assert result["query"] == case["query"]
    assert result["expected_sources"] == case["expected_sources"]
    assert "retrieved_sources" in result
    assert "relevant_count" in result
    assert "hit" in result


def test_evaluate_all_cases():
    results = evaluate()

    assert len(results) == len(EVALUATION_CASES)

    for result in results:
        assert result["query"]
        assert isinstance(
            result["retrieved_sources"],
            list,
        )
        assert isinstance(
            result["relevant_count"],
            int,
        )
        assert isinstance(
            result["hit"],
            bool,
        )


def test_evaluate_empty_cases():
    assert evaluate([]) == []


def test_evaluate_case_with_no_results(monkeypatch):
    monkeypatch.setattr(
        "app.rag.evaluation.retrieve",
        lambda query, limit=3: [],
    )

    result = evaluate_case(
        "unknown question",
        {"missing.md"},
    )

    assert result["retrieved_sources"] == []
    assert result["relevant_count"] == 0
    assert result["hit"] is False


def test_recall_at_k():
    results = retrieve(
        "How does the portfolio AI/RAG system work?"
    )

    score = recall_at_k(
        results,
        {"projects.md", "architecture.md"},
    )

    assert 0.0 <= score <= 1.0


def test_recall_at_k_empty_expected_sources():
    assert recall_at_k([], set()) == 0.0


def test_recall_at_k_partial_recall():
    results = [
        {"source": "projects.md"},
        {"source": "other.md"},
    ]

    assert recall_at_k(
        results,
        {"projects.md", "architecture.md"},
    ) == 0.5


def test_recall_at_k_full_recall():
    results = [
        {"source": "projects.md"},
        {"source": "architecture.md"},
    ]

    assert recall_at_k(
        results,
        {"projects.md", "architecture.md"},
    ) == 1.0


def test_precision_at_k_empty_results():
    assert precision_at_k([], {"projects.md"}) == 0.0


def test_precision_at_k():
    results = [
        {"source": "projects.md"},
        {"source": "other.md"},
        {"source": "architecture.md"},
    ]

    assert precision_at_k(
        results,
        {"projects.md", "architecture.md"},
    ) == 2 / 3


def test_precision_at_k_all_relevant():
    results = [
        {"source": "projects.md"},
        {"source": "architecture.md"},
    ]

    assert precision_at_k(
        results,
        {"projects.md", "architecture.md"},
    ) == 1.0


def test_reciprocal_rank_first_result():
    results = [
        {"source": "projects.md"},
        {"source": "other.md"},
    ]

    assert reciprocal_rank(
        results,
        {"projects.md"},
    ) == 1.0


def test_reciprocal_rank_second_result():
    results = [
        {"source": "other.md"},
        {"source": "projects.md"},
    ]

    assert reciprocal_rank(
        results,
        {"projects.md"},
    ) == 0.5


def test_reciprocal_rank_no_relevant_result():
    results = [
        {"source": "other.md"},
        {"source": "another.md"},
    ]

    assert reciprocal_rank(
        results,
        {"projects.md"},
    ) == 0.0


def test_mean_reciprocal_rank_empty_cases():
    assert mean_reciprocal_rank([]) == 0.0


def test_mean_reciprocal_rank(monkeypatch):
    monkeypatch.setattr(
        "app.rag.evaluation.retrieve",
        lambda query, limit=3: [
            {"source": "projects.md"},
            {"source": "other.md"},
        ],
    )

    cases = [
        {
            "query": "question one",
            "expected_sources": {"projects.md"},
        },
        {
            "query": "question two",
            "expected_sources": {"projects.md"},
        },
    ]

    assert mean_reciprocal_rank(cases) == 1.0


def test_mean_reciprocal_rank_second_position(monkeypatch):
    monkeypatch.setattr(
        "app.rag.evaluation.retrieve",
        lambda query, limit=3: [
            {"source": "other.md"},
            {"source": "projects.md"},
        ],
    )

    cases = [
        {
            "query": "question",
            "expected_sources": {"projects.md"},
        },
    ]

    assert mean_reciprocal_rank(cases) == 0.5


def test_unique_source_count():
    results = [
        {"source": "about.md"},
        {"source": "about.md"},
        {"source": "architecture.md"},
    ]

    assert unique_source_count(results) == 2


def test_unique_source_count_empty():
    assert unique_source_count([]) == 0


def test_duplicate_source_count():
    results = [
        {"source": "about.md"},
        {"source": "about.md"},
        {"source": "architecture.md"},
    ]

    assert duplicate_source_count(results) == 1


def test_duplicate_source_count_without_duplicates():
    results = [
        {"source": "about.md"},
        {"source": "architecture.md"},
    ]

    assert duplicate_source_count(results) == 0


def test_unique_chunk_count():
    results = [
        {"source": "about.md", "chunk": 0},
        {"source": "about.md", "chunk": 0},
        {"source": "about.md", "chunk": 1},
    ]

    assert unique_chunk_count(results) == 2


def test_duplicate_chunk_count():
    results = [
        {"source": "about.md", "chunk": 0},
        {"source": "about.md", "chunk": 0},
        {"source": "about.md", "chunk": 1},
    ]

    assert duplicate_chunk_count(results) == 1


def test_unique_chunk_count_distinguishes_sources():
    results = [
        {"source": "about.md", "chunk": 0},
        {"source": "projects.md", "chunk": 0},
    ]

    assert unique_chunk_count(results) == 2


def test_duplicate_chunk_count_without_duplicates():
    results = [
        {"source": "about.md", "chunk": 0},
        {"source": "about.md", "chunk": 1},
    ]

    assert duplicate_chunk_count(results) == 0

