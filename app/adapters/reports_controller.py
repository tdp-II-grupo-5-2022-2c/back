from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body
from starlette import status
from starlette.responses import JSONResponse

from app.adapters.dtos.sticker_details import StickerDetailResponse
from app.db import DatabaseManager, get_database
from app.db.impl.sticker_manager import StickerManager, GetStickerManager
from app.db.impl.user_manager import UserManager, GetUserManager
from app.db.model.sticker import StickerModel, UpdateStickerModel
from app.db.model.sticker_metrics import StickerMetricsModel
from app.db.model.user_id import UserIdModel
from typing import List, Dict

router = APIRouter(tags=["reports"])


@router.get(
    "/reports/top5-stickers-metrics",
    response_description="Get top 5 stickers metrics",
    status_code=status.HTTP_200_OK,
)
async def get_stickers(
        sticker_manager: StickerManager = Depends(GetStickerManager),
):
    try:
        top5 = await sticker_manager.get_sticker_metrics_top_5()
        result = await renderStickers(top5)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error getting top 5. Exception: {e}"
        )


async def renderStickers(stickers: List[Dict]) -> List[Dict]:
    sticker_manager: StickerManager = await GetStickerManager()
    result = []
    for s in stickers:
        sticker = await sticker_manager.get_by_id(s['sticker_id'])
        sticker['counter'] = s['counter']
        result.append(sticker)

    return result
