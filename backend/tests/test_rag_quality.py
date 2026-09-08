from app.rag.evaluation import (
    evaluate,
    mean_reciprocal_rank_results,
)


def test_rag_quality_gate():
    results = evaluate()

    assert results

    hit_rate = (
        sum(result["hit"] for result in results)
        / len(results)
    )

    mrr = mean_reciprocal_rank_results(
        results
    )

    duplicate_sources = sum(
        len(result["retrieved_sources"])
        - len(set(result["retrieved_sources"]))
        for result in results
    )

    assert hit_rate >= 0.80
    assert mrr >= 0.80
    assert duplicate_sources == 0