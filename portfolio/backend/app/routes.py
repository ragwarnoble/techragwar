from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from .ai import ai_service
from .database import get_db
from .models import ContactMessage
from .schemas import ChatRequest
from .schemas import ChatResponse
from .schemas import ContactCreate
from .schemas import ContactResponse


router = APIRouter(
    prefix="/api"
)


@router.get("/health")
def health():

    return {
        "status": "ok",
        "service": "framework-freefe-api",
    }


@router.post(
    "/contact",
    response_model=ContactResponse,
)
def create_contact(
    payload: ContactCreate,
    db: Session = Depends(get_db),
):

    message = ContactMessage(
        name=payload.name,
        email=payload.email,
        message=payload.message,
    )

    db.add(message)

    db.commit()

    db.refresh(message)

    return message


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    payload: ChatRequest,
):

    response = ai_service.chat(
        payload.message
    )

    return {
        "response": response
    }