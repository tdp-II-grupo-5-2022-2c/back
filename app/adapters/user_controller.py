from fastapi import APIRouter, status, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List

from app.db import DatabaseManager, get_database
from app.db.impl.user_manager import UserManager
from app.adapters.dtos.user import UserResponse
import logging
from app.db.impl.sticker_manager import StickerManager
from app.db.model.user import UserModel, UpdateUserModel
from app.adapters.dtos.sticker_details import StickerDetailResponse

router = APIRouter(tags=["users"])


@router.get(
    "/users",
    response_description="Get a all users",
    status_code=status.HTTP_200_OK,
)
async def get_users(
        mail: str = None,
        db: DatabaseManager = Depends(get_database),
):
    manager = UserManager(db.db)
    try:
        if mail is not None:
            logging.info(mail)
            response = await manager.get_user_by_mail(mail=mail)
            logging.info(response)
            user = UserResponse(
                id=str(response.id),
                mail=response.mail,
                stickers=response.stickers
            )
            return user
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
    response_model=List[StickerDetailResponse],
    status_code=status.HTTP_200_OK,
)
async def get_stickers(
        user_id: str,
        country: str = None,
        name: str = None,
        is_on_album: bool = None,
        db: DatabaseManager = Depends(get_database)
):
    user_manager = UserManager(db.db)
    sticker_manager = StickerManager(db.db)
    try:
        stickers = await user_manager.get_stickers(
            id=user_id, is_on_album=is_on_album
        )
        if stickers is None:
            return []
        ids = [s.id for s in stickers]
        sticker_details = await sticker_manager.find_by_query(
            ids,
            country=country,
            name=name
        )

        response = []
        for sticker_detail in sticker_details:
            sticker = [s for s in stickers if s.id == sticker_detail["_id"]]
            if len(sticker) != 0:
                sticker_response = StickerDetailResponse(
                    **sticker[0].dict(),
                    **sticker_detail
                )
                response.append(sticker_response)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.exception(e)
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
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Could not paste sticker. Exception: {e}"
        )
