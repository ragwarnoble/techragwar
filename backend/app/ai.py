from openai import OpenAI

from .config import settings
from .rag.context import build_context
from .rag.prompts import RAG_SYSTEM_PROMPT
from .rag.retriever import retrieve


class AIService:

    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.ai_model

        self.client = (
            OpenAI(api_key=self.api_key)
            if self.api_key
            else None
        )

    def _fallback_response(
        self,
        message: str,
        documents: list[dict],
    ) -> str:

        if not documents:
            return (
                "That information is not available in the "
                "portfolio knowledge base."
            )

        context = build_context(
            message,
            results=documents,
        )

        if not context:
            return (
                "That information is not available in the "
                "portfolio knowledge base."
            )

        return (
            "AI service is currently unavailable. "
            "Here is the relevant portfolio information:\n\n"
            f"{context}"
        )

    def chat(self, message: str) -> dict:

        documents = retrieve(message)

        sources = [
            document["source"]
            for document in documents
        ]

        if not documents:
            return {
                "response": (
                    "That information is not available in the "
                    "portfolio knowledge base."
                ),
                "sources": [],
            }

        context = build_context(
            message,
            results=documents,
        )

        if not context:
            return {
                "response": (
                    "That information is not available in the "
                    "portfolio knowledge base."
                ),
                "sources": [],
            }

        if not self.client:
            return {
                "response": self._fallback_response(
                    message,
                    documents,
                ),
                "sources": sources,
            }

        prompt = (
            "Portfolio context:\n\n"
            f"{context}\n\n"
            "User question:\n\n"
            f"{message}"
        )

        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=RAG_SYSTEM_PROMPT,
                input=prompt,
            )

            return {
                "response": response.output_text,
                "sources": sources,
            }

        except Exception as exc:
            print(
                f"OpenAI API error: "
                f"{type(exc).__name__}: {exc}"
            )

            return {
                "response": self._fallback_response(
                    message,
                    documents,
                ),
                "sources": sources,
            }


ai_service = AIService()
