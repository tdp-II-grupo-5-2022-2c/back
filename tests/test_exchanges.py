import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.db.impl.exchange_manager import GetExchangeManager
from app.db.impl.user_manager import UserManager, GetUserManager
from app.db.model.my_sticker import MyStickerModel
from app.db.model.user import UserModel
from app.db.model.exchange import ExchangeModel
from unittest.mock import MagicMock, AsyncMock, ANY


class TestExchangeManager(unittest.TestCase):
    def test_create_exchange(self):
        client = TestClient(app)
        exchangeManagerMock = MagicMock()
        userManagerMock = MagicMock()

        app.dependency_overrides[GetExchangeManager] = lambda: exchangeManagerMock
        app.dependency_overrides[GetUserManager] = lambda: userManagerMock

        exchangeManagerMock.get_pending_exchanges_by_sender_id = AsyncMock(return_value=[])

        fakeUser = UserModel(
            mail='dani@test.com',
            name='dani',
            lastname='test',
            date_of_birth='25/03/1997',
            country='ARG',
            is_profile_complete=True,
            stickers=[MyStickerModel(id='s1', is_on_album=False, quantity=2)]
        )
        userManagerMock.get_by_id = AsyncMock(return_value=fakeUser)
        userManagerMock.update = AsyncMock()
        fakeExchange = ExchangeModel(
            sender_id=str(fakeUser.id),
            stickers_to_give=['s1'],
            stickers_to_receive=['s3', 's4'],
        )
        exchangeManagerMock.add_new = AsyncMock(return_value=fakeExchange)

        body = {
            'sender_id': str(fakeUser.id),
            'stickers_to_give': ['s1'],
            'stickers_to_receive': ['s3', 's4'],
        }

        response = client.post('/exchanges', json=body)
        # sticker quantity decrements because now sticker belongs to exchange
        fakeUser.stickers[0].quantity -= 1

        assert response.status_code == 201
        userManagerMock.update.assert_called_once_with(str(fakeUser.id), fakeUser)
        fakeExchange.id = ANY
        exchangeManagerMock.add_new.assert_called_once_with(fakeExchange)

    def test_cannot_apply_action_to_completed_exchange(self):
        client = TestClient(app)
        exchangeManagerMock = MagicMock()
        userManagerMock = MagicMock()

        app.dependency_overrides[GetExchangeManager] = lambda: exchangeManagerMock
        app.dependency_overrides[GetUserManager] = lambda: userManagerMock

        exchangeManagerMock.get_pending_exchanges_by_sender_id = AsyncMock(return_value=[])

        fakeUser = UserModel(
            mail='dani@test.com',
            name='dani',
            lastname='test',
            date_of_birth='25/03/1997',
            country='ARG',
            is_profile_complete=True,
            stickers=[MyStickerModel(id='s1', is_on_album=False, quantity=2)]
        )
        userManagerMock.get_by_id = AsyncMock(return_value=fakeUser)

        fakeExchange = ExchangeModel(
            sender_id=str(fakeUser.id),
            stickers_to_give=['s1'],
            stickers_to_receive=['s3', 's4'],
            completed=True,
        )
        exchangeManagerMock.get_exchange_by_id = AsyncMock(return_value=fakeExchange)

        body = {
            'action': 'accept',
            'receiver_id': str(fakeUser.id),
        }

        response = client.post(f'/exchanges/{fakeExchange.id}', json=body)

        assert response.status_code == 400
        userManagerMock.get_by_id.assert_called_once_with(str(fakeUser.id))
        exchangeManagerMock.get_exchange_by_id.assert_called_once_with(str(fakeExchange.id))
        responseBody = response.json()
        assert responseBody['detail'] == f"exchange {fakeExchange.id} is completed, you cannot apply any action"
