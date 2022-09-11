from app.db.model.py_object_id import PyObjectId
from pydantic import Field
from app.db.model.sticker import StickerModel

from pydantic.main import BaseModel
from typing import List, Optional
from bson import ObjectId


class UserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    mail: str = Field(...)
    stickers: List[StickerModel] = []

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "mail": "user@mail",
                "stickers": [],
            }
        }


class UpdateUserModel(BaseModel):
    mail: Optional[str]
    stickers: Optional[List[StickerModel]]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "mail": "user@mail",
                "stickers": [],
            }
        }
