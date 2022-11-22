from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from typing import Union
from app.db import DatabaseManager, get_database
from app.db.model.report import AlbumCompletionReport
from app.db.model.user import UserModel


class ReportManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_album_completion_report(self, users: List[UserModel]):
        report = AlbumCompletionReport()

        for user in users:
            album_completion = user.album_completion_pct

            if album_completion <= 20:
                report.p20 += 1

            elif album_completion <= 40:
                report.p40 += 1

            elif album_completion <= 60:
                report.p60 += 1

            elif album_completion <= 80:
                report.p80 += 1

            else:
                report.p100 += 1

        await self.db["album_reports"].insert_one(report.__dict__)
        return report


instance: Union[ReportManager, None] = None


async def GetReportManager():
    global instance
    if instance is None:
        db: DatabaseManager = await get_database()
        instance = ReportManager(db.db)

    return instance
