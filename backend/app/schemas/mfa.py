from pydantic import BaseModel
from app.schemas.user import UserResponse


class MFASetupRequest(BaseModel):
    user_id: int

class MFASetupResponse(BaseModel):
    secret: str
    qr_code_url: str
    user: UserResponse

class MFAVerifyResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse

class MFAVerifyRequest(BaseModel):
    user_id: int
    code: str

class MFADisableResponse(BaseModel):
    user: UserResponse
