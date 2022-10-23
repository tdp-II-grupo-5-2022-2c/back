from typing import Union
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body
from fastapi import Header
from starlette import status
from starlette.responses import JSONResponse

from app.db import DatabaseManager, get_database
from app.db.impl.community_manager import CommunityManager
from app.db.model.community import CommunityModel, UpdateCommunityModel


router = APIRouter(tags=["communities"])


@router.get(
    "/communities",
    response_description="Get all communities",
    status_code=status.HTTP_200_OK,
)
async def get_all(
    owner_id: str = None,
    member_id: str = None,
    db: DatabaseManager = Depends(get_database),
):
    manager = CommunityManager(db.db)
    try:
        response = await manager.get_all(owner_id, member_id)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting All Communities. Exception {e}"
        )


@router.get(
    "/communities/{community_id}",
    response_description="Get community by id",
    status_code=status.HTTP_200_OK,
)
async def get_community_by_id(
    community_id: str,
    db: DatabaseManager = Depends(get_database),
):
    manager = CommunityManager(db.db)
    try:
        response = await manager.get_by_id(id=community_id)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting Community by id {community_id}. Exception {e}"
        )


@router.patch(
    "/communities/{community_id}",
    response_description="Set community password",
    status_code=status.HTTP_200_OK,
)
async def set_community_password(
    community_id: str,
    body: UpdateCommunityModel = Body(...),
    x_user_id: Union[str, None] = Header(default=None),
    db: DatabaseManager = Depends(get_database),
):
    manager = CommunityManager(db.db)

    if x_user_id is None:
        raise HTTPException(
            status_code=400,
            detail="Missing X-User-Id header on request",
        )

    if body.password is None or body.password == "":
        raise HTTPException(
            status_code=400,
            detail="password is required",
        )

    try:
        community = await manager.get_by_id(id=community_id)
        if community.owner != x_user_id:
            raise HTTPException(
                status_code=401,
                detail=f"user_id: {x_user_id} is not authorized for this operation",
            )

        result = await manager.update(community_id, body)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating Community by id {community_id}. Exception {e}"
        )


@router.post(
    "/communities",
    response_description="Create new community",
    response_model=CommunityModel,
    status_code=status.HTTP_201_CREATED,
)
async def create_community(
        community: CommunityModel = Body(...),
        db: DatabaseManager = Depends(get_database),
):
    manager = CommunityManager(db.db)
    try:
        response = await manager.add_new(community=community)
        return JSONResponse(
                status_code=status.HTTP_201_CREATED, content=jsonable_encoder(response)
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not create Community. Exception: {e}"
        )
