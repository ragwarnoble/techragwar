import pytest

from app.rag import semantic_retriever


class FakeModel:
    def __init__(self):
        self.calls = []

    def encode(self, texts, normalize_embeddings=True):
        self.calls.append(texts)

        if isinstance(texts, str):
            return [1.0, 0.0]

        return [
            [1.0, 0.0],
            [0.0, 1.0],
        ]


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


def test_get_model(monkeypatch):
    model = FakeModel()

    monkeypatch.setattr(
        semantic_retriever,
        "SentenceTransformer",
        lambda name: model,
    )

    semantic_retriever.get_model.cache_clear()

    result = semantic_retriever.get_model()

    assert result is model

    semantic_retriever.get_model.cache_clear()


def test_build_index(monkeypatch):
    model = FakeModel()

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

    monkeypatch.setattr(
        semantic_retriever,
        "get_model",
        lambda: model,
    )

    monkeypatch.setattr(
        semantic_retriever,
        "load_chunks",
        lambda: chunks,
    )

    semantic_retriever.build_index.cache_clear()

    result = semantic_retriever.build_index()

    assert len(result) == 2
    assert result[0]["source"] == "about.md"
    assert result[1]["source"] == "skills.md"
    assert "embedding" in result[0]

    semantic_retriever.build_index.cache_clear()


def test_build_index_empty(monkeypatch):
    monkeypatch.setattr(
        semantic_retriever,
        "load_chunks",
        lambda: [],
    )

    semantic_retriever.build_index.cache_clear()

    assert semantic_retriever.build_index() == []

    semantic_retriever.build_index.cache_clear()


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
    model = FakeModel()

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
        "get_model",
        lambda: model,
    )

    monkeypatch.setattr(
        semantic_retriever,
        "build_index",
        lambda: chunks,
    )

    result = semantic_retriever.retrieve_semantic(
        "Python",
        limit=1,
    )

    assert len(result) == 1
    assert result[0]["source"] == "about.md"
    assert result[0]["score"] == pytest.approx(1.0)


def test_retrieve_semantic_sorted(monkeypatch):
    model = FakeModel()

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
        "get_model",
        lambda: model,
    )

    monkeypatch.setattr(
        semantic_retriever,
        "build_index",
        lambda: chunks,
    )

    result = semantic_retriever.retrieve_semantic(
        "Python",
        limit=3,
    )

    assert result[0]["source"] == "about.md"
    assert result[1]["source"] == "skills.md"