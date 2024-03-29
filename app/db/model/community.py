from app.db.model.py_object_id import PyObjectId
from pydantic import Field

from pydantic.main import BaseModel
from typing import List, Optional
from bson import ObjectId


class CommunityModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    owner: str = Field(...)
    users: List[str] = []
    password: str = "password"
    description: str = ""
    is_blocked: bool = False

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "name",
                "owner": "name",
                "password": "password",
                "description": "description",
                "users": [],
                "is_blocked": False
            }
        }


class UpdateCommunityModel(BaseModel):
    name: Optional[str]
    owner: Optional[str]
    password: Optional[str]
    description: Optional[str]
    users: Optional[List[str]]
    is_blocked: Optional[bool]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "name",
                "owner": "name",
                "password": "password",
                "description": "description",
                "users": [],
                "is_blocked": False
            }
        }
