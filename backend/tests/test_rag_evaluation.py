from app.rag.evaluation import (
    EVALUATION_CASES,
    evaluate,
    evaluate_case,
    recall_at_k,
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
    assert "retrieved_sources" in result
    assert "hit" in result
    assert "relevant_count" in result


def test_evaluate_all_cases():
    results = evaluate()

    assert len(results) == len(EVALUATION_CASES)

    for result in results:
        assert result["query"]
        assert isinstance(
            result["retrieved_sources"],
            list,
        )


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
