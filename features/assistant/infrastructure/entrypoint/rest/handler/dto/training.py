from pydantic import BaseModel, EmailStr

class TrainingRequest(BaseModel):
    tenant_id: str
    notification_email: EmailStr