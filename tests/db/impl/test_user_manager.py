import unittest
import pytest
from unittest.mock import MagicMock

from app.db.impl.user_manager import UserManager
from app.db.model.user import UserModel
from app.db.model.my_sticker import MyStickerModel
from app.db.model.py_object_id import PyObjectId

class TestUserManager(unittest.TestCase):
    db = MagicMock()

    @pytest.mark.asyncio
    async def test_get_user(self):
        sticker = MyStickerModel(
            id="sticker_id",
            is_on_album=False,
            quantity=2
        )
        user = UserModel(
            _id=PyObjectId("1"),
            mail="usermail@gmail.com",
            stickers=[]
        )
        self.db["users"].find_one = MagicMock(return_value=user)

        user_manager = UserManager(self.db)
        result = await user_manager.get_by_id("1")
        self.assertIsNotNone(result)