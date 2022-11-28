from pydantic.main import BaseModel
from datetime import datetime, timezone, timedelta


class AlbumCompletionReport(BaseModel):
    report_date: str = (datetime.now(timezone.utc) - timedelta(hours=3))\
        .strftime('%d-%m-%Y')
    p20: int = 0
    p40: int = 0
    p60: int = 0
    p80: int = 0
    p100: int = 0
