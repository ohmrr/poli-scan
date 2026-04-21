from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "development"

    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "qwen2.5:14b"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    LLM_PROVIDER: str = "ollama"

    TURSO_DATABASE_URL: str
    TURSO_AUTH_TOKEN: str

    class Config:
        env_file = "server/.env"
        env_file_encoding = "utf-8"


settings = Settings()
