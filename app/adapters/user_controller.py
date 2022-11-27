from fastapi import APIRouter, status, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List

from app.db import DatabaseManager, get_database
from app.db.impl.user_manager import UserManager, GetUserManager
import logging
from app.db.impl.sticker_manager import StickerManager
from app.db.model.user import UserModel, UpdateUserModel
from app.adapters.dtos.sticker_details import StickerDetailResponse
from app.firebase import FirebaseManager, GetFirebaseManager

router = APIRouter(tags=["users"])


@router.get(
    "/users",
    response_description="Get a all users or get an user by mail",
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
            return response
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
    response_description="Get a user",
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
    response_description="Update an user",
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
        if response.is_profile_complete is False:
            if response.isProfileComplete():
                response.is_profile_complete = True
                response.package_counter += 3
                response = await manager.update(id=user_id, user=response)

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


@router.put(
    "/users/packages/daily-package",
    response_model=List[UserModel],
    status_code=status.HTTP_200_OK,
    description="Set the daily packages on True to all users"
)
async def put_daily_package_availability(
        manager: UserManager = Depends(GetUserManager),
        firebaseManager: FirebaseManager = Depends(GetFirebaseManager),
):
    try:
        users = await manager.get_all()
        users_updated = []
        for user in users:
            user.has_daily_packages_available = True
            users_updated.append(user)
            await manager.update(id=user.id, user=user)
            if user.fcmToken != '':
                firebaseManager.sendPush(
                    title="Reclama tus paquetes diarios!",
                    description="Anda a Inicio para reclamar tus paquetes diarios",
                    fcmToken=user.fcmToken
                )

        return users_updated
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not get daily packages. Exception: {e}"
        )


@router.put(
    "/users/{user_id}/packages/daily-package",
    response_model=UserModel,
    status_code=status.HTTP_200_OK,
    description="Add the daily packages to the user's package amount"
)
async def put_daily_package(
        user_id: str,
        manager: UserManager = Depends(GetUserManager),
):
    try:
        user = await manager.get_by_id(id=user_id)
        if user.has_daily_packages_available is False:
            raise HTTPException(
                status_code=400, detail=f"User {user_id} hasn't any packages available"
            )
        user.has_daily_packages_available = False
        user.package_counter += 2
        await manager.update(id=user_id, user=user)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not get daily packages. Exception: {e}"
        )
