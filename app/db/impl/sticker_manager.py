import logging

from fastapi import Body
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.model.package import PackageModel
from app.db.model.package_counter import PackageCounterModel
from app.db.model.sticker import StickerModel, UpdateStickerModel
from app.db.model.sticker_metrics import StickerMetricsModel
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

    async def create_sticker_metrics(self, stickerMetrics: StickerMetricsModel):
        new = jsonable_encoder(stickerMetrics)
        await self.db["stickers_metrics"].insert_one(new)
        return new

    async def update(self, id: str, sticker: UpdateStickerModel = Body(...)):
        sticker = {k: v for k, v in sticker.dict().items() if v is not None}
        await self.db["stickers"].update_one({"_id": id}, {"$set": sticker})
        model = await self.get_by_id(id)
        return model

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
                stickers_remaining = []
                stickers_up_to_now = stickers_in_package
                while len(stickers_up_to_now) < 5 and i < 6:
                    stickers_remaining = await self.db["stickers"].\
                        find({"weight": {"$gte": 4, "$lte": i}}) \
                        .to_list(5 - len(stickers_in_package))
                    i += 1
                    stickers_up_to_now = stickers_in_package + stickers_remaining

                stickers_in_package = stickers_in_package + stickers_remaining

                if len(stickers_in_package) < 5:
                    raise Exception("No stickers at the moment to create a package")
            else:
                difficult_sticker = await self.db["stickers"].find({"weight": 5}).to_list(1)
                i = 4
                while len(difficult_sticker) < 1 and i > 0:
                    difficult_sticker = await self.db["stickers"].find({"weight": i}).to_list(1)
                    i -= 1
                if len(difficult_sticker) < 1:
                    raise Exception("No stickers at the moment to create a package")

                easy_stickers = await self.db["stickers"].find({"weight": 1}).to_list(2)
                easy_stickers_remaining = []
                easy_stickers_up_to_now = easy_stickers
                i = 2
                while len(easy_stickers_up_to_now) < 2 and i < 6:
                    easy_stickers_remaining = await self.db["stickers"].find({"weight": i}) \
                        .to_list(2 - len(easy_stickers))
                    i += 1
                    easy_stickers_up_to_now = easy_stickers_up_to_now + easy_stickers_remaining

                easy_stickers = easy_stickers + easy_stickers_remaining

                if len(easy_stickers) < 2:
                    raise Exception("No stickers at the moment to create a package")

                medium_stickers = await self.db["stickers"].find({
                    "weight": {"$gte": 2, "$lte": 4}
                }).to_list(2)
                if len(medium_stickers) < 2:
                    remaining_medium_stickers = await self.db["stickers"].find({
                        "weight": 1
                    }).to_list(2 - len(medium_stickers))
                    medium_stickers = medium_stickers + remaining_medium_stickers
                if len(medium_stickers) < 2:
                    remaining_medium_stickers = await self.db["stickers"].find({
                        "weight": 5
                    }).to_list(2 - len(medium_stickers))
                    medium_stickers = medium_stickers + remaining_medium_stickers
                if len(medium_stickers) < 2:
                    raise Exception("No stickers at the moment to create a package")

                stickers_in_package = difficult_sticker + easy_stickers + medium_stickers

                # Check for duplicates
                id_list = []
                for sticker in stickers_in_package:
                    if sticker['_id'] not in id_list:
                        id_list.append(sticker['_id'])
                if len(id_list) < 5:
                    raise Exception("No stickers at the moment to create a package")

            package = PackageModel(stickers=stickers_in_package)
            await self.db["package-counter"].update_one({}, {"$inc": {"counter": 1}})
            return package

        except Exception as e:
            msg = f"[OPEN_PACKAGE] error: {e}"
            logging.error(msg)
            raise RuntimeError(msg)

    async def find_by_name(self, name: str):
        query = {}
        if name is not None:
            query["$or"] = [
                {"name": name.title()},
                {"name": {"$regex": name.title()}}
            ]
        stickers = await self.db["stickers"].find(query).to_list(100000)
        return stickers

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
