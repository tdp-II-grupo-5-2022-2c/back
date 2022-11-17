import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.db.impl.exchange_manager import GetExchangeManager
from app.db.impl.user_manager import UserManager, GetUserManager
from app.db.model.my_sticker import MyStickerModel
from app.db.model.user import UserModel
from app.db.model.exchange import ExchangeModel
from unittest.mock import MagicMock, AsyncMock
import requests


class TestStickerManager(unittest.TestCase):
    def test_get_exchange(self):
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
            sender_id= str(fakeUser.id),
            stickers_to_give= ['s1'],
            stickers_to_receive= ['s3', 's4'],
        )
        exchangeManagerMock.add_new = AsyncMock(return_value=fakeExchange)

        body = {
            'sender_id': str(fakeUser.id),
            'stickers_to_give': ['s1'],
            'stickers_to_receive': ['s3', 's4'],
        }

        response = client.post('/exchanges', json=body)
        fakeUser.stickers[0].quantity -= 1

        assert response.status_code == 201
        userManagerMock.update.assert_called_once_with(str(fakeUser.id), fakeUser)
        # ToDo assert response body y los otros mocks
