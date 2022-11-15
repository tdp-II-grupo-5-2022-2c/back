from fastapi.testclient import TestClient
from app.main import app
from app.db import get_database
from .mock_mongo_manager import MockMongoManager
from unittest.mock import MagicMock, AsyncMock
import pytest


@pytest.mark.asyncio
def test_get_exchange():
    client = TestClient(app)

    db = MockMongoManager()
    db.db = AsyncMock()

    app.dependency_overrides[get_database] = lambda: db

    body = {
        'sender_id': 'fake-user-id',
        'stickers_to_give': ['s1', 's2'],
        'stickers_to_receive': ['s3', 's4'],
        'blacklist_user_ids': [],
    }

    db.db["exchanges"].find.to_list.return_value = []

    response = client.post('/exchanges', json=body)
    assert response.status_code == 200
