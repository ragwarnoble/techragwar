from datetime import datetime

from pydantic import BaseModel
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

    class Config:
        from_attributes = True
