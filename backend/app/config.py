from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "postgresql+psycopg2://labseq:labseq@localhost:5434/labseq"
    seed_on_empty: bool = True


settings = Settings()
