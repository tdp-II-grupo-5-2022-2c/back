from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Union
from app.db import DatabaseManager, get_database
from app.db.model.report import AlbumCompletionReport


class ReportManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def save_album_completion_report(self, report: AlbumCompletionReport):
        await self.db["album_reports"].update_one(
            {"report_date": report.report_date},
            {"$set": report.dict()},
            upsert=True
        )
        return

    async def get_album_completion_report(self, date):
        report = await self.db["album_reports"].find_one({"report_date": date})
        if report is not None:
            model = AlbumCompletionReport(**report)
            return model
        return None


instance: Union[ReportManager, None] = None


async def GetReportManager():
    global instance
    if instance is None:
        db: DatabaseManager = await get_database()
        instance = ReportManager(db.db)

    return instance
