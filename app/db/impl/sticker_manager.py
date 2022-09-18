from fastapi import Body
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.model.package import PackageModel
from app.db.model.package_counter import PackageCounterModel
from app.db.model.sticker import StickerModel


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

    async def create_package(self):

        package_counter = await self.db["package-counter"].find_one()
        package_counter_model = PackageCounterModel(**package_counter)
        package_amount = package_counter_model.counter

        if (package_amount % 11 != 0) or (package_amount == 0):
            stickers_in_package = await self.db["stickers"].find({"weight": {"$gte": 1, "$lte": 3}}).to_list(5)
        else:
            difficult_sticker = await self.db["stickers"].find({"weight": 5}).to_list(1)
            easy_stickers = await self.db["stickers"].find({"weight": 1}).to_list(2)
            medium_stickers = await self.db["stickers"].find({"weight": {"$gte": 2, "$lte": 4}}).to_list(2)
            stickers_in_package = difficult_sticker + easy_stickers + medium_stickers

        package = PackageModel(stickers=stickers_in_package)
        await self.db["package-counter"].update_one({}, {"$inc": {"counter": 1}})
        return package
