from pydantic.main import BaseModel


class StickerDetailResponse(BaseModel):
    id: str
    image: str
    name: str
    quantity: int
    country: str
    is_on_album: bool