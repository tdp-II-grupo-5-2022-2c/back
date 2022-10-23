import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Body, HTTPException

from app.adapters.dtos.sticker_details import StickerDetailResponse
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
        if user != None:
            return UserModel(**user)
        return None

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

    async def get_stickers(self, id: str, is_on_album: bool = None):
        try:
            if is_on_album is not None:
                pipeline = [
                    {"$match": {
                        "_id": id,
                        "stickers.is_on_album": is_on_album
                    }},
                    {"$addFields": {
                        "stickers": {
                            "$filter": {
                                "input": "$stickers",
                                "cond": {
                                    "$eq": ["$$this.is_on_album", is_on_album]
                                }
                            }
                        }
                    }}
                ]
                logging.info(pipeline)
                async for user in self.db["users"].aggregate(pipeline):
                    user_model = UserModel(**user)
                    return user_model.stickers
            else:
                user_model = await self.get_by_id(id)
                return user_model.stickers
        except Exception as e:
            msg = f"[GET STICKERS] id: {id} error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)

    async def paste_sticker(self, user_id: str, sticker_id: str):
        model = await self.get_by_id(user_id)
        for s in model.stickers:
            if s.id == sticker_id:
                if s.is_on_album:
                    raise HTTPException(status_code=400, detail=f"Sticker {s.id} is already pasted")
                if s.quantity <= 0:
                    msg = f"Sticker quantity for {s.id} is {s.quantity}"
                    raise HTTPException(status_code=400, detail=msg)
                s.is_on_album = True
                s.quantity -= 1
        await self.db["users"].update_one(
            {"_id": user_id},
            {"$set": model.dict()},
            upsert=False
        )

        user = await self.get_by_id(user_id)
        return user

    async def open_package(
        self, user_id: str, package: PackageModel
    ):
        try:
            model = await self.get_by_id(user_id)
            stickers_response = []
            for sticker in package.stickers:
                sticker_id = str(sticker.id)
                on_my_list = await self.update_sticker(user_id, sticker_id)
                if not on_my_list:
                    await self.add_new_sticker(user_id, sticker_id)
                # el modelo del comienzo esta desactualizado, porque en
                # la linea anterior se
                # inserto un nuevo sticker a la lista que nunca va a encontrar
                model = await self.get_by_id(user_id)
                iterator_stickers = iter(model.stickers)
                sticker_user = next(
                    s for s in iterator_stickers if str(s.id) == str(sticker.id)
                )
                sticker_detail = self.create_detail_stickers(sticker, sticker_user)
                stickers_response.append(sticker_detail)
            return stickers_response
        except Exception as e:
            msg = f"[OPEN PACKAGE] id: {user_id} error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)

    def create_detail_stickers(self, sticker, sticker_user):
        sticker_detail = StickerDetailResponse(
            id=str(sticker.id),
            image=sticker.image,
            name=sticker.name,
            quantity=sticker_user.quantity,
            number=sticker.number,
            is_on_album=sticker_user.is_on_album,
            country=sticker.country
        )
        return sticker_detail

    async def update_sticker(self, user_id: str, sticker_id: str):
        """
            If sticker already in user list then increment quantity
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
            msg = f"[UPDATE STICKER] id: {user_id} error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)

    async def add_new_sticker(self, user_id: str, sticker_id: str):
        """
            If sticker is not in user list then create MySticker
        """
        try:
            my_sticker = MyStickerModel(
                id=sticker_id,
                quantity=1,
                is_on_album=False
            )
            new = {k: v for k, v in my_sticker.dict().items() if v is not None}
            await self.db["users"].update_one(
                    {"_id": user_id},
                    {"$push": {"stickers": new}}
                )
        except Exception as e:
            msg = f"[ADD NEW STICKER] id: {user_id} error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)