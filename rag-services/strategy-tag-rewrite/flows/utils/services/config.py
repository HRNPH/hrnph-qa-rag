import os
from typing import Optional
from pydantic import Field, ValidationError, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # ChromaDB Settings
    chromadb_host: str = Field(..., env="CHROMADB_HOST")
    chromadb_cf_access_client_id: str = Field(..., env="CHROMADB_CF_ACCESS_CLIENT_ID")
    chromadb_cf_access_client_secret: str = Field(
        ..., env="CHROMADB_CF_ACCESS_CLIENT_SECRET"
    )
    chromadb_auth_token: str = Field(..., env="CHROMADB_AUTH_TOKEN")
    target_collection_name: str = Field(..., env="TARGET_COLLECTION_NAME")

    # AI Services Settings
    openai_model: str = Field(..., env="OPENAI_MODEL")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_base_url: Optional[str] = Field(None, env="OPENAI_BASE_URL")
    openai_websocket_base_url: Optional[str] = Field(
        None, env="OPENAI_WEBSOCKET_BASE_URL"
    )

    # Promptflow Settings
    pf_disable_tracing: bool = Field(..., env="PF_DISABLE_TRACING")


SETTING = Settings()
