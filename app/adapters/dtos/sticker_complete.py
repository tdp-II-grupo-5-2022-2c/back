from pydantic.main import BaseModel


class StickerCompleteResponse(BaseModel):
    id: str
    image: str
    name: str
    team: str
    quantity: int
    country: str
    is_on_album: bool
