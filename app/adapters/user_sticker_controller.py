# import logging
from typing import Optional
from fastapi import APIRouter, status, Depends, HTTPException, Body
# from fastapi.responses import JSONResponse
# from fastapi.encoders import jsonable_encoder

from app.db import DatabaseManager, get_database
from app.db.impl.user_sticker_manager import UserManager
from app.db.model.user_sticker import UserModel, UpdateUserModel

router = APIRouter(tags=["users"])


@router.get(
    "/users/{user_id}",
    response_description="Get a single user sticker list",
    response_model=UserModel,
    status_code=status.HTTP_200_OK,
)
async def show_my_list(
    user_id: str,
    db: DatabaseManager = Depends(get_database),
):
    manager = UserManager(db.db)
    response = await manager.get_by_id(id=user_id)
    return response


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
