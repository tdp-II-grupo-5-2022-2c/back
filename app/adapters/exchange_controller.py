import logging
from typing import List
from app.db.impl.exchange_manager import ExchangeManager
from app.db.impl.user_manager import UserManager
from app.db.model.exchange import ExchangeModel, ExchangeActionModel, AVAILABLE_EXCHANGE_ACTIONS, ACCEPT_ACTION, REJECT_ACTION
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

    # Validation for amount of stickers in exchange
    if len(exchange.stickers_to_give) > 5:
        raise HTTPException(status_code=400, detail=f"Could not create Exchange. len of stickers_to_give is: {exchange.stickers_to_give} should be lower or equal than 5")
    if len(exchange.stickers_to_receive) > 5:
        raise HTTPException(status_code=400, detail=f"Could not create Exchange. len of stickers_to_receive is: {exchange.stickers_to_receive} should be lower or equal than 5")

    # Validation for unique stickers in exchange
    if not stickersForExchangeAreUnique(exchange.stickers_to_give):
        raise HTTPException(status_code=400, detail=f"Could not create Exchange. stickers_to_give are not unique: {exchange.stickers_to_give}")
    if not stickersForExchangeAreUnique(exchange.stickers_to_receive):
        raise HTTPException(status_code=400, detail=f"Could not create Exchange. stickers_to_receive are not unique: {exchange.stickers_to_receive}")

    if not stickersToGiveAndReceiveAreDiff(exchange.stickers_to_give, exchange.stickers_to_receive):
        raise HTTPException(status_code=400, detail=f"Could not create Exchange. stickers_to_receive and stickers_to_give must not have sticker in common")

    try:
        pendingExchanges = await manager.get_pending_exchanges_by_sender_id(exchange.sender_id)
        if len(pendingExchanges) >= 3: 
            raise HTTPException(status_code=400, detail=f"Could not create Exchange. user reached max amount of pending exchanges")

        sender = await user_manager.get_by_id(exchange.sender_id)
        if not userHasStickersForExchange(sender, exchange.stickers_to_give):
            raise HTTPException(
                status_code=400,
                detail=f"Error trying to create exchange for user: {sender.id}. Does not have available all the stickers for exchange."
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


def stickersForExchangeAreUnique(stickers: List[str]) -> bool:
    freq = {}
    for s in stickers:
        if s not in freq:
            freq[s] = 1
        else:
            freq[s] += 1
    
    for item in freq.keys():
        if freq[item] > 1:
            return False
    
    return True


def stickersToGiveAndReceiveAreDiff(stickersToGive: List[str], stickersToReceive: List[str]) -> bool:
    give = set(stickersToGive)
    receive = set(stickersToReceive)

    if len(give.intersection(receive)) > 0:
        return False

    return True


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

    if exchangeAction.action not in AVAILABLE_EXCHANGE_ACTIONS:
        raise HTTPException(status_code=400, detail=f"Could not apply action to exchange. invalid action: {exchangeAction.action}. Available actions: {AVAILABLE_EXCHANGE_ACTIONS}")

    manager = ExchangeManager(db.db)
    try:
        exchange = await manager.get_exchange_by_id(exchange_id)

        ### WARNING: This is not a transactional operation, if something fails this doesn't assure to end in a consistent state
        if exchangeAction.action == ACCEPT_ACTION:
            updatedExchange = await applyAccept(db, exchange, exchangeAction.receiver_id)
        elif exchangeAction.action == REJECT_ACTION:
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
    if not userHasStickersForExchange(receiver, exchange.stickers_to_receive):
        raise HTTPException(
            status_code=400,
            detail=f"Error trying to apply action to exchange {exchange.id}. Receiver with id: {receiver.id} does not have available all the stickers for exchange."
        )

    sender = await user_manager.get_by_id(exchange.sender_id)
    if not userHasStickersForExchange(sender, exchange.stickers_to_give):
        raise HTTPException(
            status_code=400,
            detail=f"Error trying to apply action to exchange {exchange.id}. Sender with id: {sender.id} does not have available all the stickers for exchange."
        )

    # Do exchange for stickers_to_receive
    for rs in exchange.stickers_to_receive:
        # receiver must deliver stickers_to_receive
        for sticker in receiver.stickers:
            if rs == sticker.id:
                sticker.quantity -= 1
        
        # sender must receive stickers_to_receive
        found = False
        for sticker in sender.stickers:
            if rs == sticker.id:
                found = True
                sticker.quantity += 1

        if found == False:
            newSticker = MyStickerModel(id=rs, quantity=1, is_on_album=False)
            sender.stickers.append(newSticker)

    # Do exchange for stickers_to_give 
    for sg in exchange.stickers_to_give:
        # sender must deliver stickers_to_give
        for sticker in sender.stickers:
            if sg == sticker.id:
                sticker.quantity -= 1
        
        # receiver must receive stickers_to_give
        found = False
        for sticker in receiver.stickers:
            if sg == sticker.id:
                found = True
                sticker.quantity += 1

        if found == False:
            sticker = MyStickerModel(id=sg, quantity=1, is_on_album=False)
            receiver.stickers.append(sticker)

    logging.info(f'sender after exchange: {sender.dict()}')
    logging.info(f'receiver after exchange: {receiver.dict()}')

    await user_manager.update(exchange.sender_id, sender)
    await user_manager.update(receiver_id, receiver)
    
    exchange.completed = True
    
    return exchange


async def applyReject(exchange: ExchangeModel, receiver_id: str):
    if receiver_id not in exchange.blacklist_user_ids:
        exchange.blacklist_user_ids.append(receiver_id)
    return exchange


@router.get(
    "/exchanges",
    response_description="Get exchanges",
    status_code=status.HTTP_200_OK,
)
async def get_pending_exchanges_by_sender_id(
    sender_id: str,
    completed: bool = None,
    db: DatabaseManager = Depends(get_database),
):
    exchange_manager = ExchangeManager(db.db)

    try:
        if sender_id is not None:
            response = await exchange_manager.get_exchange_by_sender_id(sender_id, completed)
            return response
        
        raise HTTPException(status_code=500, detail=f"Could not get exchanges. operation getAll not supported")
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not get exchanges. Exception: {e}"
        )


