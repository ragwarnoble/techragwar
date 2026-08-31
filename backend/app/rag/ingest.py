from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "portfolio"


def load_markdown_documents() -> list[dict]:
    """Load portfolio Markdown documents from the knowledge directory."""

    if not DATA_DIR.exists():
        return []

    documents = []

    for path in sorted(DATA_DIR.glob("*.md")):
        content = path.read_text(encoding="utf-8").strip()

        if not content:
            continue

        documents.append(
            {
                "source": path.name,
                "content": content,
            }
        )

    return documents


def ingest() -> list[dict]:
    """Return the current portfolio knowledge documents."""

    return load_markdown_documents()


if __name__ == "__main__":
    documents = ingest()

    print(f"Loaded {len(documents)} documents.")

    for document in documents:
        print(f"- {document['source']}")
