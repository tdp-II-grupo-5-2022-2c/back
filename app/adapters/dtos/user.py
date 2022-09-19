from pydantic.main import BaseModel
from typing import List
from app.db.model.my_sticker import MyStickerModel


class UserResponse(BaseModel):
    id: str
    mail: str
    stickers: List[MyStickerModel]
