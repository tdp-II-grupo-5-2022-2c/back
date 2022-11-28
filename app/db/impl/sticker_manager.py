import logging
from random import choice

from fastapi import Body
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Union
from app.db import DatabaseManager, get_database
from app.db.impl.user_manager import TOTAL_STICKERS_ALBUM

from app.db.model.package import PackageModel
from app.db.model.package_counter import PackageCounterModel
from app.db.model.sticker import StickerModel, UpdateStickerModel
from app.db.model.sticker_metrics import StickerMetricsModel
from typing import List, Dict
from fastapi_pagination.ext.motor import paginate
from fastapi_pagination import Params


def get_random_stickers_from_list(sticker_list: List[StickerModel],
                                  amount_of_stickers_desired: int):
    random_sticker_list = []
    amount_of_stickers_to_return = min(amount_of_stickers_desired, len(sticker_list))
    positions_stickers_added = []

    for i in range(amount_of_stickers_to_return):
        random_pos = choice(
            [number for number in range(0, len(sticker_list))
             if number not in positions_stickers_added]
        )
        random_sticker_list.append(sticker_list[random_pos])
        positions_stickers_added.append(random_pos)

    return random_sticker_list


class StickerManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_by_id(self, id: str):
        sticker = await self.db["stickers"].find_one({"_id": id})
        return sticker

    async def get_all(self, size: int = 50, page: int = 0):
        stickers = await paginate(self.db["stickers"], params=Params(size=size, page=page))
        return stickers

    async def create_sticker(self, sticker: StickerModel = Body(...)):
        new = jsonable_encoder(sticker)
        await self.db["stickers"].insert_one(new)
        return new

    async def create_sticker_metrics(self, stickerMetrics: StickerMetricsModel):
        new = jsonable_encoder(stickerMetrics)
        await self.db["stickers_metrics"].insert_one(new)
        return new

    async def get_sticker_metrics_by_sticker_id(
            self,
            sticker_id: str) -> Union[StickerMetricsModel, None]:
        stickerMetric = await self.db["stickers_metrics"]. \
            find_one({"sticker_id": sticker_id})
        if stickerMetric is None:
            return None

        return StickerMetricsModel(**stickerMetric)

    async def get_sticker_metrics_freq(self, top5: bool) -> List[Dict]:
        sort = {'$sort': {'counter': 1}}
        limit = {'$limit': 5}
        merge = {'$lookup': {
            'from': 'stickers',
            'localField': 'sticker_id',
            'foreignField': '_id',
            'as': 'metadata'
        }}
        unwind = {'$unwind': {'path': '$metadata'}}
        project = {'$project': {
            '_id': 0,
            'name': '$metadata.name',
            'country': '$metadata.country',
            'counter': 1
        }}

        pipeline = [sort]
        if top5 is True:
            pipeline = [*pipeline, limit]

        pipeline = [*pipeline, merge, unwind, project]

        return await self.db["stickers_metrics"]. \
            aggregate(pipeline).to_list(10000)

    async def update_sticker_metrics(self, stickerMetrics: StickerMetricsModel):
        payload = {k: v for k, v in stickerMetrics.dict().items() if v is not None}
        await self.db["stickers_metrics"]. \
            update_one({"sticker_id": stickerMetrics.sticker_id}, {"$set": payload})

    async def update(self, id: str, sticker: UpdateStickerModel = Body(...)):
        sticker = {k: v for k, v in sticker.dict().items() if v is not None}
        await self.db["stickers"].update_one({"_id": id}, {"$set": sticker})
        model = await self.get_by_id(id)
        return model

    async def get_package_counter(self) -> PackageCounterModel:
        package_counter = await self.db["package-counter"].find_one()
        return PackageCounterModel(**package_counter)

    async def create_package(self):
        try:
            package_counter = await self.db["package-counter"].find_one()
            package_counter_model = PackageCounterModel(**package_counter)
            package_amount = package_counter_model.counter

            # We get all the stickers whose weight is between 1 and 3
            stickers_with_weight_1 = await self.db["stickers"].find({"weight": 1}). \
                to_list(TOTAL_STICKERS_ALBUM)
            stickers_with_weight_2 = await self.db["stickers"].find({"weight": 2}). \
                to_list(TOTAL_STICKERS_ALBUM)
            stickers_with_weight_3 = await self.db["stickers"].find({"weight": 3}). \
                to_list(TOTAL_STICKERS_ALBUM)

            # If it is a normal package, we need 5 stickers whose weight is between 1 and 3
            if (package_amount % 11 != 0) or (package_amount == 0):

                # Select 5 random ones stickers whose weight is between 1 and 3
                stickers_in_package = get_random_stickers_from_list(
                    stickers_with_weight_1 +
                    stickers_with_weight_2 +
                    stickers_with_weight_3,
                    5)

                # Some variables that will help us with the amount of stickers check
                next_sticker_weight_to_add = 4
                stickers_remaining = []
                stickers_up_to_now = stickers_in_package

                # If the amount of stickers with weight between 1 and 3 is less than 5,
                # we will be adding stickers with higher weights to the package
                while len(stickers_up_to_now) < 5 and next_sticker_weight_to_add < 6:
                    stickers_remaining = await self.db["stickers"]. \
                        find({"weight": {"$gte": 4, "$lte": next_sticker_weight_to_add}}) \
                        .to_list(TOTAL_STICKERS_ALBUM)
                    stickers_remaining = get_random_stickers_from_list(
                        stickers_remaining,
                        5 - len(stickers_in_package)
                    )
                    next_sticker_weight_to_add += 1
                    stickers_up_to_now = stickers_in_package + stickers_remaining

                stickers_in_package = stickers_in_package + stickers_remaining

                if len(stickers_in_package) < 5:
                    raise Exception("No stickers at the moment to create a package")
            else:
                # If it is a "special package", we need:
                # 1 sticker with weight 5
                # 2 stickers with weight 1
                # 2 stickers with weight between 2 and 4

                # Get the remaining stickers lists that we will use
                stickers_with_weight_4 = await self.db["stickers"].find({"weight": 4}) \
                    .to_list(TOTAL_STICKERS_ALBUM)
                stickers_with_weight_5 = await self.db["stickers"].find({"weight": 5}) \
                    .to_list(TOTAL_STICKERS_ALBUM)

                # Search for a sticker with weight 5
                difficult_sticker = get_random_stickers_from_list(stickers_with_weight_5, 1)

                # Variable that will help with the amount of stickers check
                next_sticker_weight_to_add = 4

                # If there is no sticker with weight 5, we search one with a lower weight
                while len(difficult_sticker) < 1 and next_sticker_weight_to_add > 0:
                    difficult_sticker = await self.db["stickers"].find(
                        {"weight": next_sticker_weight_to_add}) \
                        .to_list(1)
                    next_sticker_weight_to_add -= 1

                if len(difficult_sticker) < 1:
                    raise Exception("No stickers at the moment to create a package")

                # Select two stickers with weight 1
                easy_stickers = get_random_stickers_from_list(stickers_with_weight_1, 2)

                # Variables that will help with the amount of stickers check
                easy_stickers_remaining = []
                easy_stickers_up_to_now = easy_stickers
                next_sticker_weight_to_add = 2

                # If the amount of stickers with weight 1 is less than 2,
                # we search for stickers with higher weight
                while len(easy_stickers_up_to_now) < 2 and next_sticker_weight_to_add < 6:
                    easy_stickers_remaining = await self.db["stickers"].find(
                        {"weight": next_sticker_weight_to_add}) \
                        .to_list(TOTAL_STICKERS_ALBUM)
                    easy_stickers_remaining = get_random_stickers_from_list(
                        easy_stickers_remaining,
                        2 - len(easy_stickers)
                    )
                    next_sticker_weight_to_add += 1
                    easy_stickers_up_to_now = easy_stickers_up_to_now + easy_stickers_remaining

                easy_stickers = easy_stickers + easy_stickers_remaining

                if len(easy_stickers) < 2:
                    raise Exception("No stickers at the moment to create a package")

                # We search for 2 stickers with weight between 2 and 4
                medium_stickers = get_random_stickers_from_list(
                    stickers_with_weight_2 +
                    stickers_with_weight_3 +
                    stickers_with_weight_4,
                    2)

                # If the amount of stickers with weight between 2 and 4 is less than 2,
                # we search for stickers with weight 1
                if len(medium_stickers) < 2:
                    remaining_medium_stickers = get_random_stickers_from_list(
                        stickers_with_weight_1,
                        2 - len(medium_stickers)
                    )
                    medium_stickers = medium_stickers + remaining_medium_stickers

                # If the amount of stickers with weight between 1 and 4 is less than 2,
                # we search for stickers with weight 5
                if len(medium_stickers) < 2:
                    remaining_medium_stickers = get_random_stickers_from_list(
                        stickers_with_weight_5,
                        2 - len(medium_stickers)
                    )
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
                {"name": {"$regex": name.title(), "$options": "i"}}
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
                {"name": {"$regex": name.title(), "$options": "i"}}
            ]
        stickers = await self.db["stickers"].find(query).to_list(100000)
        return stickers


instance: Union[StickerManager, None] = None


async def GetStickerManager():
    global instance
    if instance is None:
        db: DatabaseManager = await get_database()
        instance = StickerManager(db.db)

    return instance
