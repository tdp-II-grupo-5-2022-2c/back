from typing import Union
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body
from fastapi import Request, Header
from starlette import status
from starlette.responses import JSONResponse

from app.db import DatabaseManager, get_database
from app.db.impl.community_manager import CommunityManager
from app.db.model.community import CommunityModel, UpdateCommunityModel

router = APIRouter(tags=["communities"])

MAX_USERS_PER_COMM = 10


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
        request: Request,
        community_id: str,
        db: DatabaseManager = Depends(get_database),
):
    manager = CommunityManager(db.db)
    try:
        community = await manager.get_by_id(id=community_id)
        sender = request.headers['x-user-id']
        if sender not in community.users and sender != community.owner:
            raise HTTPException(
                status_code=401,
                detail=f"User {sender} not allowed to access community {community_id}"
            )
        return community

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
        community = await manager.get_by_id(id=community_id)
        if community.password != password:
            raise HTTPException(
                status_code=401, detail=f"Wrong password. "
                                        f"User {user_id} could not join community {community_id}"
            )
        if len(community.users) == MAX_USERS_PER_COMM:
            raise HTTPException(
                status_code=400, detail=f"Full community."
                                        f"User {user_id} could not join community {community_id}"
            )
        if user_id in community.users:
            raise HTTPException(
                status_code=400, detail=f"User {user_id} already joined community {community_id}"
            )
        response = await manager.join_community(
            community_id=community_id,
            user_id=user_id
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(response)
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not join user to Community. Exception: {e}"
        )
