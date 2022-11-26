from pydantic.main import BaseModel
from typing import List


class UserNameResponse(BaseModel):
    id: str
    name: str
    lastname: str
    mail: str


class CommunityDetailResponse(BaseModel):
    id: str
    name: str
    owner: str
    users: List[UserNameResponse]
    password: str
    description: str
    
