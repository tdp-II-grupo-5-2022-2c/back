from app.db.model.py_object_id import PyObjectId
from pydantic import Field

from pydantic.main import BaseModel
from typing import List, Optional
from bson import ObjectId
from app.db.model.my_sticker import MyStickerModel


class UserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    mail: str = Field(...)
    name: str = Field(...)
    lastname: str = Field(...)
    date_of_birth: str = Field(...)
    stickers: List[MyStickerModel] = []
    country: str = ""
    favorite_countries: List[str] = []
    is_profile_complete: bool = False

    def isProfileComplete(self) -> bool:
        if self.mail == "":
            return False
        if self.name == "":
            return False
        if self.lastname == "":
            return False
        if self.date_of_birth == "":
            return False
        if self.country == "":
            return False
        if len(self.favorite_countries) == 0:
            return False

        return True

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "mail": "user@mail",
                "stickers": [],
            }
        }


class UpdateUserModel(BaseModel):
    mail: Optional[str]
    name: Optional[str]
    lastname: Optional[str]
    date_of_birth: Optional[str]
    stickers: Optional[List[MyStickerModel]]
    country: Optional[str]
    favorite_countries: Optional[List[str]]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "mail": "user@mail",
                "stickers": [],
            }
        }
