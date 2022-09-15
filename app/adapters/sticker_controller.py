# import logging
# from typing import Optional
from fastapi import APIRouter, status, Depends, HTTPException, Body
# from fastapi.responses import JSONResponse
# from fastapi.encoders import jsonable_encoder

from app.db import DatabaseManager, get_database
from app.db.impl.sticker_manager import StickerManager
from app.db.model.package import PackageModel
from app.db.model.sticker import StickerModel

router = APIRouter(tags=["stickers"])


@router.get(
    "/stickers/new-package/{user_id}",
    response_description="Get daily package for user",
    response_model=PackageModel,
    status_code=status.HTTP_200_OK,
)
async def get_daily_package(
    user_id: str,
    db: DatabaseManager = Depends(get_database),
):
    manager = StickerManager(db.db)
    response = await manager.create_package(user_id=user_id)
    return response


@router.post(
    "/stickers",
    response_description="Get daily package for user",
    response_model=StickerModel,
    status_code=status.HTTP_200_OK,
)
async def create_sticker(
    sticker: StickerModel = Body(...),
    db: DatabaseManager = Depends(get_database),
):
    manager = StickerManager(db.db)
    try:
        response = await manager.create_sticker(sticker=sticker)
        return JSONResponse(
                    status_code=status.HTTP_201_CREATED, content=jsonable_encoder(response)
                )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Could not create User. Exception: {e}"
        )
