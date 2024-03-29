from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Body
from typing import Union
from app.db import DatabaseManager, get_database
from app.db.model.community import CommunityModel, UpdateCommunityModel
from fastapi.encoders import jsonable_encoder
from fastapi_pagination.ext.motor import paginate
from fastapi_pagination import Params


class CommunityManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_communities(self, owners: [str], member: str, name: str, blocked: bool,
                              size: int = 50, page: int = 0):
        owners = list(filter(lambda o: o is not None, owners))
        query = {"$and": []}
        if owners is not None and len(owners) > 0:
            query["$and"].append({"owner": {"$in": owners}})
        if member is not None:
            query["$and"].append({"users": member})
        if name is not None:
            query["$and"].append({"$or": [
                {"name": name},
                {"name": name.title()},
                {"name": name.lower()},
                {"name": {"$regex": name.title(), "$options": "i"}},
                {"name": {"$regex": name.lower(), "$options": "i"}}
            ]})
        if blocked is not None:
            query["$and"].append({"is_blocked": blocked})

        if len(query["$and"]) == 0:
            query = {}

        data = await paginate(self.db["communities"], query, Params(size=size, page=page))
        return data

    async def get_by_id(self, id: str):
        comm = await self.db["communities"].find_one({"_id": id})
        comm_model = CommunityModel(**comm)
        return comm_model

    async def add_new(self, community: CommunityModel = Body(...)):
        new = jsonable_encoder(community)
        await self.db["communities"].insert_one(new)
        return new

    async def update(self, id: str, community: UpdateCommunityModel = Body(...)):
        community = {k: v for k, v in community.dict().items() if v is not None}
        await self.db["communities"].update_one({"_id": id}, {"$set": community})
        model = await self.get_by_id(id)
        return model

    async def get_by_owner(self, owner_id: str):
        comms = await self.db["communities"].find({"owner": owner_id}).to_list(5000)
        return comms

    async def get_by_member(self, user_id: str):
        comms = await self.db["communities"].find({"users": user_id}).to_list(5000)
        return comms

    async def get_by_name(self, name: str):
        query = {}
        query["$or"] = [
            {"name": name},
            {"name": name.title()},
            {"name": name.lower()},
            {"name": {"$regex": name.title(), "$options": "i"}},
            {"name": {"$regex": name.lower(), "$options": "i"}}
        ]
        comm = await self.db["communities"].find(query).to_list(5000)
        return comm

    async def get_blocked(self, blocked: bool):
        comm = await self.db["communities"].find({"is_blocked": blocked}).to_list(5000)
        return comm

    async def get_community_by_id(self, community_id: str):
        comm = await self.db["communities"].find_one({"_id": community_id})
        return comm

    async def join_community(self, community_id: str, user_id: str):
        await self.db["communities"]. \
            update_one({"_id": community_id}, {"$push": {"users": user_id}})
        model = await self.get_community_by_id(community_id)
        return model


instance: Union[CommunityManager, None] = None


async def GetCommunityManager():
    global instance
    if instance is None:
        db: DatabaseManager = await get_database()
        instance = CommunityManager(db.db)

    return instance
