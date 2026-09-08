from app.rag.context import build_context


def test_context_is_deterministic():
    query = "What technologies are used to build the frontend?"

    first = build_context(query)
    second = build_context(query)

    assert first == second


def test_empty_query_returns_empty_context():
    assert build_context("") == ""


def test_unknown_query_returns_empty_context():
    assert build_context(
        "What is the capital of France?"
    ) == ""


def test_context_respects_max_chars():
    context = build_context(
        "What technologies are used to build the frontend?",
        max_chars=100,
    )

    assert len(context) <= 100


def test_context_contains_source_metadata():
    context = build_context(
        "What tools are used for server-side development?"
    )

    assert "[Source: skills.md" in context


def test_context_contains_chunk_metadata():
    context = build_context(
        "What tools are used for server-side development?"
    )

    assert "Chunk:" in context


def test_context_contains_retrieved_content():
    context = build_context(
        "What tools are used for server-side development?"
    )

    assert "Python" in context
    assert "FastAPI" in context


def test_invalid_limit_returns_empty_context():
    assert build_context(
        "frontend",
        limit=0,
    ) == ""


def test_invalid_max_chars_returns_empty_context():
    assert build_context(
        "frontend",
        max_chars=0,
    ) == ""