import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Body

from app.db.model.community import CommunityModel, UpdateCommunityModel
from fastapi.encoders import jsonable_encoder


class CommunityManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_all(self, owner_id: str = None, member_id: str = None):
        if owner_id is not None:
            all_data = await self.get_by_owner(owner_id)

        if member_id is not None:
            all_data await self.get_by_member(member_id)
        else:
            all_data = await self.db["communities"].find().to_list(20)

        return all_data

    async def get_by_id(self, id: str):
        comm = await self.db["communities"].find_one({"_id": id})
        return CommunityModel(**comm)

    async def add_new(self, community: CommunityModel = Body(...)):
        new = jsonable_encoder(community)
        await self.db["communities"].insert_one(new)
        return new

    async def update(self, id: str, community: UpdateCommunityModel = Body(...)):
        try:
            community = {k: v for k, v in community.dict().items() if v is not None}
            await self.db["communities"].update_one({"_id": id}, {"$set": community})
            model = await self.get_by_id(id)
            return model
        except Exception as e:
            msg = f"[UPDATE COMMUNITY] id: {id} error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)

    async def get_by_owner(self, owner_id: str):
        comms = await self.db["communities"].find({"owner": owner_id}).to_list(20)
        return comms

    async def get_by_member(self, user_id: str):
        comms = await self.db["communities"].find({"users": {"$in": user_id}}).to_list(20)
        return comms

    async def add_new_member(self, community_id: str, user_id: str):
        await self.db["communities"].update_one({"_id": community_id}, {"$push": {"users": user_id}})
        model = await self.get_by_id(community_id)
        return model
