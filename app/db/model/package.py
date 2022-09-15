from pydantic.main import BaseModel
from typing import List
from app.db.model.sticker import StickerModel


class MyStickerModel(BaseModel):
    user_id: str
    stickers: List[StickerModel]

    def __getitem__(self, item):
        return getattr(self, item)
