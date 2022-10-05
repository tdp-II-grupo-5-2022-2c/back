import logging

from fastapi import Body
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.model.package import PackageModel
from app.db.model.package_counter import PackageCounterModel
from app.db.model.sticker import StickerModel
from typing import List


class StickerManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_by_id(self, id: str):
        sticker = await self.db["stickers"].find_one({"_id": id})
        return sticker

    async def get_all(self):
        stickers = await self.db["stickers"].find().to_list(100)
        return stickers

    async def create_sticker(self, sticker: StickerModel = Body(...)):
        new = jsonable_encoder(sticker)
        await self.db["stickers"].insert_one(new)
        return new

    async def create_package(self):
        try:
            package_counter = await self.db["package-counter"].find_one()
            package_counter_model = PackageCounterModel(**package_counter)
            package_amount = package_counter_model.counter

            if (package_amount % 11 != 0) or (package_amount == 0):
                stickers_in_package = await self.db["stickers"].find({
                    "weight": {"$gte": 1, "$lte": 3}
                }).to_list(5)

                i = 4
                while len(stickers_in_package) < 5 and i < 6:
                    stickers_in_package = await self.db["stickers"].find(
                        {"weight": {"$gte": 1, "$lte": i}}
                    ).to_list(5)
                    i += 1

                if len(stickers_in_package) < 5:
                    raise Exception("No stickers at the moment to create a package")
            else:
                difficult_sticker = await self.db["stickers"].find(
                    {"weight": 5}
                ).to_list(1)
                i = 4
                while len(difficult_sticker) == 0 and i > 0:
                    difficult_sticker = await self.db["stickers"].find(
                        {"weight": i}
                    ).to_list(1)
                    i -= 1
                if len(difficult_sticker) < 1:
                    raise Exception("No stickers at the moment to create a package")

                easy_stickers = await self.db["stickers"].find({"weight": 1}).to_list(2)
                i = 2
                while len(easy_stickers) < 2 and i < 6:
                    easy_stickers = await self.db["stickers"].find(
                        {"weight": i}
                    ).to_list(2)
                    i += 1
                if len(easy_stickers) < 2:
                    raise Exception("No stickers at the moment to create a package")

                medium_stickers = await self.db["stickers"].find({
                    "weight": {"$gte": 2, "$lte": 4}
                }).to_list(2)
                if len(medium_stickers) < 2:
                    medium_stickers = await self.db["stickers"].find({
                        "weight": {"$gte": 1, "$lte": 4}
                    }).to_list(2)
                if len(medium_stickers) < 2:
                    medium_stickers = await self.db["stickers"].find({
                        "weight": {"$gte": 1, "$lte": 5}
                    }).to_list(2)
                if len(medium_stickers) < 2:
                    raise Exception("No stickers at the moment to create a package")

                stickers_in_package = difficult_sticker + \
                    easy_stickers + \
                    medium_stickers

            package = PackageModel(stickers=stickers_in_package)
            await self.db["package-counter"].update_one({}, {"$inc": {"counter": 1}})
            return package

        except Exception as e:
            msg = f"[OPEN_PACKAGE] error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)

    async def find_by_query(
            self,
            ids: List[str],
            country: str = None,
            name: str = None
    ):
        query = {"_id": {"$in": ids}}
        if country is not None:
            query["country"] = country
        if name is not None:
            query["$or"] = [
                {"name": name.title()},
                {"name": {"$regex": name.title()}}
            ]
        stickers = await self.db["stickers"].find(query).to_list(100000)
        return stickers
