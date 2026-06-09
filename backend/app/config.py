import json
from typing import Any, List, Union
from pydantic import AnyHttpUrl, BeforeValidator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


def parse_cors_origins(v: Any) -> List[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        try:
            if isinstance(v, str):
                return json.loads(v)
            return v
        except Exception:
            raise ValueError(f"Could not parse CORS origins: {v}")
    raise ValueError(v)


class Settings(BaseSettings):
    """
    Application Settings validated via Pydantic.
    Environment variables are automatically mapped and parsed.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Core Settings
    PROJECT_NAME: str = "AI Finance Operations Platform"
    ENVIRONMENT: str = "development"

    # API Settings
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    BACKEND_CORS_ORIGINS: Annotated[
        List[str], BeforeValidator(parse_cors_origins)
    ] = ["http://localhost:3000"]

    # PostgreSQL Database Settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres_password"
    POSTGRES_DB: str = "finance_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    
    # Constructed or overridden database URL (supports asyncpg by default)
    DATABASE_URL: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str, values: Any) -> str:
        if v:
            return v
        
        # Access elements dynamically from validation data
        data = values.data
        user = data.get("POSTGRES_USER")
        password = data.get("POSTGRES_PASSWORD")
        host = data.get("POSTGRES_HOST")
        port = data.get("POSTGRES_PORT")
        db = data.get("POSTGRES_DB")
        
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

    # Vector DB (Chroma) Settings
    CHROMA_HOST: str = "chroma"
    CHROMA_PORT: int = 8000

    # Redis Task Queue Broker Settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # S3 / Object Storage Settings
    S3_ENDPOINT_URL: str = ""  # If using MinIO locally, e.g. "http://localhost:9000"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "finance-documents"

    # OpenAI API Settings
    OPENAI_API_KEY: str = ""


# Instantiated settings object
settings = Settings()
