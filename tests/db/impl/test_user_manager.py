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
        # Given
        user = UserModel(
            _id=PyObjectId("1"),
            mail="usermail@gmail.com",
            stickers=[]
        )
        self.db["users"].find_one = MagicMock(return_value=user)

        user_manager = UserManager(self.db)

        # When
        result = await user_manager.get_by_id("1")

        # Then
        self.assertIsNotNone(result)
        self.assertEqual("1", result.id)
        self.assertEqual("usermail@gmail.com", result.mail)

    @pytest.mark.asyncio
    async def test_get_stickers_by_user(self):
        # Given
        sticker = MyStickerModel(
            id="sticker_id",
            is_on_album=False,
            quantity=2
        )
        user = UserModel(
            _id=PyObjectId("2"),
            mail="usermail@gmail.com",
            stickers=[sticker]
        )

        self.db["users"].find_one = MagicMock(return_value=user)

        user_manager = UserManager(self.db)

        # When
        result = await user_manager.get_stickers("2")

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        self.assertEqual("sticker_id", result[0].id)
        self.assertEqual(False, result[0].is_on_album)
        self.assertEqual(2, result[0].quantity)

    @pytest.mark.asyncio
    async def test_paste_sticker(self):
        # Given
        sticker_paste = MyStickerModel(
            id="sticker_id",
            is_on_album=True,
            quantity=1
        )

        user_aftere_paste = UserModel(
            _id=PyObjectId("2"),
            mail="usermail@gmail.com",
            stickers=[sticker_paste]
        )

        self.db["users"].find_one = MagicMock(return_value=user_aftere_paste)
        self.db["users"].update_one = MagicMock(return_value=True)

        user_manager = UserManager(self.db)

        # When
        result = await user_manager.paste_sticker(user_id="2", sticker_id="sticker_id")

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        self.assertEqual("sticker_id", result[0].id)
        self.assertEqual(True, result[0].is_on_album)
        self.assertEqual(1, result[0].quantity)

        self.db["users"].update_one = MagicMock(return_value=True)

