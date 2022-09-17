# import logging
# from typing import Optional
from typing import List

from fastapi import APIRouter, status, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List

from app.db import DatabaseManager, get_database
from app.db.impl.user_manager import UserManager
from app.db.model.user import MyStickerModel, UserModel, UpdateUserModel

router = APIRouter(tags=["users"])


@router.get(
    "/users",
    response_description="Get a all users",
    response_model=List[UserModel],
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
    db: DatabaseManager = Depends(get_database),
):
    manager = UserManager(db.db)
    try:
        response = await manager.get_all()
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting Users info. Exception {e}"
        )


@router.get(
    "/users/{user_id}",
    response_description="Get a user with the sticker list",
    response_model=UserModel,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_id(
        user_id: str,
        db: DatabaseManager = Depends(get_database),
):
    manager = UserManager(db.db)
    response = await manager.get_by_id(id=user_id)
    return response


@router.post(
    "/users",
    response_description="Create user",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
)
async def create_new(
        user: UserModel = Body(...),
        db: DatabaseManager = Depends(get_database),
):
    manager = UserManager(db.db)
    try:
        response = await manager.add_new(user=user)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content=jsonable_encoder(response)
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Could not create User. Exception: {e}"
        )


@router.put(
    "/users/{user_id}",
    response_description="Update an user sticker's list",
    response_model=UserModel,
    status_code=status.HTTP_200_OK,
)
async def update(
        user_id: str,
        user: UpdateUserModel = Body(...),
        db: DatabaseManager = Depends(get_database)
):
    manager = UserManager(db.db)
    try:
        # do
        response = await manager.update(id=user_id, user=user)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error updating User. Exception {e}"
        )


@router.get(
    "/users/{user_id}/stickers",
    response_description="Get an user sticker's list",
    response_model=List[MyStickerModel],
    status_code=status.HTTP_200_OK,
)
async def get_stickers(
        user_id: str,
        db: DatabaseManager = Depends(get_database)
):
    manager = UserManager(db.db)
    try:
        response = await manager.get_stickers(id=user_id)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting stickers. Exception {e}"
        )
@router.patch(
    "/users/{user_id}/stickers/{sticker_id}/paste",
    response_description="Paste sticker in album",
    response_model=UserModel,
    status_code=status.HTTP_200_OK,
)
async def paste_sticker(
    user_id: str,
    sticker_id: str,
    db: DatabaseManager = Depends(get_database),
):
    manager = UserManager(db.db)
    try:
        response = await manager.paste_sticker(user_id=user_id, sticker_id=sticker_id)
        return JSONResponse(
                status_code=status.HTTP_200_OK, content=jsonable_encoder(response)
            )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Could not paste sticker. Exception: {e}"
        )
