from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/docint"
    REDIS_URL: str = "redis://localhost:6379/0"
    ENVIRONMENT: str = "development"
    
    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""
    # Usually we can construct JWKS URL from the publishable key or a specific issuer URL
    CLERK_ISSUER_URL: str = ""
    
    # MinIO / S3 config
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "docint-pdfs"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
