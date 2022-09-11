import logging
from typing import Optional, List
from fastapi import APIRouter, status, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.db import DatabaseManager, get_database
from app.db.impl.user_sticker_manager import UserStickerManager
from app.db.model.user_sticker import UserStickerModel, UpdateUserStickerModel

router = APIRouter(tags=["stickers"])


@router.get(
    "/user/stickers/{user_sticker_id}",
    response_description="Get a single user sticker list",
    response_model=UserStickerModel,
    status_code=status.HTTP_200_OK,
)
async def show_my_list(
	user_sticker_id: str,
    db: DatabaseManager = Depends(get_database),
):
	manager = UserStickerManager(db.db)
	response = await manager.get_by_id(id=user_sticker_id)
	return response


@router.get(
    "/user/stickers",
    response_description="Get a single user sticker list by user_id",
    response_model=UserStickerModel,
    status_code=status.HTTP_200_OK,
)
async def show_my_list_by_user_id(
	user_id: Optional[str] = None,
    db: DatabaseManager = Depends(get_database),
):
	manager = UserStickerManager(db.db)
	response = await manager.get_by_user_id(user_id=user_id)
	return response


@router.put(
    "/user/stickers/{user_sticker_id}",
    response_description="Update an user sticker's list",
    response_model=UserStickerModel,
    status_code=status.HTTP_200_OK,
)
async def update(
    user_sticker_id: str,
    user_sticker: UpdateUserStickerModel = Body(...),
    db: DatabaseManager = Depends(get_database)
):
	manager = UserStickerManager(db.db)
	try:
		# do
		response = await manager.update(id=user_sticker_id, sticker=user_sticker)
		return response
	except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error updating User Sticker. Exception {e}"
        )