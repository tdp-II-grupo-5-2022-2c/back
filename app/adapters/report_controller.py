from fastapi import APIRouter, status, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List

from app.db import DatabaseManager, get_database
from app.db.impl.report_manager import ReportManager
from app.db.impl.user_manager import UserManager
from app.db.model.report import AlbumCompletionReport

router = APIRouter(tags=["reports"])

@router.get(
    "/reports/album_completion",
    response_description="Get user's album completion percentage",
    response_model=AlbumCompletionReport,
    status_code=status.HTTP_200_OK,
)
async def get_users_album_completion(
    db: DatabaseManager = Depends(get_database),
):
    manager = ReportManager(db.db)
    user_manager = UserManager(db.db)

    try:
        users = await user_manager.get_all()
        response = await manager.get_album_completion_report(users)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not generate album completion report. Exception: {e}"
        )
