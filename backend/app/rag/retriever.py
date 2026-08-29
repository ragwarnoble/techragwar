import re
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "portfolio"

STOP_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "is",
    "are",
    "what",
    "does",
    "do",
    "how",
    "why",
    "where",
    "when",
    "who",
    "use",
    "used",
    "about",
    "tell",
    "me",
}


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())

    return {
        word
        for word in words
        if len(word) > 2 and word not in STOP_WORDS
    }


def load_documents() -> list[dict]:
    documents = []

    if not DATA_DIR.exists():
        return documents

    for path in DATA_DIR.glob("*.md"):
        documents.append(
            {
                "source": path.name,
                "content": path.read_text(encoding="utf-8"),
            }
        )

    return documents


def retrieve(query: str, limit: int = 3) -> list[dict]:
    query_words = tokenize(query)

    results = []

    for document in load_documents():
        document_words = tokenize(document["content"])

        score = len(query_words & document_words)

        if score > 0:
            results.append(
                {
                    "source": document["source"],
                    "content": document["content"],
                    "score": score,
                }
            )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:limit]
