from pydantic.main import BaseModel
from typing import List
from app.db.model.my_sticker import MyStickerModel
from app.adapters.dtos.sticker_complete import StickerCompleteResponse


class UserResponse(BaseModel):
    id: str
    mail: str
    stickers: List[MyStickerModel]
