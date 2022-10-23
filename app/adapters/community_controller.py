from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body
from fastapi import Request
from starlette import status
from starlette.responses import JSONResponse

from app.db import DatabaseManager, get_database
from app.db.impl.community_manager import CommunityManager
from app.db.model.community import CommunityModel
from app.adapters.dtos.community_details import UserNameResponse
from app.adapters.dtos.community_details import CommunityDetailResponse
from app.db.impl.user_manager import UserManager
import logging

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
    request: Request,
    community_id: str,
    db: DatabaseManager = Depends(get_database),
):
    comm_manager = CommunityManager(db.db)
    user_manager = UserManager(db.db)
    try:
        sender = request.headers['x-user-id']
        comm = await comm_manager.get_by_id(id=community_id)
        logging.info(comm)

        users = []
        for user_id in comm.users:
            logging.info(user_id)
            user_model = await user_manager.get_by_id(user_id)
            logging.info(user_model)
            if user_model != None:
                user = UserNameResponse(
                    id=str(user_model.id),
                    name=user_model.name,
                    lastname=user_model.lastname,
                    mail=user_model.mail
                )
                users.append(user)
        response = CommunityDetailResponse(
            id=str(comm.id),
            name=comm.name,
            owner=comm.owner,
            users=users,
            password=comm.password
        )
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
