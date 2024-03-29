from pydantic.main import BaseModel
from app.db.model.py_object_id import PyObjectId
from typing import Optional
from pydantic import Field
from bson import ObjectId
import datetime

# The weight measures how likely is the sticker to appear in a package.
# It goes from 1 to 5 being:
# 1 - Most likely
# 5 - Unlikely


class StickerModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    number: int = Field(...)
    date_of_birth: datetime.date = Field(...)
    height: float = Field(...)
    position: str = Field(...)
    country: str = Field(...)
    image: str = Field(...)
    weight: int = 1

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "id": "..",
                "name": "Lionel Messi",
                "number": 10,  # Posicion en el album (posicion del 0 al 11)
                "dateOfBirth": "1985-02-02",
                "height": "170",
                "position": "CF",
                "country": "Argentina",
                "image": "https://picsum.photos/300/200",
                "weight": 5,
            }
        }

    def __getitem__(self, item):
        return getattr(self, item)


class UpdateStickerModel(BaseModel):
    name: Optional[str]
    weight: Optional[int]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "weight": 5,
            }
        }

    def __getitem__(self, item):
        return getattr(self, item)
