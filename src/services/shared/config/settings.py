from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    s3_endpoint: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str
    vitess_host: str
    vitess_port: int
    vitess_database: str = "wikibase"
    vitess_user: str = "root"
    vitess_password: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
