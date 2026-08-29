from openai import OpenAI

from .config import settings
from .rag.prompts import RAG_SYSTEM_PROMPT
from .rag.retriever import retrieve


class AIService:
    def __init__(self):
        self.api_key = settings.ai_api_key
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
                "I don't have that information in the "
                "Ragwar Tech portfolio knowledge base."
            )

        context = "\n\n".join(
            document["content"]
            for document in documents
        )

        return (
            "AI service is currently unavailable. "
            "Here is the relevant portfolio information:\n\n"
            f"{context}"
        )

    def chat(self, message: str) -> str:
        documents = retrieve(message)

        if not self.client:
            return self._fallback_response(message, documents)

        context = "\n\n".join(
            f"Source: {document['source']}\n"
            f"{document['content']}"
            for document in documents
        )

        if not context:
            context = (
                "No relevant information was found in the "
                "portfolio knowledge base."
            )

        prompt = f"""
Portfolio context:

{context}

User question:

{message}
"""

        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=RAG_SYSTEM_PROMPT,
                input=prompt,
            )

            return response.output_text

        except Exception:
            return self._fallback_response(message, documents)


ai_service = AIService()
