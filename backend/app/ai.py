from openai import OpenAI

from .config import settings


SYSTEM_PROMPT = """
You are the AI assistant for Ragwar Tech.

You help visitors understand:

- the developer's portfolio
- software engineering projects
- AI and LLM projects
- frontend development
- backend development
- APIs
- deployment
- agentic systems

Be concise, professional, and technically useful.

Do not invent projects, employment history,
credentials, clients, or accomplishments.

If information is unavailable, say so.
"""


class AIService:

    def __init__(self):

        self.client = None

        if settings.ai_api_key:

            self.client = OpenAI(
                api_key=settings.ai_api_key
            )


    def chat(self, message: str) -> str:

        if not self.client:

            return (
                "AI service is not configured yet. "
                "Add AI_API_KEY to backend/.env."
            )


        response = self.client.responses.create(

            model=settings.ai_model,

            instructions=SYSTEM_PROMPT,

            input=message,

        )


        return response.output_text


ai_service = AIService()
