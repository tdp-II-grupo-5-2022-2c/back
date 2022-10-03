from pydantic.main import BaseModel


class StickerDetailResponse(BaseModel):
    id: str
    image: str
    name: str
    number: int
    quantity: int
    country: str
    is_on_album: bool
