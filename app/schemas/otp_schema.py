from pydantic import BaseModel, Field

class SendOTPRequest(BaseModel):
    phone: str = Field(..., description="Phone number in E.164 or local format")

class VerifyOTPRequest(BaseModel):
    phone: str
    code: str
