from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    redis_host: str = Field("127.0.0.1", env="REDIS_HOST")
    redis_port: str = Field("6379", env="REDIS_PORT")
    es_host: str = Field("127.0.0.1", env="ELASTIC_HOST")
    es_port: str = Field("9200", env="ELASTIC_PORT")
    es_url: str = Field("http://127.0.0.1", env="ELASTIC_URL")
    base_api: str = Field("http://127.0.0.1:8000/api/v1", env="BASE_API")
