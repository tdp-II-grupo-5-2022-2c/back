from app.db.model.exchange import ExchangeModel, UpdateExchangeModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Body
from fastapi.encoders import jsonable_encoder


class ExchangeManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_pending_exchanges_by_sender_id(self, sender_id: str):
        pendingExchanges = await self.db["exchanges"].\
            find({"sender_id": sender_id, "completed": False}, {'id': 0}).\
                to_list(10)  # Max amount of exchanges per user is 3
        return pendingExchanges

    async def get_exchange_by_id(self, id: str):
        exchange = await self.db["exchanges"].find_one({"_id": id})
        return ExchangeModel(**exchange)

    async def get_exchange_by_sender_id(self, sender_id: str, completed: bool):
        query = {"sender_id": sender_id}
        if completed is not None:
            query['completed'] = completed

        exchanges = await self.db["exchanges"].find(query, {'id': 0}).to_list(100)
        return exchanges

    async def add_new(self, exchange: ExchangeModel = Body(...)):
        new = jsonable_encoder(exchange)
        await self.db["exchanges"].insert_one(new)
        return new

    async def update(self, id: str, exchange: UpdateExchangeModel = Body(...)):
        exchange = {k: v for k, v in exchange.dict().items() if v is not None}
        await self.db["exchanges"].update_one({"_id": id}, {"$set": exchange})
        model = await self.get_exchange_by_id(id)
        return model

