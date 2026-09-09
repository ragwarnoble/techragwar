import pytest

from app.rag import hybrid_retriever


def test_hybrid_tokens_remove_stop_words():
    result = hybrid_retriever._hybrid_tokens(
        "What does the portfolio use for backend development?"
    )

    assert "what" not in result
    assert "does" not in result
    assert "the" not in result
    assert "use" not in result
    assert "portfolio" in result
    assert "backend" in result
    assert "development" in result


def test_hybrid_tokens_ignore_short_words():
    result = hybrid_retriever._hybrid_tokens("AI is an API")

    assert "ai" not in result
    assert "is" not in result
    assert "an" not in result
    assert "api" in result


def test_hybrid_lexical_score():
    score = hybrid_retriever._hybrid_lexical_score(
        "Python backend API",
        "Python backend development",
    )

    assert score == 2


def test_hybrid_lexical_score_empty_query():
    assert (
        hybrid_retriever._hybrid_lexical_score(
            "is the",
            "Python backend",
        )
        == 0
    )


def test_lexical_candidates(monkeypatch):
    chunks = [
        {
            "source": "about.md",
            "content": "Python backend development",
            "chunk": 0,
        },
        {
            "source": "skills.md",
            "content": "SQL database engineering",
            "chunk": 0,
        },
        {
            "source": "projects.md",
            "content": "Python AI project",
            "chunk": 0,
        },
    ]

    monkeypatch.setattr(
        hybrid_retriever,
        "load_chunks",
        lambda: chunks,
    )

    results = hybrid_retriever._lexical_candidates(
        "Python backend"
    )

    assert len(results) == 2
    assert results[0]["source"] == "about.md"
    assert results[0]["lexical_score"] == 2


def test_lexical_candidates_sorted_deterministically(monkeypatch):
    chunks = [
        {
            "source": "z.md",
            "content": "Python API",
            "chunk": 0,
        },
        {
            "source": "a.md",
            "content": "Python API",
            "chunk": 0,
        },
    ]

    monkeypatch.setattr(
        hybrid_retriever,
        "load_chunks",
        lambda: chunks,
    )

    results = hybrid_retriever._lexical_candidates(
        "Python API"
    )

    assert [r["source"] for r in results] == [
        "a.md",
        "z.md",
    ]


def test_lexical_candidates_limit(monkeypatch):
    chunks = [
        {
            "source": f"{i}.md",
            "content": "Python backend API",
            "chunk": 0,
        }
        for i in range(10)
    ]

    monkeypatch.setattr(
        hybrid_retriever,
        "load_chunks",
        lambda: chunks,
    )

    results = hybrid_retriever._lexical_candidates(
        "Python backend API",
        limit=3,
    )

    assert len(results) == 3


def test_semantic_candidates(monkeypatch):
    monkeypatch.setattr(
        hybrid_retriever,
        "embed_text",
        lambda client, query: [1.0, 0.0],
    )

    expected = [
        {
            "source": "about.md",
            "content": "Python backend",
            "chunk": 0,
            "score": 0.9,
        }
    ]

    monkeypatch.setattr(
        hybrid_retriever,
        "retrieve_semantic",
        lambda embedding, chunks, limit: expected,
    )

    result = hybrid_retriever._semantic_candidates(
        "Python",
        [],
        object(),
        limit=3,
    )

    assert result == expected


def test_rank_map():
    results = [
        {"source": "about.md", "chunk": 0},
        {"source": "skills.md", "chunk": 1},
    ]

    result = hybrid_retriever._rank_map(results)

    assert result == {
        ("about.md", 0): 1,
        ("skills.md", 1): 2,
    }


def test_fuse_results_combines_rankings():
    lexical = [
        {
            "source": "about.md",
            "content": "Python backend",
            "chunk": 0,
            "lexical_score": 2,
        },
        {
            "source": "skills.md",
            "content": "SQL",
            "chunk": 0,
            "lexical_score": 1,
        },
    ]

    semantic = [
        {
            "source": "skills.md",
            "content": "SQL",
            "chunk": 0,
            "score": 0.9,
        },
        {
            "source": "projects.md",
            "content": "AI",
            "chunk": 0,
            "score": 0.8,
        },
    ]

    result = hybrid_retriever._fuse_results(
        lexical,
        semantic,
    )

    assert len(result) == 3

    by_key = {
        (item["source"], item["chunk"]): item
        for item in result
    }

    assert by_key[("about.md", 0)]["lexical_rank"] == 1
    assert by_key[("about.md", 0)]["semantic_rank"] is None

    assert by_key[("skills.md", 0)]["lexical_rank"] == 2
    assert by_key[("skills.md", 0)]["semantic_rank"] == 1
    assert by_key[("skills.md", 0)]["semantic_score"] == pytest.approx(0.9)

    assert by_key[("projects.md", 0)]["lexical_rank"] is None
    assert by_key[("projects.md", 0)]["semantic_rank"] == 2


def test_fuse_results_is_deterministic():
    lexical = [
        {
            "source": "b.md",
            "content": "Python",
            "chunk": 0,
            "lexical_score": 1,
        },
        {
            "source": "a.md",
            "content": "Python",
            "chunk": 0,
            "lexical_score": 1,
        },
    ]

    first = hybrid_retriever._fuse_results(
        lexical,
        [],
    )

    second = hybrid_retriever._fuse_results(
        lexical,
        [],
    )

    assert first == second


