# import logging
# from typing import Optional
from fastapi import APIRouter, status, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.db import DatabaseManager, get_database
from app.db.impl.sticker_manager import StickerManager
from app.db.model.package import PackageModel
from app.db.model.sticker import StickerModel
from app.db.model.user_id import UserIdModel
from app.db.model.user import UserModel


router = APIRouter(tags=["stickers"])


@router.post(
    "/stickers/new-package",
    response_description="Get daily package for user",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
)
async def get_daily_package(
    user_id: UserIdModel = Body(...),
    db: DatabaseManager = Depends(get_database),
):
    manager = StickerManager(db.db)
    user_manager = StickerManager(db.db)
    try:
        package = await manager.create_package(user_id=user_id.user_id)
        # SE deberia tambien agregar la lista de stickers al user,
        # el package tiene que tener un id??
        # Como seria el endpoint de open package
        # Agregar lista de stickers al user
        response = await user_manager.open_package(package=package)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content=jsonable_encoder(response)
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Could not return daily package. Exception: {e}"
        )


@router.post(
    "/stickers",
    response_description="Create new sticker",
    response_model=StickerModel,
    status_code=status.HTTP_201_CREATED,
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
            status_code=400, detail=f"Could not create Sticker. Exception: {e}"
        )
