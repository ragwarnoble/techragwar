from app.rag import hybrid_retriever


def test_hybrid_tokens():
    result = hybrid_retriever._hybrid_tokens("What backend tools are used?")

    assert "backend" in result
    assert "tools" in result
    assert "what" not in result
    assert "are" not in result


def test_hybrid_lexical_score():
    score = hybrid_retriever._hybrid_lexical_score(
        "Python backend",
        "Python FastAPI backend development",
    )

    assert score == 2


def test_hybrid_lexical_score_no_overlap():
    score = hybrid_retriever._hybrid_lexical_score(
        "database",
        "Python FastAPI frontend",
    )

    assert score == 0


def test_lexical_candidates_invalid_query():
    assert hybrid_retriever._lexical_candidates("") == []
    assert hybrid_retriever._lexical_candidates("   ") == []


def test_lexical_candidates_invalid_limit():
    assert (
        hybrid_retriever._lexical_candidates(
            "Python",
            limit=0,
        )
        == []
    )


def test_rank_map():
    results = [
        {"source": "about.md", "chunk": 0},
        {"source": "skills.md", "chunk": 0},
    ]

    result = hybrid_retriever._rank_map(results)

    assert result == {
        ("about.md", 0): 1,
        ("skills.md", 0): 2,
    }


def test_fuse_results_combines_lexical_and_semantic():
    lexical = [
        {
            "source": "skills.md",
            "content": "Python",
            "chunk": 0,
            "lexical_score": 2,
        },
    ]

    semantic = [
        {
            "source": "skills.md",
            "content": "Python",
            "chunk": 0,
            "score": 0.9,
        },
    ]

    result = hybrid_retriever._fuse_results(
        lexical,
        semantic,
    )

    assert len(result) == 1
    assert result[0]["source"] == "skills.md"
    assert result[0]["lexical_score"] == 2
    assert result[0]["semantic_score"] == 0.9
    assert result[0]["lexical_rank"] == 1
    assert result[0]["semantic_rank"] == 1
    assert result[0]["hybrid_score"] > 0


def test_fuse_results_preserves_semantic_only_results():
    lexical = []

    semantic = [
        {
            "source": "architecture.md",
            "content": "FastAPI backend",
            "chunk": 0,
            "score": 0.85,
        },
    ]

    result = hybrid_retriever._fuse_results(
        lexical,
        semantic,
    )

    assert len(result) == 1
    assert result[0]["source"] == "architecture.md"
    assert result[0]["lexical_score"] == 0
    assert result[0]["semantic_score"] == 0.85
    assert result[0]["lexical_rank"] is None
    assert result[0]["semantic_rank"] == 1


def test_fuse_results_preserves_lexical_only_results():
    lexical = [
        {
            "source": "skills.md",
            "content": "Python",
            "chunk": 0,
            "lexical_score": 2,
        },
    ]

    semantic = []

    result = hybrid_retriever._fuse_results(
        lexical,
        semantic,
    )

    assert len(result) == 1
    assert result[0]["source"] == "skills.md"
    assert result[0]["lexical_score"] == 2
    assert result[0]["semantic_score"] == 0.0
    assert result[0]["lexical_rank"] == 1
    assert result[0]["semantic_rank"] is None


def test_apply_semantic_gate():
    results = [
        {
            "source": "about.md",
            "chunk": 0,
            "semantic_score": 0.8,
        },
        {
            "source": "skills.md",
            "chunk": 0,
            "semantic_score": 0.5,
        },
    ]

    result = hybrid_retriever._apply_semantic_gate(
        results,
        threshold=0.6,
    )

    assert len(result) == 1
    assert result[0]["source"] == "about.md"


def test_apply_semantic_gate_boundary():
    results = [
        {
            "source": "about.md",
            "chunk": 0,
            "semantic_score": 0.6,
        },
    ]

    result = hybrid_retriever._apply_semantic_gate(
        results,
        threshold=0.6,
    )

    assert len(result) == 1


def test_select_distinct_sources():
    results = [
        {"source": "skills.md", "chunk": 0},
        {"source": "skills.md", "chunk": 1},
        {"source": "about.md", "chunk": 0},
        {"source": "architecture.md", "chunk": 0},
    ]

    result = hybrid_retriever._select_distinct_sources(
        results,
        limit=3,
    )

    assert [item["source"] for item in result] == [
        "skills.md",
        "about.md",
        "architecture.md",
    ]


def test_select_distinct_sources_respects_limit():
    results = [
        {"source": "about.md", "chunk": 0},
        {"source": "skills.md", "chunk": 0},
        {"source": "architecture.md", "chunk": 0},
    ]

    result = hybrid_retriever._select_distinct_sources(
        results,
        limit=2,
    )

    assert len(result) == 2


def test_select_distinct_sources_invalid_limit():
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


def test_retrieve_hybrid_invalid_query():
    assert hybrid_retriever.retrieve_hybrid("") == []
    assert hybrid_retriever.retrieve_hybrid("   ") == []


def test_retrieve_hybrid_invalid_limit():
    assert (
        hybrid_retriever.retrieve_hybrid(
            "Python",
            limit=0,
        )
        == []
    )


def test_retrieve_hybrid_no_embedded_chunks(monkeypatch):
    monkeypatch.setattr(
        hybrid_retriever,
        "build_embedded_chunks",
        list,
    )

    result = hybrid_retriever.retrieve_hybrid(
        "Python",
    )

    assert result == []


