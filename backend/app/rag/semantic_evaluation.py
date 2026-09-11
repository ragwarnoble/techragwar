from statistics import mean

from app.config import settings
from app.rag.evaluation import EVALUATION_CASES
from app.rag.ingest import load_chunks
from app.rag.openai_embeddings import embedding_service

EMBEDDING_MODEL = settings.embedding_model
LIMIT = 3


def cosine_similarity(vector_a, vector_b):
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b, strict=True))

    magnitude_a = sum(a * a for a in vector_a) ** 0.5

    magnitude_b = sum(b * b for b in vector_b) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def unique_sources(retrieved_sources):
    """
    Preserve first-seen source order while removing duplicates.
    """
    return list(dict.fromkeys(retrieved_sources))


def hit_at_k(retrieved_sources, expected_sources):
    expected_sources = set(expected_sources)

    # For out-of-scope queries, success means
    # no portfolio source was retrieved.
    if not expected_sources:
        return len(retrieved_sources) == 0

    return bool(set(retrieved_sources) & expected_sources)


def source_recall_at_k(
    retrieved_sources,
    expected_sources,
):
    expected_sources = set(expected_sources)

    if not expected_sources:
        return 0.0

    retrieved = set(retrieved_sources)

    return len(retrieved & expected_sources) / len(expected_sources)


def source_precision_at_k(
    retrieved_sources,
    expected_sources,
):
    expected_sources = set(expected_sources)
    retrieved = set(retrieved_sources)

    if not retrieved:
        return 0.0

    return len(retrieved & expected_sources) / len(retrieved)


def chunk_precision_at_k(
    retrieved_sources,
    expected_sources,
):
    expected_sources = set(expected_sources)

    if not retrieved_sources:
        return 0.0

    relevant_chunks = sum(source in expected_sources for source in retrieved_sources)

    return relevant_chunks / len(retrieved_sources)


def duplicate_rate(retrieved_sources):
    if not retrieved_sources:
        return 0.0

    unique_count = len(set(retrieved_sources))

    duplicate_count = len(retrieved_sources) - unique_count

    return duplicate_count / len(retrieved_sources)


def reciprocal_rank(
    retrieved_sources,
    expected_sources,
):
    expected_sources = set(expected_sources)

    if not expected_sources:
        return 0.0

    for rank, source in enumerate(
        retrieved_sources,
        start=1,
    ):
        if source in expected_sources:
            return 1.0 / rank

    return 0.0


def retrieve_semantic(
    query_embedding,
    embedded_chunks,
    limit=LIMIT,
):
    scored = []

    for chunk in embedded_chunks:
        score = cosine_similarity(
            query_embedding,
            chunk["embedding"],
        )

        scored.append(
            {
                "source": chunk["source"],
                "chunk": chunk["chunk"],
                "content": chunk["content"],
                "score": score,
            }
        )

    # Deterministic ordering:
    # 1. Highest semantic similarity
    # 2. Source name
    # 3. Chunk number
    scored.sort(
        key=lambda item: (
            -item["score"],
            item["source"],
            item["chunk"],
        )
    )

    return scored[:limit]


def evaluate_case(
    query_embedding,
    embedded_chunks,
    query,
    expected_sources,
):
    retrieved = retrieve_semantic(
        query_embedding,
        embedded_chunks,
        LIMIT,
    )

    retrieved_sources = [result["source"] for result in retrieved]

    expected_sources = set(expected_sources)

    unique_retrieved = unique_sources(retrieved_sources)

    hit = hit_at_k(
        retrieved_sources,
        expected_sources,
    )

    source_recall = source_recall_at_k(
        retrieved_sources,
        expected_sources,
    )

    source_precision = source_precision_at_k(
        retrieved_sources,
        expected_sources,
    )

    chunk_precision = chunk_precision_at_k(
        retrieved_sources,
        expected_sources,
    )

    dup_rate = duplicate_rate(retrieved_sources)

    rr = reciprocal_rank(
        retrieved_sources,
        expected_sources,
    )

    return {
        "query": query,
        "expected_sources": sorted(expected_sources),
        "retrieved": retrieved,
        "retrieved_sources": retrieved_sources,
        "unique_sources": unique_retrieved,
        "hit": hit,
        "source_recall": source_recall,
        "source_precision": source_precision,
        "chunk_precision": chunk_precision,
        "duplicate_rate": dup_rate,
        "reciprocal_rank": rr,
    }


def print_case(result):
    print()
    print(f"Query: {result['query']}")

    print(f"Expected:             {result['expected_sources']}")

    print(f"Retrieved chunks:     {result['retrieved_sources']}")

    print(f"Unique sources:       {result['unique_sources']}")

    print("Similarity scores:")

    for item in result["retrieved"]:
        print(f"  {item['source']}:{item['chunk']} score={item['score']:.4f}")

    print(f"Hit@3:               {result['hit']}")

    print(f"Source Recall@3:     {result['source_recall']:.3f}")

    print(f"Source Precision@3:  {result['source_precision']:.3f}")

    print(f"Chunk Precision@3:   {result['chunk_precision']:.3f}")

    print(f"Duplicate Rate@3:    {result['duplicate_rate']:.3f}")

    print(f"Reciprocal Rank:      {result['reciprocal_rank']:.3f}")


def main():
    print("SEMANTIC RAG EVALUATION")
    print("=" * 70)
    print()
    print(f"Embedding model: {EMBEDDING_MODEL}")

    chunks = load_chunks()

    print(f"Chunks evaluated: {len(chunks)}")

    if not embedding_service.available:
        raise RuntimeError(
            "OpenAI embedding service is not configured. "
            "Check OPENAI_API_KEY in backend/.env."
        )

    print()
    print("Embedding knowledge base chunks...")

    embeddings = embedding_service.embed_documents(
        [chunk["content"] for chunk in chunks]
    )

    embedded_chunks = []

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings, strict=True),
        start=1,
    ):
        print(f"  [{index}/{len(chunks)}] {chunk['source']}:{chunk['chunk']}")

        embedded_chunks.append(
            {
                **chunk,
                "embedding": embedding,
            }
        )

    print()
    print("Embedding evaluation queries...")

    query_embeddings = embedding_service.embed_documents(
        [case["query"] for case in EVALUATION_CASES]
    )

    for index, case in enumerate(
        EVALUATION_CASES,
        start=1,
    ):
        print(f"  [{index}/{len(EVALUATION_CASES)}] {case['query']}")

    print()
    print("=" * 70)
    print("SEMANTIC RETRIEVAL RESULTS")
    print("=" * 70)

    results = []

    for case, query_embedding in zip(
        EVALUATION_CASES,
        query_embeddings,
        strict=True,
    ):
        result = evaluate_case(
            query_embedding,
            embedded_chunks,
            case["query"],
            case["expected_sources"],
        )

        results.append(result)

        print_case(result)

    print()
    print("=" * 70)
    print("SEMANTIC RAG RESULTS")
    print("=" * 70)

    print(f"Hit Rate@3:          {mean(r['hit'] for r in results):.3f}")

    print(f"Source Recall@3:     {mean(r['source_recall'] for r in results):.3f}")

    print(f"Source Precision@3:  {mean(r['source_precision'] for r in results):.3f}")

    print(f"Chunk Precision@3:   {mean(r['chunk_precision'] for r in results):.3f}")

    print(f"Duplicate Rate@3:    {mean(r['duplicate_rate'] for r in results):.3f}")

    print(f"MRR@3:               {mean(r['reciprocal_rank'] for r in results):.3f}")


if __name__ == "__main__":
    main()
