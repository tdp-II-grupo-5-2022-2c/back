from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body
from starlette import status
from starlette.responses import JSONResponse

from app.adapters.dtos.sticker_details import StickerDetailResponse
from app.db import DatabaseManager, get_database
from app.db.impl.sticker_manager import StickerManager
from app.db.impl.user_manager import UserManager
from app.db.model.sticker import StickerModel, UpdateStickerModel
from app.db.model.user_id import UserIdModel
from typing import List


router = APIRouter(tags=["stickers"])


@router.get(
    "/stickers",
    response_description="Get all stickers",
    status_code=status.HTTP_200_OK,
)
async def get_stickers(
        db: DatabaseManager = Depends(get_database),
):
    manager = StickerManager(db.db)
    try:
        response = await manager.get_all()
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting All Sticker. Exception {e}"
        )


@router.get(
    "/stickers/{sticker_id}",
    response_description="Get sticker by id",
    status_code=status.HTTP_200_OK,
)
async def get_sticker_by_id(
    sticker_id: str,
    db: DatabaseManager = Depends(get_database),
):
    manager = StickerManager(db.db)
    try:
        response = await manager.get_by_id(id=sticker_id)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting All Sticker. Exception {e}"
        )


@router.post(
    "/stickers/package",
    response_description="Get package for user",
    response_model=List[StickerDetailResponse],
    status_code=status.HTTP_201_CREATED,
)
async def get_package(
    user_id: UserIdModel = Body(...),
    db: DatabaseManager = Depends(get_database),
):
    manager = StickerManager(db.db)
    user_manager = UserManager(db.db)
    try:
        user = await user_manager.get_by_id(id=user_id.user_id)
        if user.package_counter == 0:
            raise HTTPException(
                status_code=400,
                detail=f"User {user_id.user_id} doesn't have any packages to open",
            )

        package = await manager.create_package()
        # After create package open package and add to user myStickers
        response = await user_manager.open_package(
            package=package, user_id=user_id.user_id
        )
        # User updated with his new stickers
        user_updated = await user_manager.get_by_id(id=user_id.user_id)
        user_updated.package_counter -= 1
        await user_manager.update(id=user_id.user_id, user=user_updated)

        return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=jsonable_encoder(response)
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not return daily package. Exception: {e}"
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


@router.put(
    "/stickers/{sticker_id}",
    response_description="Update an sticker",
    response_model=StickerModel,
    status_code=status.HTTP_200_OK,
)
async def update(
        sticker_id: str,
        stickers: UpdateStickerModel = Body(...),
        db: DatabaseManager = Depends(get_database)
):
    manager = StickerManager(db.db)
    try:
        response = await manager.update(id=sticker_id, sticker=stickers)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error updating Sticker. Exception {e}"
        )