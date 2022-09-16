import unittest
import pytest
from unittest.mock import MagicMock

from app.db.impl.user_manager import UserManager, UserModel
from app.db.model.py_object_id import PyObjectId

class TestUserManager(unittest.TestCase):
    db = MagicMock()

    @pytest.mark.asyncio
    async def test_get_user(self):
        user = UserModel(
            _id=PyObjectId("62be27922d98b5aaad951f95"),
            user_id="user_id"
        )
        self.db["users"].find_one = MagicMock(return_value=user)

        user_manager = UserManager(self.db)
        result = await user_manager.get_by_id("62be27922d98b5aaad951f95")
        self.assertIsNotNone(result)