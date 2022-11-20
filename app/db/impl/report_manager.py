from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from datetime import datetime
from app.db.model.report import AlbumCompletionReport
from app.db.model.user import UserModel


class ReportManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_album_completion_report(self, users: List[UserModel]):
        report = AlbumCompletionReport()
        report.date = datetime.today().strftime('%Y-%m-%d')

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

            await self.db["album_reports"].insert_one(report)

        return report
