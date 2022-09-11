import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Body

from app.db.model.user_sticker import UserStickerModel, UpdateUserStickerModel
from fastapi.encoders import jsonable_encoder


class UserStickerManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_by_user_id(self, user_id: str):
        sticker = await self.db["user_stickers"].find_one({"user_id": id})
        return sticker

    async def get_by_id(self, id: str):
        sticker = await self.db["user_stickers"].find_one({"_id": id})
        return sticker

    async def add_new(self, sticker: UserStickerModel = Body(...)):
        new = jsonable_encoder(sticker)
        await self.db["user_stickers"].insert_one(new)
        return new

    async def update(self, id: str, sticker: UpdateUserStickerModel = Body(...)):
        try:
            sticker = {k: v for k, v in sticker.dict().items() if v is not None}
            await self.db["user_stickers"].update_one({"_id": id}, {"$set": sticker})
            model = await self.get_by_user_id(id)
            return model
        except Exception as e:
            msg = f"[UPDATE_STICKER] id: {id} error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)
