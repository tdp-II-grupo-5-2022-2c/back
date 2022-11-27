import json
import unittest
from fastapi.testclient import TestClient

from app.db.impl.user_manager import GetUserManager
from app.db.model.user import UserModel
from app.db.model.sticker import StickerModel
from app.main import app
from app.db.impl.sticker_manager import GetStickerManager
from app.db.model.package_counter import PackageCounterModel
from app.firebase import GetFirebaseManager
from unittest.mock import MagicMock, AsyncMock
from app.db.impl.report_manager import GetReportManager


class TestStickersManager(unittest.TestCase):
    def test_get_stickers_default_paginated(self):
        client = TestClient(app)
        stickerManagerMock = MagicMock()
        app.dependency_overrides[GetStickerManager] = lambda: stickerManagerMock

        stickers = [
            StickerModel(
                name='s1',
                number=1,
                date_of_birth='1998-03-02',
                height=12.3,
                position=10,
                country='ARG',
                image='path/to/image',
            ),
            StickerModel(
                name='s2',
                number=2,
                date_of_birth='1998-03-02',
                height=13.3,
                position=11,
                country='ARG',
                image='path/to/image',
            ),
        ]
        stickerManagerMock.get_all = AsyncMock(return_value=stickers)

        response = client.get('/stickers')

        assert response.status_code == 200
        stickerManagerMock.get_all.assert_called_once_with(50, 1)
        assert len(response.json()) == len(stickers)

    def test_get_stickers_custom_paginated(self):
        client = TestClient(app)
        stickerManagerMock = MagicMock()
        app.dependency_overrides[GetStickerManager] = lambda: stickerManagerMock

        stickers = [
            StickerModel(
                name='s1',
                number=1,
                date_of_birth='1998-03-02',
                height=12.3,
                position=10,
                country='ARG',
                image='path/to/image',
            ),
            StickerModel(
                name='s2',
                number=2,
                date_of_birth='1998-03-02',
                height=13.3,
                position=11,
                country='ARG',
                image='path/to/image',
            ),
        ]
        stickerManagerMock.get_all = AsyncMock(return_value=stickers)

        response = client.get('/stickers?page=3&size=30')

        assert response.status_code == 200
        stickerManagerMock.get_all.assert_called_once_with(30, 3)
        assert len(response.json()) == len(stickers)