@router.get(
    "/users/{user_id}/communities/{community_id}/exchanges",
    response_description="Get available exchanges for user_id",
    status_code=status.HTTP_200_OK,
)
async def get_available_exchanges(
    user_id: str,
    community_id: str,
    db: DatabaseManager = Depends(get_database),
):
    exchange_manager = ExchangeManager(db.db)
    user_manager = UserManager(db.db)
    community_manager = CommunityManager(db.db)

    try:
        communities = await community_manager.get_by_member(user_id)
        if community_id not in [c['_id'] for c in communities]:
            raise HTTPException(
                status_code=404, detail=f"user_id: {user_id} does not belong to the community_id: {community_id}"
            )

        community = await community_manager.get_by_id(community_id)
        possibleExchangers = set(community.users)
        possibleExchangers.remove(user_id)
        logging.info(f"possibleExchangers: {possibleExchangers}")

        allExchanges = []
        for pe in possibleExchangers:
            exchanges = await exchange_manager.get_pending_exchanges_by_sender_id(pe)
            allExchanges.extend(exchanges)
        
        logging.info(f"allExchanges: {allExchanges}")
        user = await user_manager.get_by_id(user_id)

        result = []
        for exchange in allExchanges:
            if user_id in exchange['blacklist_user_ids']:
                continue
            if not userHasStickersForExchange(user, exchange['stickers_to_receive']):
                continue
            
            result.append(exchange)

        return JSONResponse(
                status_code=status.HTTP_200_OK, content=jsonable_encoder(result)
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not get exchanges. Exception: {e}"
        )

def userHasStickersForExchange(user: UserModel, sticker_ids: List[str]) -> bool:
    stickersFreq = {}
    for sid in sticker_ids:
        if sid not in stickersFreq:
            stickersFreq[sid] = 1
        else:
            stickersFreq[sid] += 1

    for sid in stickersFreq.keys():
        found = False
        for sticker in user.stickers:
            if sticker.quantity >= stickersFreq[sid] and sid == sticker.id:
                found = True
        
        if not found:
            return False

    return True