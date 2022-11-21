from pydantic.main import BaseModel
from pydantic import Field


class StickerMetricsModel(BaseModel):
    sticker_id: str = Field(...)
    counter: int = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "sticker_id": "sticker1",
                "counter": 3
            }
        }
