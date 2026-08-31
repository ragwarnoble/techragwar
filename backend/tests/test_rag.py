from app.rag.ingest import load_markdown_documents
from app.rag.retriever import retrieve, tokenize


def test_tokenize_removes_stop_words():
    tokens = tokenize("What technologies does Ragwar Tech use?")

    assert "what" not in tokens
    assert "does" not in tokens
    assert "use" not in tokens
    assert "technologies" in tokens
    assert "ragwar" in tokens


def test_load_markdown_documents():
    documents = load_markdown_documents()

    assert documents
    assert all("source" in document for document in documents)
    assert all("content" in document for document in documents)


def test_retrieve_framework_freefe():
    results = retrieve("Tell me about Framework-FreeFE")

    assert results
    assert any(
        "framework-free" in result["content"].lower()
        for result in results
    )


def test_retrieve_ai_projects():
    results = retrieve("What AI projects are in the portfolio?")

    assert results
    assert any(
        "retrieval-augmented generation" in result["content"].lower()
        or "llm" in result["content"].lower()
        for result in results
    )


def test_retrieve_returns_empty_for_unknown_query():
    results = retrieve(
        "quantum submarine agricultural satellite"
    )

    assert results == []


def test_retrieve_limit():
    results = retrieve(
        "Ragwar Tech software engineering portfolio",
        limit=2,
    )

    assert len(results) <= 2


def test_retrieve_invalid_limit():
    assert retrieve("Python", limit=0) == []
    assert retrieve("Python", limit=-1) == []
