from pydantic.main import BaseModel
from datetime import datetime


class AlbumCompletionReport(BaseModel):
    report_date: str = datetime.today().strftime('%Y-%m-%d')
    p20: float = 0
    p40: float = 0
    p60: float = 0
    p80: float = 0
    p100: float = 0
