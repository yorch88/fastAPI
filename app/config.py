from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ELASTICSEARCH_HOST: str = "http://elasticsearch:9200"

    class Config:
        env_file = ".env"

settings = Settings()