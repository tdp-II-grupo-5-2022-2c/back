from pydantic.main import BaseModel
from typing import List
from app.db.model.sticker import StickerModel
from bson import ObjectId


class PackageModel(BaseModel):
    stickers: List[StickerModel]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "stickers": []
            }
        }

    def __getitem__(self, item):
        return getattr(self, item)
