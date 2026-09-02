from app.rag.ingest import (
    chunk_document,
    load_chunks,
    load_markdown_documents,
)
from app.rag.retriever import retrieve, tokenize


def test_tokenize_removes_stop_words():
    tokens = tokenize("What does Ragwar Tech use for backend development?")

    assert "what" not in tokens
    assert "does" not in tokens
    assert "use" not in tokens
    assert "ragwar" not in tokens
    assert "tech" not in tokens


def test_load_markdown_documents():
    documents = load_markdown_documents()

    assert documents

    for document in documents:
        assert document["source"].endswith(".md")
        assert document["content"]


def test_retrieve_framework_freefe():
    results = retrieve("Framework-FreeFE")

    assert results
    assert any(
        "Framework-FreeFE" in result["content"]
        for result in results
    )


def test_retrieve_ai_projects():
    results = retrieve("AI Projects")

    assert results
    assert any(
        "AI" in result["content"]
        for result in results
    )


def test_retrieve_returns_empty_for_unknown_query():
    assert retrieve("quantum bananas spaceship") == []


def test_retrieve_limit():
    results = retrieve("portfolio", limit=2)

    assert len(results) <= 2


def test_retrieve_invalid_limit():
    assert retrieve("Python", limit=0) == []
    assert retrieve("Python", limit=-1) == []


def test_chunk_document_preserves_source_and_chunk_metadata():
    document = {
        "source": "test.md",
        "content": (
            "## First\n\n"
            "First section.\n\n"
            "## Second\n\n"
            "Second section."
        ),
    }

    chunks = chunk_document(document)

    assert len(chunks) == 2

    assert chunks[0]["source"] == "test.md"
    assert chunks[0]["chunk"] == 0
    assert "First section" in chunks[0]["content"]

    assert chunks[1]["source"] == "test.md"
    assert chunks[1]["chunk"] == 1
    assert "Second section" in chunks[1]["content"]


def test_load_chunks_returns_chunk_metadata():
    chunks = load_chunks()

    assert len(chunks) == 15

    for chunk in chunks:
        assert "source" in chunk
        assert "content" in chunk
        assert "chunk" in chunk


def test_retrieval_returns_chunk_metadata():
    results = retrieve("Framework-FreeFE")

    assert results

    for result in results:
        assert "source" in result
        assert "content" in result
        assert "chunk" in result
        assert "score" in result


def test_retrieve_preserves_chunk_metadata():
    results = retrieve("AI RAG")

    assert results

    for result in results:
        assert "source" in result
        assert "content" in result
        assert "chunk" in result
        assert "score" in result


def test_retrieve_ai_rag_returns_relevant_chunks():
    results = retrieve(
        "How does the portfolio AI/RAG system work?"
    )

    assert results

    sources = {result["source"] for result in results}

    assert (
        "projects.md" in sources
        or "architecture.md" in sources
    )


def test_retrieve_engineering_goals_returns_engineering_content():
    results = retrieve("What are the engineering goals?")

    assert results

    top = results[0]

    assert top["source"] in {
        "about.md",
        "skills.md",
    }

    assert "Engineering" in top["content"]


def test_retrieve_unknown_question_returns_no_results():
    results = retrieve(
        "What is the capital of France?"
    )

    assert results == []
