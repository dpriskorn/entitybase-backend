from pydantic import BaseModel

from models.infrastructure.config import Config


class VitessConfig(Config):
    host: str
    port: int
    database: str
    user: str = "root"
    password: str = ""


class HistoryRecord(BaseModel):
    revision_id: int
    created_at: str
    is_mass_edit: bool = False
