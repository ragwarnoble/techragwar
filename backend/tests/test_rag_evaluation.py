from app.rag.retriever import retrieve


EVALUATION_CASES = [
    {
        "question": "What technologies does Ragwar Tech use?",
        "expected_sources": {"about.md", "skills.md"},
    },
    {
        "question": "How does the portfolio AI/RAG system work?",
        "expected_sources": {"projects.md", "architecture.md"},
    },
    {
        "question": "What is Framework-FreeFE?",
        "expected_sources": {"about.md", "projects.md"},
    },
    {
        "question": "What are the engineering goals?",
        "expected_sources": {"about.md", "skills.md"},
    },
]


def test_rag_evaluation_cases():
    for case in EVALUATION_CASES:
        results = retrieve(case["question"])

        assert results, case["question"]

        sources = {
            result["source"]
            for result in results
        }

        assert sources & case["expected_sources"], (
            f"No expected source retrieved for: "
            f"{case['question']}"
        )


def test_rag_unknown_question_has_no_results():
    results = retrieve(
        "What is the capital of France?"
    )

    assert results == []
