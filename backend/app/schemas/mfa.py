from pydantic import BaseModel

class MFASetupRequest(BaseModel):
    user_id: int

class MFASetupResponse(BaseModel):
    secret: str
    qr_code_url: str

class MFAVerifyRequest(BaseModel):
    code: str