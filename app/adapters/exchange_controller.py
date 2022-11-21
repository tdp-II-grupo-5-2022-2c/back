import logging
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body
from starlette import status
from starlette.responses import JSONResponse
from app.db.impl.community_manager import CommunityManager, GetCommunityManager
from app.db.impl.exchange_manager import GetExchangeManager, ExchangeManager
from app.db.impl.sticker_manager import GetStickerManager
from app.db.impl.user_manager import UserManager, GetUserManager
from app.db.model.exchange import ExchangeModel, \
    ExchangeActionModel, AVAILABLE_EXCHANGE_ACTIONS, ACCEPT_ACTION, REJECT_ACTION
from app.db.model.my_sticker import MyStickerModel
from app.db.model.user import UserModel
from app.firebase import FirebaseManager, GetFirebaseManager


router = APIRouter(tags=["exchanges"])


@router.post(
    "/exchanges",
    response_description="Create new exchange",
    status_code=status.HTTP_200_OK,
)
async def create_exchange(
    exchange: ExchangeModel = Body(...),
    manager: ExchangeManager = Depends(GetExchangeManager),
    user_manager: UserManager = Depends(GetUserManager),
):
    # Validation for amount of stickers in exchange
    if len(exchange.stickers_to_give) > 5:
        raise HTTPException(
            status_code=400,
            detail="Could not create Exchange. len of stickers_to_give " +
            f"is: {exchange.stickers_to_give} should be lower or equal than 5"
        )
    if len(exchange.stickers_to_receive) > 5:
        raise HTTPException(
            status_code=400,
            detail="Could not create Exchange. len of stickers_to_receive " +
            f"is: {exchange.stickers_to_receive} should be lower or equal than 5"
        )

    # Validation for unique stickers in exchange
    if not stickersForExchangeAreUnique(exchange.stickers_to_give):
        raise HTTPException(
            status_code=400,
            detail="Could not create Exchange. " +
            f"stickers_to_give are not unique: {exchange.stickers_to_give}"
        )
    if not stickersForExchangeAreUnique(exchange.stickers_to_receive):
        raise HTTPException(
            status_code=400,
            detail="Could not create Exchange. " +
            f"stickers_to_receive are not unique: {exchange.stickers_to_receive}"
        )

    if not stickersToGiveAndReceiveAreDiff(exchange.stickers_to_give, exchange.stickers_to_receive):
        raise HTTPException(
            status_code=400,
            detail="Could not create Exchange. stickers_to_receive " +
            "and stickers_to_give must not have sticker in common"
        )

    try:
        pendingExchanges = await manager.get_pending_exchanges_by_sender_id(exchange.sender_id)
        if len(pendingExchanges) >= 3:
            raise HTTPException(
                status_code=400,
                detail="Could not create Exchange. " +
                "user reached max amount of pending exchanges"
            )

        sender = await user_manager.get_by_id(exchange.sender_id)
        if sender.is_profile_complete is False:
            raise HTTPException(
                status_code=400,
                detail=f"user_id {exchange.sender_id} has not complete his profile"
            )

        if not userHasStickersForExchange(sender, exchange.stickers_to_give):
            raise HTTPException(
                status_code=400,
                detail=f"Error trying to create exchange for user: {sender.id}. " +
                "Does not have available all the stickers for exchange."
            )

        # update user
        for sg in exchange.stickers_to_give:
            # sender must deliver stickers_to_give
            for sticker in sender.stickers:
                if sg == sticker.id:
                    sticker.quantity -= 1

        await user_manager.update(exchange.sender_id, sender)

        response = await manager.add_new(exchange)
        return JSONResponse(
                status_code=status.HTTP_201_CREATED, content=jsonable_encoder(response)
            )
    except HTTPException as exception:
        raise exception
    except Exception as exception:
        raise HTTPException(
            status_code=500, detail=f"Could not create Community. Exception: {exception}"
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


def stickersToGiveAndReceiveAreDiff(
    stickersToGive: List[str],
    stickersToReceive: List[str],
) -> bool:
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
    manager: ExchangeManager = Depends(GetExchangeManager),
    user_manager: UserManager = Depends(GetUserManager),
):
    # WARNING: Here we are assuming that sender and receiver are on the same community
    #  so they can perform exchange operations

    if exchangeAction.action not in AVAILABLE_EXCHANGE_ACTIONS:
        raise HTTPException(
            status_code=400,
            detail="Could not apply action to exchange. " +
            f"invalid action: {exchangeAction.action}. " +
            f"Available actions: {AVAILABLE_EXCHANGE_ACTIONS}"
        )

    try:
        user = await user_manager.get_by_id(exchangeAction.receiver_id)
        if user.is_profile_complete is False:
            raise HTTPException(
                status_code=400,
                detail=f"user_id {exchangeAction.receiver_id} has not complete his profile"
            )

        exchange = await manager.get_exchange_by_id(exchange_id)

        if exchange.completed is True:
            raise HTTPException(
                status_code=400,
                detail=f"exchange {exchange_id} is completed, you cannot apply any action"
            )

        # WARNING: This is not a transactional operation,
        # if something fails this doesn't assure to end in a consistent state
        if exchangeAction.action == ACCEPT_ACTION:
            updatedExchange = await applyAccept(exchange, exchangeAction.receiver_id)
        elif exchangeAction.action == REJECT_ACTION:
            updatedExchange = await applyReject(exchange, exchangeAction.receiver_id)

        result = await manager.update(exchange_id, updatedExchange)

        return result
    except HTTPException as exception:
        raise exception
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error trying to apply action to exchange {exchange_id}. Exception {e}"
        )