def test_apply_semantic_gate():
    results = [
        {
            "source": "good.md",
            "chunk": 0,
            "semantic_score": 0.80,
        },
        {
            "source": "bad.md",
            "chunk": 0,
            "semantic_score": 0.40,
        },
    ]

    result = hybrid_retriever._apply_semantic_gate(
        results,
        threshold=0.60,
    )

    assert len(result) == 1
    assert result[0]["source"] == "good.md"


def test_apply_semantic_gate_includes_exact_threshold():
    results = [
        {
            "source": "exact.md",
            "chunk": 0,
            "semantic_score": 0.60,
        }
    ]

    result = hybrid_retriever._apply_semantic_gate(
        results,
        threshold=0.60,
    )

    assert len(result) == 1


def test_select_distinct_sources():
    results = [
        {"source": "about.md", "chunk": 0},
        {"source": "about.md", "chunk": 1},
        {"source": "skills.md", "chunk": 0},
        {"source": "projects.md", "chunk": 0},
    ]

    result = hybrid_retriever._select_distinct_sources(
        results,
        limit=3,
    )

    assert [
        (item["source"], item["chunk"])
        for item in result
    ] == [
        ("about.md", 0),
        ("skills.md", 0),
        ("projects.md", 0),
    ]


def test_select_distinct_sources_limit_zero():
    results = [
        {"source": "about.md", "chunk": 0},
    ]

    assert (
        hybrid_retriever._select_distinct_sources(
            results,
            limit=0,
        )
        == []
    )


def test_build_embedded_chunks(monkeypatch):
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
        hybrid_retriever,
        "load_chunks",
        lambda: chunks,
    )

    embeddings = iter(
        [
            [1.0, 0.0],
            [0.0, 1.0],
        ]
    )

    monkeypatch.setattr(
        hybrid_retriever,
        "embed_text",
        lambda client, text: next(embeddings),
    )

    result = hybrid_retriever.build_embedded_chunks(
        object()
    )

    assert len(result) == 2
    assert result[0]["embedding"] == [1.0, 0.0]
    assert result[1]["embedding"] == [0.0, 1.0]
    assert result[0]["source"] == "about.md"


def test_build_embedded_chunks_empty(monkeypatch):
    monkeypatch.setattr(
        hybrid_retriever,
        "load_chunks",
        lambda: [],
    )

    result = hybrid_retriever.build_embedded_chunks(
        object()
    )

    assert result == []


def test_retrieve_hybrid_limit_zero():
    assert (
        hybrid_retriever.retrieve_hybrid(
            "Python",
            [],
            object(),
            limit=0,
        )
        == []
    )


def test_retrieve_hybrid_pipeline(monkeypatch):
    lexical = [
        {
            "source": "about.md",
            "content": "Python backend",
            "chunk": 0,
            "lexical_score": 2,
        }
    ]

    semantic = [
        {
            "source": "about.md",
            "content": "Python backend",
            "chunk": 0,
            "score": 0.90,
        }
    ]

    monkeypatch.setattr(
        hybrid_retriever,
        "_lexical_candidates",
        lambda query, limit: lexical,
    )

    monkeypatch.setattr(
        hybrid_retriever,
        "_semantic_candidates",
        lambda query, embedded_chunks, client, limit: semantic,
    )

    result = hybrid_retriever.retrieve_hybrid(
        "Python backend",
        [],
        object(),
    )

    assert len(result) == 1
    assert result[0]["source"] == "about.md"
    assert result[0]["semantic_score"] == pytest.approx(0.90)


def test_retrieve_hybrid_rejects_below_threshold(monkeypatch):
    monkeypatch.setattr(
        hybrid_retriever,
        "_lexical_candidates",
        lambda query, limit: [
            {
                "source": "about.md",
                "content": "Python backend",
                "chunk": 0,
                "lexical_score": 2,
            }
        ],
    )

    monkeypatch.setattr(
        hybrid_retriever,
        "_semantic_candidates",
        lambda query, embedded_chunks, client, limit: [
            {
                "source": "about.md",
                "content": "Python backend",
                "chunk": 0,
                "score": 0.30,
            }
        ],
    )

    result = hybrid_retriever.retrieve_hybrid(
        "weather",
        [],
        object(),
    )

    assert result == []


def test_retrieve_hybrid_prefers_distinct_sources(monkeypatch):
    lexical = [
        {
            "source": "about.md",
            "content": "Python",
            "chunk": 0,
            "lexical_score": 3,
        },
        {
            "source": "about.md",
            "content": "FastAPI",
            "chunk": 1,
            "lexical_score": 2,
        },
        {
            "source": "skills.md",
            "content": "SQL",
            "chunk": 0,
            "lexical_score": 1,
        },
    ]

    semantic = [
        {
            "source": "about.md",
            "content": "Python",
            "chunk": 0,
            "score": 0.90,
        },
        {
            "source": "about.md",
            "content": "FastAPI",
            "chunk": 1,
            "score": 0.85,
        },
        {
            "source": "skills.md",
            "content": "SQL",
            "chunk": 0,
            "score": 0.80,
        },
    ]

    monkeypatch.setattr(
        hybrid_retriever,
        "_lexical_candidates",
        lambda query, limit: lexical,
    )

    monkeypatch.setattr(
        hybrid_retriever,
        "_semantic_candidates",
        lambda query, embedded_chunks, client, limit: semantic,
    )

    result = hybrid_retriever.retrieve_hybrid(
        "Python FastAPI SQL",
        [],
        object(),
        limit=2,
    )

    assert len(result) == 2
    assert [item["source"] for item in result] == [
        "about.md",
        "skills.md",
    ]
