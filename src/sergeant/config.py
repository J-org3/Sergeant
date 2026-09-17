from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Telegram
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    telegram_webhook_secret: str = Field(..., alias="TELEGRAM_WEBHOOK_SECRET")
    telegram_webhook_path: str = Field("/telegram/webhook", alias="TELEGRAM_WEBHOOK_PATH")
    public_webhook_url: str = Field(..., alias="PUBLIC_WEBHOOK_URL")

    allowed_telegram_user_ids_raw: str = Field("", alias="ALLOWED_TELEGRAM_USER_IDS")

    # App
    app_host: str = Field("0.0.0.0", alias="APP_HOST")
    app_port: int = Field(8000, alias="APP_PORT")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    sergeant_env: str = Field("production", alias="sergeant_env")

    # Model routing
    model_primary: str = Field("azure", alias="MODEL_PRIMARY")
    model_fallback: str = Field("ollama", alias="MODEL_FALLBACK")

    # Azure OpenAI
    azure_openai_endpoint: str = Field("", alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field("", alias="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field("2024-10-21", alias="AZURE_OPENAI_API_VERSION")
    azure_openai_deployment: str = Field("", alias="AZURE_OPENAI_DEPLOYMENT")

    # Ollama
    ollama_base_url: str = Field("http://127.0.0.1:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field("llama3.1:8b", alias="OLLAMA_MODEL")

    # OSINT / recon
    shodan_api_key: str = Field("", alias="SHODAN_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def telegram_api_base(self) -> str:
        return f"https://api.telegram.org/bot{self.telegram_bot_token}"

    @property
    def allowed_telegram_user_ids(self) -> set[int]:
        raw = self.allowed_telegram_user_ids_raw.strip()
        if not raw:
            return set()

        result: set[int] = set()
        for item in raw.split(","):
            item = item.strip()
            if item:
                result.add(int(item))
        return result

    @property
    def azure_configured(self) -> bool:
        return bool(
            self.azure_openai_endpoint
            and self.azure_openai_api_key
            and self.azure_openai_deployment
        )

    @property
    def shodan_configured(self) -> bool:
        return bool(self.shodan_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
