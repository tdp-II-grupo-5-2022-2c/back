from pydantic.main import BaseModel


class StickerModel(BaseModel):
    id: str
    isOnAlbum: bool
    isRepeated: bool
    quantity: str

    def __getitem__(self, item):
        return getattr(self, item)
