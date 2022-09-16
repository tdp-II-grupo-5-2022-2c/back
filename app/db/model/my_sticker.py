from pydantic.main import BaseModel
from pydantic import Field


class MyStickerModel(BaseModel):
    id: str = Field(...)
    is_on_album: bool = Field(...)
    quantity: int = Field(...)

    def __getitem__(self, item):
        return getattr(self, item)
