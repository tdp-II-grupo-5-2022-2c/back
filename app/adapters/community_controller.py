from typing import Union
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body
from fastapi import Request, Header
from starlette import status
from starlette.responses import JSONResponse

from app.db import DatabaseManager, get_database
from app.db.impl.community_manager import CommunityManager
from app.adapters.dtos.community_details import UserNameResponse
from app.adapters.dtos.community_details import CommunityDetailResponse
from app.db.impl.user_manager import UserManager
import logging
import traceback
from app.db.model.community import CommunityModel, UpdateCommunityModel

router = APIRouter(tags=["communities"])

MAX_USERS_PER_COMM = 11


@router.get(
    "/communities",
    response_description="Get community by owner id or member id."
                         "If no parameter is specified, it will get all communities",
    status_code=status.HTTP_200_OK,
)
async def get_communities(
        owner: str = None,
        member: str = None,
        name: str = None,
        mail: str = None,
        blocked: bool = None,
        db: DatabaseManager = Depends(get_database),
):
    manager = CommunityManager(db.db)
    user_manager = UserManager(db.db)

    try:
        if mail is not None:
            users = await user_manager.get_users_by_mail(mail)
            if users is None or len(users) == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"Mail {mail} not found"
                )
            users_ids = list(map(lambda o: o['_id'], users))
            response = await manager.get_communities(users_ids, None, name, blocked)
        else:
            response = await manager.get_communities([owner], member, name, blocked)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error getting Communities. Exception {e}")
        logging.error(traceback.format_exc())
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
        if sender not in comm.users and sender != comm.owner:
            raise HTTPException(
                status_code=401,
                detail=f"User {sender} not allowed to access community {community_id}"
            )
        users = []
        for user_id in comm.users:
            logging.info(user_id)
            user_model = await user_manager.get_by_id(user_id)
            logging.info(user_model)
            if user_model is not None:
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
            description=comm.description,
            password=comm.password
        )
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        error_msg = f"Error getting Community by id {community_id}. Exception {e}"
        logging.error(error_msg)
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=error_msg
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
        error_msg = f"Error updating Community by id {community_id}. Exception {e}"
        logging.error(error_msg)
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=error_msg
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
    user_manager = UserManager(db.db)

    try:
        owner = await user_manager.get_by_id(community.owner)
        if owner.is_profile_complete is False:
            raise HTTPException(
                status_code=400,
                detail=f"user_id {community.owner} has not complete his profile"
            )

        comm = await manager.get_by_name(community.name)
        if len(comm) != 0:
            raise HTTPException(
                status_code=400,
                detail='there is already a community with that name'
            )

        comms = await manager.get_by_member(community.owner)
        if len(comms) >= 10:
            raise HTTPException(
                status_code=400,
                detail="user can't be in more than 10 communities"
            )

        community.users.append(community.owner)
        response = await manager.add_new(community=community)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content=jsonable_encoder(response)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        error_msg = f"Could not create Community Exception {e}"
        logging.error(error_msg)
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=error_msg
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
    user_manager = UserManager(db.db)

    try:
        user = await user_manager.get_by_id(user_id)
        if user.is_profile_complete is False:
            raise HTTPException(
                status_code=400,
                detail=f"user_id {user_id} has not complete his profile"
            )

        community = await manager.get_by_id(id=community_id)
        if community.password != password:
            raise HTTPException(
                status_code=401, detail=f"Wrong password. "
                                        f"User {user_id} could not join community {community_id}"
            )
        if community.is_blocked is True:
            raise HTTPException(
                status_code=401, detail=f"Community is blocked. "
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
        comms = await manager.get_by_member(user_id)
        if len(comms) >= 10:
            raise HTTPException(
                status_code=400,
                detail="user can't be in more than 10 communities"
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
        error_msg = f"Could not join user to Community. Exception: {e}"
        logging.error(error_msg)
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=error_msg
        )


@router.put(
    "/communities/{community_id}",
    response_description="Update community",
    status_code=status.HTTP_200_OK,
)
async def update(
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
    try:
        result = await manager.update(community_id, body)
        if result.owner != x_user_id:
            raise HTTPException(
                status_code=401,
                detail=f"user_id: {x_user_id} is not authorized for this operation",
            )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        error_msg = f"Error updating Community by id {community_id}. Exception {e}"
        logging.error(error_msg)
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )
