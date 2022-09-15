import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Body

from app.db.model import sticker
from app.db.model.user import PackageModel
from app.db.model.sticker import StickerModel
from fastapi.encoders import jsonable_encoder


class StickerManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_by_id(self, id: str):
        user = await self.db["stickers"].find_one({"_id": id})
        return user

    async def add_new(self, user: StickerModel = Body(...)):
        new = jsonable_encoder(sticker)
        await self.db["stickers"].insert_one(new)
        return new

    async def create_package(self, user_id: str):
        # logica
        # ver cuantos paquetes abrio el usario
        # Obtener 5 figuritas con determinados atributos
        return None