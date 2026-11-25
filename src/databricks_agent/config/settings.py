from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Required now: Databricks
    databricks_host: str
    databricks_token: str
    databricks_http_path: str
    databricks_catalog: str
    databricks_schema: str
    databricks_llm_endpoint: str

    # Optional later: Neo4j
    neo4j_enabled: bool = False
    neo4j_uri: str | None = None
    neo4j_username: str | None = None
    neo4j_password: str | None = None
    neo4j_database: str = "neo4j"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()