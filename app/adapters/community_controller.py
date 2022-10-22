from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body
from starlette import status
from starlette.responses import JSONResponse

from app.db import DatabaseManager, get_database
from app.db.impl.community_manager import CommunityManager
from app.db.model.community import CommunityModel

router = APIRouter(tags=["communities"])


@router.get(
    "/communities",
    response_description="Get community by owner id or member id."
                         "If no parameter is specified, it will get all communities",
    status_code=status.HTTP_200_OK,
)
async def get_communities(
        owner: str = None,
        member: str = None,
        db: DatabaseManager = Depends(get_database),
):
    manager = CommunityManager(db.db)
    try:
        response = await manager.get_communities(owner, member)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting Communities. Exception {e}"
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


@router.post(
    "/communities/{community_id}/users/{user_id}",
    response_description="Join user to community",
    response_model=CommunityModel,
    status_code=status.HTTP_200_OK,
)
async def join_community(
        community_id: str,
        user_id: str,
        password: str = None,
        db: DatabaseManager = Depends(get_database),
):
    manager = CommunityManager(db.db)
    try:
        response = await manager.join_community(
            community_id=community_id,
            user_id=user_id,
            password=password
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(response)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not join user to Community. Exception: {e}"
        )
