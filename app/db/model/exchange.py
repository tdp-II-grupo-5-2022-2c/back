from app.db.model.py_object_id import PyObjectId
from pydantic import Field

from pydantic.main import BaseModel
from typing import List, Optional
from bson import ObjectId
from app.db.model.my_sticker import MyStickerModel


class ExchangeModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    sender_id: str = Field(...)
    community_id: str = Field(...)
    stickers_to_give: List[str] = Field(...),
    stickers_to_receive: List[str] = Field(...),
    blacklist_user_ids: List[str] = []
    completed: bool = False

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "user_id": "user1",
                "community_id": "community",
                "stickers_to_give": ["s1", "s2"],
                "stickers_to_receive": ["s3", "s4"], 
                "blacklist_user_ids": [],            
                "completed": False 
            }
        }


# class UpdateCommunityModel(BaseModel):
#     name: Optional[str]
#     owner: Optional[str]
#     users: Optional[List[str]]

#     class Config:
#         arbitrary_types_allowed = True
#         json_encoders = {ObjectId: str}
#         schema_extra = {
#             "example": {
#                 "name": "name",
#                 "owner": "name",
#                 "users": [],
#             }
#         }
