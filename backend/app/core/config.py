from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    MAIL_MAILER: str
    MAIL_HOST: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_ENCRYPTION: str
    MAIL_FROM_ADDRESS: str
    MAIL_FROM_NAME: str = "HarasSystem"
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
