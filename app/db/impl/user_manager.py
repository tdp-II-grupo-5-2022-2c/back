import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Body

from app.db.model.user import UserModel, UpdateUserModel
from fastapi.encoders import jsonable_encoder


class UserManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_by_id(self, id: str):
        user = await self.db["users"].find_one({"_id": id})
        return UserModel(**user)

    async def add_new(self, user: UserModel = Body(...)):
        new = jsonable_encoder(user)
        await self.db["users"].insert_one(new)
        return new

    async def update(self, id: str, user: UpdateUserModel = Body(...)):
        try:
            user = {k: v for k, v in user.dict().items() if v is not None}
            await self.db["users"].update_one({"_id": id}, {"$set": user})
            model = await self.get_by_id(id)
            return model
        except Exception as e:
            msg = f"[UPDATE_USER] id: {id} error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)

    async def paste_sticker(self, user_id: str, sticker_id: str):
        try:
            await self.db["users"].update_one(
                {"_id": user_id, "stickers.id": sticker_id},
                {"$set": 
                    {"stickers.is_in_album": True}
                }
            )
            model = await self.get_by_id(user_id)
            return model
        except Exception as e:
            msg = f"[UPDATE_USER] id: {user_id} error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)
