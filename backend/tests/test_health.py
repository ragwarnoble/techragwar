from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat(monkeypatch):

    monkeypatch.setattr(
        "app.routes.ai_service.chat",
        lambda message: {
            "response": (
                "Python and FastAPI are used "
                "for backend development."
            ),
            "sources": ["skills.md"],
        },
    )

    response = client.post(
        "/api/chat",
        json={
            "message": (
                "What tools are used for "
                "server-side development?"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "response": (
            "Python and FastAPI are used "
            "for backend development."
        ),
        "sources": ["skills.md"],
    }


def test_chat_unknown_question(monkeypatch):

    monkeypatch.setattr(
        "app.routes.ai_service.chat",
        lambda message: {
            "response": (
                "That information is not available "
                "in the portfolio knowledge base."
            ),
            "sources": [],
        },
    )

    response = client.post(
        "/api/chat",
        json={
            "message": "What is the capital of France?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "response": (
            "That information is not available "
            "in the portfolio knowledge base."
        ),
        "sources": [],
    }


def test_chat_requires_message():

    response = client.post(
        "/api/chat",
        json={},
    )

    assert response.status_code == 422


def test_chat_rejects_invalid_message_type():

    response = client.post(
        "/api/chat",
        json={
            "message": 123
        },
    )

    assert response.status_code == 422