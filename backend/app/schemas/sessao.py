from pydantic import BaseModel

class SessaoRefreshTokenRequest(BaseModel):
    refresh_token: str