def test_retrieve_hybrid_combines_results(monkeypatch):
    lexical = [
        {
            "source": "skills.md",
            "content": "Python FastAPI",
            "chunk": 0,
            "lexical_score": 2,
        },
    ]

    semantic = [
        {
            "source": "skills.md",
            "content": "Python FastAPI",
            "chunk": 0,
            "score": 0.9,
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
        lambda query, embedded_chunks, limit: semantic,
    )

    embedded_chunks = [
        {
            "source": "skills.md",
            "content": "Python FastAPI",
            "chunk": 0,
            "embedding": [1.0, 0.0],
        }
    ]

    result = hybrid_retriever.retrieve_hybrid(
        "Python",
        embedded_chunks,
        limit=3,
    )

    assert len(result) == 1
    assert result[0]["source"] == "skills.md"
    assert result[0]["semantic_score"] == 0.9


def test_retrieve_hybrid_semantic_gate(monkeypatch):
    lexical = [
        {
            "source": "skills.md",
            "content": "Python",
            "chunk": 0,
            "lexical_score": 1,
        },
    ]

    semantic = [
        {
            "source": "skills.md",
            "content": "Python",
            "chunk": 0,
            "score": 0.4,
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
        lambda query, embedded_chunks, limit: semantic,
    )

    embedded_chunks = [
        {
            "source": "skills.md",
            "content": "Python",
            "chunk": 0,
            "embedding": [1.0, 0.0],
        }
    ]

    result = hybrid_retriever.retrieve_hybrid(
        "Python",
        embedded_chunks,
        limit=3,
    )

    assert result == []


def test_retrieve_hybrid_source_diversity(monkeypatch):
    lexical = [
        {
            "source": "skills.md",
            "content": "Python",
            "chunk": 0,
            "lexical_score": 3,
        },
        {
            "source": "skills.md",
            "content": "FastAPI",
            "chunk": 1,
            "lexical_score": 2,
        },
        {
            "source": "about.md",
            "content": "Python",
            "chunk": 0,
            "lexical_score": 1,
        },
    ]

    semantic = [
        {
            "source": "skills.md",
            "content": "Python",
            "chunk": 0,
            "score": 0.9,
        },
        {
            "source": "skills.md",
            "content": "FastAPI",
            "chunk": 1,
            "score": 0.85,
        },
        {
            "source": "about.md",
            "content": "Python",
            "chunk": 0,
            "score": 0.8,
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
        lambda query, embedded_chunks, limit: semantic,
    )

    embedded_chunks = [
        {
            "source": "skills.md",
            "content": "Python",
            "chunk": 0,
            "embedding": [1.0, 0.0],
        }
    ]

    result = hybrid_retriever.retrieve_hybrid(
        "Python",
        embedded_chunks,
        limit=2,
    )

    assert len(result) == 2
    assert len({item["source"] for item in result}) == 2


def test_retrieve_hybrid_deterministic_tie_breaking(monkeypatch):
    lexical = [
        {
            "source": "about.md",
            "content": "Python",
            "chunk": 0,
            "lexical_score": 1,
        },
        {
            "source": "skills.md",
            "content": "Python",
            "chunk": 0,
            "lexical_score": 1,
        },
    ]

    semantic = [
        {
            "source": "skills.md",
            "content": "Python",
            "chunk": 0,
            "score": 0.8,
        },
        {
            "source": "about.md",
            "content": "Python",
            "chunk": 0,
            "score": 0.8,
        },
    ]

    embedded_chunks = [
        {
            "source": "about.md",
            "content": "Python",
            "chunk": 0,
            "embedding": [1.0, 0.0],
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
        lambda query, embedded_chunks, limit: semantic,
    )

    result = hybrid_retriever.retrieve_hybrid(
        "Python",
        embedded_chunks,
        limit=2,
    )

    assert [item["source"] for item in result] == [
        "about.md",
        "skills.md",
    ]


def test_retrieve_hybrid_uses_build_index_when_not_supplied(monkeypatch):
    embedded_chunks = [
        {
            "source": "skills.md",
            "content": "Python",
            "chunk": 0,
            "embedding": [1.0, 0.0],
        }
    ]

    monkeypatch.setattr(
        hybrid_retriever,
        "build_embedded_chunks",
        lambda: embedded_chunks,
    )

    monkeypatch.setattr(
        hybrid_retriever,
        "_lexical_candidates",
        lambda query, limit: [
            {
                "source": "skills.md",
                "content": "Python",
                "chunk": 0,
                "lexical_score": 1,
            }
        ],
    )

    monkeypatch.setattr(
        hybrid_retriever,
        "_semantic_candidates",
        lambda query, embedded_chunks, limit: [
            {
                "source": "skills.md",
                "content": "Python",
                "chunk": 0,
                "score": 0.9,
            }
        ],
    )

    result = hybrid_retriever.retrieve_hybrid(
        "Python",
    )

    assert len(result) == 1
    assert result[0]["source"] == "skills.md"


def test_build_embedded_chunks_delegates(monkeypatch):
    expected = [
        {
            "source": "skills.md",
            "content": "Python",
            "chunk": 0,
            "embedding": [1.0, 0.0],
        }
    ]

    monkeypatch.setattr(
        hybrid_retriever,
        "build_index",
        lambda: expected,
    )

    assert hybrid_retriever.build_embedded_chunks() == expected
