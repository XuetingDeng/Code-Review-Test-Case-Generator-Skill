from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    database_url: str = "sqlite:///./code_review_skill.db"
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-plus"
    llm_timeout_seconds: int = 30
    llm_max_retries: int = 1
    log_code_in_dev: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
