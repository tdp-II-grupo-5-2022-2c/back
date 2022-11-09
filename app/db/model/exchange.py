from app.db.model.py_object_id import PyObjectId
from pydantic import Field

from pydantic.main import BaseModel
from typing import List, Optional
from bson import ObjectId


ACCEPT_ACTION = 'accept'
REJECT_ACTION = 'reject'
AVAILABLE_EXCHANGE_ACTIONS = [ACCEPT_ACTION, REJECT_ACTION]


class ExchangeModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    sender_id: str = Field(...)  # user_id
    stickers_to_give: List[str] = [],
    stickers_to_receive: List[str] = [],
    blacklist_user_ids: List[str] = []
    completed: bool = False

    def __getitem__(self, item):
        return getattr(self, item)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "user_id": "user1",
                "stickers_to_give": ["s1", "s2"],
                "stickers_to_receive": ["s3", "s4"],
                "blacklist_user_ids": [],
                "completed": False
            }
        }


class ExchangeActionModel(BaseModel):
    action: str = Field(...)
    receiver_id: str = Field(...)  # user_id who could potentially receive the exchange

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "action": "accept",
                "receiver_id": "user_id"
            }
        }


class UpdateExchangeModel(BaseModel):
    completed: Optional[bool]
    blacklist_user_ids: Optional[List[str]]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "blacklist_user_ids": [],
                "completed": False
            }
        }
