from pydantic.main import BaseModel
from app.db.model.py_object_id import PyObjectId
from pydantic import Field


class StickerModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    image: str = Field(...)
    type: str = Field(...)

    def __getitem__(self, item):
        return getattr(self, item)
