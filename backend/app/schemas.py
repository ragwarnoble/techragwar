from datetime import datetime
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr


class ContactCreate(BaseModel):

    name: str

    email: EmailStr

    message: str


class ContactResponse(BaseModel):

    id: int
    name: str
    email: str
    message: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ChatRequest(BaseModel):

    message: str


class ChatResponse(BaseModel):

    response: str