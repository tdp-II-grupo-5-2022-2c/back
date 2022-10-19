import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Body

from app.db.model.community import CommunityModel, UpdateCommunityModel
from fastapi.encoders import jsonable_encoder


class CommunityManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_communities(self, owner: str, member: str):
        if owner is not None:
            data = await self.get_by_owner(owner)
        elif member is not None:
            data = await self.get_by_member(member)
        else:
            data = await self.db["communities"].find().to_list(5000)

        return data

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
        comms = await self.db["communities"].find({"owner": owner_id}).to_list(5000)
        return comms

    async def get_by_member(self, user_id: str):
        comms = await self.db["communities"].find({"users": user_id}).to_list(5000)
        return comms

    async def join_community(self, community_id: str, user_id: str, password=password):
        community = await self.get_by_id(community_id)
        if (community.password == password):
            await self.db["communities"].\
                update_one({"_id": community_id}, {"$push": {"users": user_id}})
            model = await self.get_by_id(community_id)
            return model
        else:
            msg = "Password invalid, user {user_id} can't join community {community_id}"
            logging.error(msg)
            raise RuntimeError(msg)
