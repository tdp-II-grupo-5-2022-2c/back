import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Body
from app.db.model.user import UserModel, UpdateUserModel
from app.db.model.package import PackageModel
from app.db.model.my_sticker import MyStickerModel
from fastapi.encoders import jsonable_encoder


class UserManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_all(self):
        users = await self.db["users"].find().to_list(20)
        return users

    async def get_by_id(self, id: str):
        user = await self.db["users"].find_one({"_id": id})
        return UserModel(**user)

    async def get_user_by_mail(self, mail: str):
        user = await self.db["users"].find_one({"mail": mail})
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

    async def get_stickers(self, id: str):
        try:
            user = await self.db["users"].find_one({"_id": id})
            user_model = UserModel(**user)
            return user_model.stickers
        except Exception as e:
            msg = f"[GET_STICKERS_FROM_USER] id: {id} error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)

    async def paste_sticker(self, user_id: str, sticker_id: str):
        try:
            await self.db["users"].update_one(
                {"_id": user_id, "stickers.id": sticker_id},
                {
                    "$set": {"stickers.$.is_on_album": True},
                    "$inc": {"stickers.$.quantity": -1}
                },
                upsert=False
            )
            model = await self.get_by_id(user_id)
            return model
        except Exception as e:
            msg = f"[PASTE STICKER] id: {user_id} error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)

    async def open_package(
        self, user_id: str, package: PackageModel
    ):
        try:
            for sticker in package.stickers:
                if not self.update_sticker(user_id, sticker.id):
                    self.add_new_sticker(user_id, sticker.id)
            model = await self.get_by_id(user_id)
            return model
        except Exception as e:
            msg = f"[PASTE STICKER] id: {user_id} error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)

    async def update_sticker(self, user_id: str, sticker_id: str):
        """
            If sticker already in user list
            then increment quantity
        """
        try:
            user = await self.db["users"].find_one(
                {"_id": user_id, "stickers.id": sticker_id}
            )
            if user is not None:
                await self.db["users"].update_one(
                    {"_id": user_id, "stickers.id": sticker_id},
                    {"$inc": {"stickers.$.quantity": 1}},
                    upsert=False
                )
                return True
            return False
        except Exception as e:
            msg = f"[PASTE STICKER] id: {user_id} error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)

    async def add_new_sticker(self, user_id: str, sticker_id: str):
        """
            If sticker is not in user list
            then create MySticker
        """
        try:
            my_sticker = MyStickerModel(
                id=sticker_id,
                quantity=1,
                is_on_album=False
            )
            await self.db["users"].update_one(
                    {"_id": user_id},
                    {"$push": {"stickers": my_sticker}},
                    upsert=False
                )
        except Exception as e:
            msg = f"[PASTE STICKER] id: {user_id} error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)
