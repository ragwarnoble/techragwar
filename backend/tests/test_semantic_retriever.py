import pytest

from app.rag import semantic_retriever


def test_cosine_similarity():
    result = semantic_retriever.cosine_similarity(
        [1.0, 0.0],
        [1.0, 0.0],
    )

    assert result == pytest.approx(1.0)


def test_cosine_similarity_orthogonal():
    result = semantic_retriever.cosine_similarity(
        [1.0, 0.0],
        [0.0, 1.0],
    )

    assert result == pytest.approx(0.0)


def test_cosine_similarity_zero_vector():
    result = semantic_retriever.cosine_similarity(
        [0.0, 0.0],
        [1.0, 0.0],
    )

    assert result == 0.0


def test_cosine_similarity_zero_document_vector():
    result = semantic_retriever.cosine_similarity(
        [1.0, 0.0],
        [0.0, 0.0],
    )

    assert result == 0.0


def test_build_index(monkeypatch):
    chunks = [
        {
            "source": "about.md",
            "content": "Python backend",
            "chunk": 0,
        },
        {
            "source": "skills.md",
            "content": "SQL database",
            "chunk": 0,
        },
    ]

    embeddings = [
        [1.0, 0.0],
        [0.0, 1.0],
    ]

    monkeypatch.setattr(
        semantic_retriever,
        "load_chunks",
        lambda: chunks,
    )

    monkeypatch.setattr(
        semantic_retriever.embedding_service,
        "embed_documents",
        lambda texts: embeddings,
    )

    result = semantic_retriever.build_index()

    assert len(result) == 2
    assert result[0]["source"] == "about.md"
    assert result[1]["source"] == "skills.md"
    assert result[0]["embedding"] == [1.0, 0.0]
    assert result[1]["embedding"] == [0.0, 1.0]


def test_build_index_empty(monkeypatch):
    monkeypatch.setattr(
        semantic_retriever,
        "load_chunks",
        list,
    )

    result = semantic_retriever.build_index()

    assert result == []


def test_retrieve_semantic_limit_zero():
    assert (
        semantic_retriever.retrieve_semantic(
            "Python",
            limit=0,
        )
        == []
    )


def test_retrieve_semantic_empty_query():
    assert (
        semantic_retriever.retrieve_semantic(
            "   ",
        )
        == []
    )


def test_retrieve_semantic(monkeypatch):
    chunks = [
        {
            "source": "about.md",
            "content": "Python backend",
            "chunk": 0,
            "embedding": [1.0, 0.0],
        },
        {
            "source": "skills.md",
            "content": "SQL database",
            "chunk": 0,
            "embedding": [0.0, 1.0],
        },
    ]

    monkeypatch.setattr(
        semantic_retriever,
        "build_index",
        lambda: chunks,
    )

    monkeypatch.setattr(
        semantic_retriever.embedding_service,
        "embed_query",
        lambda text: [1.0, 0.0],
    )

    result = semantic_retriever.retrieve_semantic(
        "Python",
        limit=1,
    )

    assert len(result) == 1
    assert result[0]["source"] == "about.md"
    assert result[0]["score"] == pytest.approx(1.0)


def test_retrieve_semantic_sorted(monkeypatch):
    chunks = [
        {
            "source": "skills.md",
            "content": "SQL database",
            "chunk": 0,
            "embedding": [0.0, 1.0],
        },
        {
            "source": "about.md",
            "content": "Python backend",
            "chunk": 0,
            "embedding": [1.0, 0.0],
        },
    ]

    monkeypatch.setattr(
        semantic_retriever,
        "build_index",
        lambda: chunks,
    )

    monkeypatch.setattr(
        semantic_retriever.embedding_service,
        "embed_query",
        lambda text: [1.0, 0.0],
    )

    result = semantic_retriever.retrieve_semantic(
        "Python",
        limit=3,
    )

    assert result[0]["source"] == "about.md"
    assert result[1]["source"] == "skills.md"
