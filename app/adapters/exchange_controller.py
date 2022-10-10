from typing import List
from app.db.impl.exchange_manager import ExchangeManager
from app.db.impl.user_manager import UserManager
from app.db.model.exchange import ExchangeModel, ExchangeActionModel, available_exchange_actions, accept_action, reject_action
from app.db.model.my_sticker import MyStickerModel
from app.db.model.user import UpdateUserModel, UserModel
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body
from starlette import status
from starlette.responses import JSONResponse

from app.db import DatabaseManager, get_database
from app.db.impl.community_manager import CommunityManager
from app.db.model.community import CommunityModel


router = APIRouter(tags=["exchanges"])


@router.post(
    "/exchanges",
    response_description="Create new exchange",
    status_code=status.HTTP_200_OK,
)
async def create_exchange(
    exchange: ExchangeModel = Body(...),
    db: DatabaseManager = Depends(get_database),
):
    manager = ExchangeManager(db.db)
    user_manager = UserManager(db.db)

    if len(exchange.stickers_to_give) > 5:
        raise HTTPException(status_code=400, detail=f"Could not create Exchange. len of stickers_to_give is: {exchange.stickers_to_give} should be lower or equal than 5")
    if len(exchange.stickers_to_receive) > 5:
        raise HTTPException(status_code=400, detail=f"Could not create Exchange. len of stickers_to_receive is: {exchange.stickers_to_receive} should be lower or equal than 5")

    try:
        pendingExchanges = await manager.get_pending_exchanges_by_sender_id(exchange.sender_id)
        if len(pendingExchanges) >= 3: 
            raise HTTPException(status_code=400, detail=f"Could not create Exchange. user reached max amount of pending exchanges")

        sender = await user_manager.get_by_id(exchange.sender_id)

        # Check sender has stickers for the exchange
        for ss in exchange.stickers_to_give:
            found = False
            
            for sticker in sender.stickers:
                if sticker.quantity > 0 and ss == sticker.id:
                    found = True

            
            if found == False:
                raise HTTPException(
                status_code=400,
                detail=f"Error trying to create exchange for user: {sender.id}. Does not have available all the stickers for exchange. Missing {ss}"
            )
    
        response = await manager.add_new(exchange)
        return JSONResponse(
                status_code=status.HTTP_201_CREATED, content=jsonable_encoder(response)
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not create Community. Exception: {e}"
        )



@router.post(
    "/exchanges/{exchange_id}",
    response_description="Apply action to exchange",
    status_code=status.HTTP_200_OK,
)
async def apply_action_to_exchange(
    exchange_id: str,
    exchangeAction: ExchangeActionModel = Body(...),
    db: DatabaseManager = Depends(get_database),
):
    # WARNING: Here we are assuming that sender and receiver are on the same community so they can perform exchange operations

    if exchangeAction.action not in available_exchange_actions:
        raise HTTPException(status_code=400, detail=f"Could not apply action to exchange. invalid action: {exchangeAction.action}. Available actions: {available_exchange_actions}")

    manager = ExchangeManager(db.db)
    try:
        exchange = await manager.get_exchange_by_id(exchange_id)

        ### WARNING: This is not a transactional operation, if something fails this doesn't assure to end in a consistent state
        if exchangeAction.action == accept_action:
            updatedExchange = await applyAccept(db, exchange, exchangeAction.receiver_id)
        elif exchangeAction.action == reject_action:
            updatedExchange = await applyReject(exchange, exchangeAction.receiver_id)

        result = await manager.update(exchange_id, updatedExchange)

        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error trying to apply action to exchange {exchange_id}. Exception {e}"
        )


async def applyAccept(db: DatabaseManager, exchange: ExchangeModel, receiver_id: str):
    user_manager = UserManager(db.db)

    receiver = await user_manager.get_by_id(receiver_id)
    
    # Check that receiver has stickers_to_receive (the stickers that the giver will receive) for the exchange and if found decrement sticker quantity
    for rs in exchange.stickers_to_receive:
        found = False
        
        for sticker in receiver.stickers:
            if sticker.quantity > 0 and rs == sticker.id:
                found = True
                sticker.quantity -= 1

        
        if found == False:
            raise HTTPException(
            status_code=400,
            detail=f"Error trying to apply action to exchange {exchange.id}. Receiver with id: {receiver.id} does not have available all the stickers for exchange. Missing {rs}"
        )

    sender = await user_manager.get_by_id(exchange.sender_id)

    # Check that sender has stickers_to_give for the exchange and if found decrement sticker quantity
    for ss in exchange.stickers_to_give:
        found = False
        
        for sticker in sender.stickers:
            if sticker.quantity > 0 and ss == sticker.id:
                found = True
                sticker.quantity -= 1

        
        if found == False:
            raise HTTPException(
            status_code=400,
            detail=f"Error trying to apply action to exchange {exchange.id}. Sender with id: {sender.id} does not have available all the stickers for exchange. Missing {ss}"
        )

    # Do exchange for sender, he must receive stickers_to_receive
    for rs in exchange.stickers_to_receive:
        found = False
        
        for sticker in sender.stickers:
            if rs == sticker.id:
                found = True
                sticker.quantity += 1

        
        if found == False:
            sticker = MyStickerModel(
                id=rs,
                quantity=1,
                is_on_album=False)
            sender.stickers.append(sticker)

    # Do exchange for receiver, he must receive stickers_to_give
    for sg in exchange.stickers_to_give:
        found = False
        
        for sticker in receiver.stickers:
            if sg == sticker.id:
                found = True
                sticker.quantity += 1

        
        if found == False:
            sticker = MyStickerModel(
                id=sg,
                quantity=1,
                is_on_album=False
            )
            receiver.stickers.append(sticker)

    print('sender: ', sender.dict())
    print()
    print('receiver: ', receiver.dict())
    print()
    await user_manager.update(exchange.sender_id, sender)
    await user_manager.update(receiver_id, receiver)
    
    exchange.completed = True
    
    return exchange


async def applyReject(exchange: ExchangeModel, receiver_id: str):
    exchange.blacklist_user_ids.append(receiver_id)
    return exchange
