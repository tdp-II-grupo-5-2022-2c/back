from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body
from starlette import status
from starlette.responses import JSONResponse

from app.db import DatabaseManager, get_database
from app.db.impl.sticker_manager import StickerManager
from app.db.model.package import PackageModel
from app.db.model.sticker import StickerModel

router = APIRouter(tags=["stickers"])


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


@router.get(
    "/stickers/package",
    response_description="Get daily package for user",
    response_model=PackageModel,
    status_code=status.HTTP_201_CREATED,
)
async def get_package(
        db: DatabaseManager = Depends(get_database),
):
    manager = StickerManager(db.db)
    try:
        package = await manager.create_package()
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content=jsonable_encoder(package)
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Could not return package. Exception: {e}"
        )
