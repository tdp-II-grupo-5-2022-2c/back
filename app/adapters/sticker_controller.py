from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body
from starlette import status
from starlette.responses import JSONResponse

from app.db import DatabaseManager, get_database
from app.db.impl.sticker_manager import StickerManager
from app.db.impl.user_manager import UserManager
from app.db.model.package import PackageModel
from app.db.model.sticker import StickerModel
from app.db.model.user_id import UserIdModel
from app.db.model.user import UserModel


router = APIRouter(tags=["stickers"])


@router.post(
    "/stickers/package",
    response_description="Get daily package for user",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
)
async def get_daily_package(
    user_id: UserIdModel = Body(...),
    db: DatabaseManager = Depends(get_database),
):
    manager = StickerManager(db.db)
    user_manager = UserManager(db.db)
    try:
        package = await manager.create_package()
        # After create package open package and add to user myStickers
        response = await user_manager.open_package(package=package, user_id=user_id.id)
        return JSONResponse(
                status_code=status.HTTP_201_CREATED, content=jsonable_encoder(response)
            )
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