async def applyAccept(exchange: ExchangeModel, receiver_id: str):
    user_manager = await GetUserManager()

    receiver = await user_manager.get_by_id(receiver_id)
    if not userHasStickersForExchange(receiver, exchange.stickers_to_receive):
        raise HTTPException(
            status_code=400,
            detail=f"Error trying to apply action to exchange {exchange.id}. " +
            "Receiver with id: {receiver.id} does not have available " +
            "all the stickers for exchange."
        )

    sender = await user_manager.get_by_id(exchange.sender_id)

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

        if not found:
            newSticker = MyStickerModel(id=rs, quantity=1, is_on_album=False)
            sender.stickers.append(newSticker)

    # Do exchange for stickers_to_give
    for sg in exchange.stickers_to_give:
        # sender must deliver stickers_to_give, this action is moved to create exchange

        # receiver must receive stickers_to_give
        found = False
        for sticker in receiver.stickers:
            if sg == sticker.id:
                found = True
                sticker.quantity += 1

        if not found:
            sticker = MyStickerModel(id=sg, quantity=1, is_on_album=False)
            receiver.stickers.append(sticker)

    # Update statistics
    receiver.exchanges_amount += 1
    sender.exchanges_amount += 1

    logging.info(f'sender after exchange: {sender.dict()}')
    logging.info(f'receiver after exchange: {receiver.dict()}')

    await user_manager.update(exchange.sender_id, sender)
    await user_manager.update(receiver_id, receiver)

    if sender.fcmToken != "":
        firebaseManager: FirebaseManager = await GetFirebaseManager()
        firebaseManager.sendPush(
            "Intercambio aceptado!",
            "Ve a Mis figus para ver las figuritas recibidas!",
            sender.fcmToken)

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
    exchange_manager: ExchangeManager = Depends(GetExchangeManager),
):
    try:
        if sender_id is not None:
            exchanges = await exchange_manager.get_exchange_by_sender_id(sender_id, completed)
            response_body = await render_fetch(exchanges)
            return response_body

        raise HTTPException(
            status_code=500,
            detail="Could not get exchanges. operation getAll not supported"
        )

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
    exchange_manager: ExchangeManager = Depends(GetExchangeManager),
    user_manager: UserManager = Depends(GetUserManager),
    community_manager: CommunityManager = Depends(GetCommunityManager),
):
    try:
        communities = await community_manager.get_by_member(user_id)
        if community_id not in [c['_id'] for c in communities]:
            raise HTTPException(
                status_code=404,
                detail=f"user_id: {user_id} does not belong to the community_id: {community_id}"
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

        response_body = await render_fetch(result)

        return JSONResponse(
                status_code=status.HTTP_200_OK, content=jsonable_encoder(response_body)
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not get exchanges. Exception: {e}"
        )


async def render_fetch(exchanges: List[Dict]):
    sticker_manager = await GetStickerManager()
    user_manager = await GetUserManager()

    for exc in exchanges:
        stickers_to_receive = []
        stickers_to_give = []

        for sr in exc['stickers_to_receive']:
            sticker = await sticker_manager.get_by_id(sr)
            stickers_to_receive.append(sticker)

        for sg in exc['stickers_to_give']:
            sticker = await sticker_manager.get_by_id(sg)
            stickers_to_give.append(sticker)

        exc['stickers_to_receive'] = stickers_to_receive
        exc['stickers_to_give'] = stickers_to_give

        userModel = await user_manager.get_by_id(exc['sender_id'])
        sender = userModel.dict()
        sender['_id'] = exc['sender_id']
        del sender['stickers']
        del sender['id']
        exc['sender'] = sender

    return exchanges


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
