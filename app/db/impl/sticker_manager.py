# import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Body

from app.db.model.user import PackageModel
from app.db.model.sticker import StickerModel
from fastapi.encoders import jsonable_encoder


class StickerManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_by_id(self, id: str):
        sticker = await self.db["stickers"].find_one({"_id": id})
        return sticker

    async def create_sticker(self, sticker: StickerModel = Body(...)):
        new = jsonable_encoder(sticker)
        await self.db["stickers"].insert_one(new)
        return new

    async def create_package(self, user_id: str):
        # Agregar logica
        # ver cuantos paquetes abrio el usario
        # Obtener 5 figuritas con determinados atributos
        easy_sticker = await self.db["stickers"].find({"type": "easy"}).to_list(3)
        rare_sticker = await self.db["stickers"].find({"type": "rare"}).to_list(1)

        stickers_in_package = easy_sticker + rare_sticker
        package = PackageModel(user_id=user_id, stickers=stickers_in_package)
        return package
