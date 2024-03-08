from pydantic import BaseModel, EmailStr

class Training(BaseModel):
    email: EmailStr