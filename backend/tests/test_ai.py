from unittest.mock import MagicMock

from app.ai import AIService


def test_ai_service_without_api_key(monkeypatch):

    monkeypatch.setattr(
        "app.ai.settings.google_api_key",
        "",
    )

    service = AIService()

    assert service.client is None


def test_ai_service_with_google_api_key(monkeypatch):

    monkeypatch.setattr(
        "app.ai.settings.google_api_key",
        "test-key",
    )

    mock_client = MagicMock()

    monkeypatch.setattr(
        "app.ai.genai.Client",
        lambda api_key: mock_client,
    )

    service = AIService()

    assert service.client is mock_client


def test_chat_uses_rag_fallback(monkeypatch):

    monkeypatch.setattr(
        "app.ai.settings.google_api_key",
        "",
    )

    documents = [
        {
            "source": "skills.md",
            "chunk": 1,
            "content": (
                "Python and FastAPI are used "
                "for backend development."
            ),
        }
    ]

    monkeypatch.setattr(
        "app.ai.retrieve",
        lambda message: documents,
    )

    service = AIService()

    response = service.chat(
        "What is used for backend development?"
    )

    assert "Python" in response["response"]
    assert "FastAPI" in response["response"]
    assert response["sources"] == ["skills.md"]


def test_unknown_question_does_not_call_gemini(monkeypatch):

    monkeypatch.setattr(
        "app.ai.settings.google_api_key",
        "test-key",
    )

    mock_client = MagicMock()

    monkeypatch.setattr(
        "app.ai.genai.Client",
        lambda api_key: mock_client,
    )

    monkeypatch.setattr(
        "app.ai.retrieve",
        lambda message: [],
    )

    service = AIService()

    response = service.chat(
        "What is the capital of France?"
    )

    assert (
        response["response"]
        == "That information is not available in the "
        "portfolio knowledge base."
    )

    assert response["sources"] == []

    mock_client.models.generate_content.assert_not_called()


def test_gemini_receives_rag_context(monkeypatch):

    monkeypatch.setattr(
        "app.ai.settings.google_api_key",
        "test-key",
    )

    mock_client = MagicMock()

    mock_response = MagicMock()
    mock_response.text = (
        "Python and FastAPI are used for backend development."
    )

    mock_client.models.generate_content.return_value = (
        mock_response
    )

    monkeypatch.setattr(
        "app.ai.genai.Client",
        lambda api_key: mock_client,
    )

    documents = [
        {
            "source": "skills.md",
            "chunk": 1,
            "content": (
                "Python and FastAPI are used "
                "for backend development."
            ),
        }
    ]

    monkeypatch.setattr(
        "app.ai.retrieve",
        lambda message: documents,
    )

    service = AIService()

    response = service.chat(
        "What is used for backend development?"
    )

    assert (
        response["response"]
        == "Python and FastAPI are used for backend development."
    )

    assert response["sources"] == ["skills.md"]

    mock_client.models.generate_content.assert_called_once()

    call_kwargs = (
        mock_client
        .models
        .generate_content
        .call_args.kwargs
    )

    prompt = call_kwargs["contents"]

    assert "Python and FastAPI" in prompt
    assert "skills.md" in prompt
    assert "What is used for backend development?" in prompt


def test_gemini_failure_uses_fallback(monkeypatch):

    monkeypatch.setattr(
        "app.ai.settings.google_api_key",
        "test-key",
    )

    mock_client = MagicMock()

    mock_client.models.generate_content.side_effect = (
        RuntimeError("Gemini unavailable")
    )

    monkeypatch.setattr(
        "app.ai.genai.Client",
        lambda api_key: mock_client,
    )

    documents = [
        {
            "source": "skills.md",
            "chunk": 1,
            "content": (
                "Python and FastAPI are used "
                "for backend development."
            ),
        }
    ]

    monkeypatch.setattr(
        "app.ai.retrieve",
        lambda message: documents,
    )

    service = AIService()

    response = service.chat(
        "What is used for backend development?"
    )

    assert (
        "AI service is currently unavailable."
        in response["response"]
    )

    assert "Python" in response["response"]
    assert "FastAPI" in response["response"]

    assert response["sources"] == ["skills.md"]