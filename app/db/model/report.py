import datetime
from pydantic.main import BaseModel
from pydantic import Field


class AlbumCompletionReport(BaseModel):
    date: datetime.date = Field(...)
    p20: float = 0
    p40: float = 0
    p60: float = 0
    p80: float = 0
    p100: float = 0
