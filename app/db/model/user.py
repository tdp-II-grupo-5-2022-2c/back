from app.db.model.py_object_id import PyObjectId
from pydantic import Field

from pydantic.main import BaseModel
from typing import List, Optional
from bson import ObjectId
from app.db.model.my_sticker import MyStickerModel
from datetime import datetime, timezone, timedelta


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
    package_counter: int = 0
    stickers_collected: int = 0
    album_completion_pct: float = 0
    exchanges_amount: int = 0
    has_daily_packages_available: bool = True
    fcmToken: str = ""
    register_date: str = (datetime.now(timezone.utc) - timedelta(hours=3))\
        .strftime('%Y-%m-%d')
    is_admin: bool = False

    def isProfileComplete(self) -> bool:
        if self.mail == "" or self.name == ""\
                or self.lastname == "" or self.date_of_birth == ""\
                or self.country == "" or len(self.favorite_countries) == 0:
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
                "register_date": "2022-11-11"
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
    package_counter: Optional[int]
    fcmToken: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "mail": "user@mail",
                "stickers": [],
            }
        }
