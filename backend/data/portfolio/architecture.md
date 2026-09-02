# Architecture

The portfolio follows a separation between frontend, backend, AI
services, and data.

The frontend communicates with backend services through HTTP APIs.

The FastAPI backend exposes application endpoints and delegates AI
requests to the AI service.

The AI service obtains information by retrieving relevant portfolio
knowledge before sending context to the language model.

The RAG layer is responsible for portfolio document retrieval and
context preparation.

The architecture is designed to be deterministic, testable, portable,
and maintainable.
