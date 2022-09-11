from pydantic.main import BaseModel


class StickerModel(BaseModel):
    id: str
    status: str
    quantity: str

    def __getitem__(self, item):
        return getattr(self, item)
