import unittest
import pytest
from unittest.mock import MagicMock

from app.db.impl.user_manager import UserManager
from app.db.model.sticker import StickerModel
from app.db.model.user import UserModel
from app.db.model.my_sticker import MyStickerModel
from app.db.model.package import PackageModel
from app.db.model.py_object_id import PyObjectId


class TestUserManager(unittest.TestCase):
    db = MagicMock()

    @pytest.mark.asyncio
    async def test_get_user(self):
        # Given
        user = UserModel(
            _id=PyObjectId("1"),
            mail="usermail@gmail.com",
            name="Daniela",
            lastname="Sua",
            date_of_birth="28-07-12",
            stickers_on_album=0,
            stickers_on_my_stickers_section=0,
            total_stickers_collected=0,
            album_completion_pct=0,
            exchanges_amount=0,
            stickers=[],
            register_date="2022-11-02"
        )
        self.db["users"].find_one = MagicMock(return_value=user)

        user_manager = UserManager(self.db)

        # When
        result = await user_manager.get_by_id("1")

        # Then
        self.assertIsNotNone(result)
        self.assertEqual("1", result.id)
        self.assertEqual("usermail@gmail.com", result.mail),
        self.assertEqual("Daniela", result.name)
        self.assertEqual("Sua", result.lastname)
        self.assertEqual("28-07-12", result.date_of_birth)
        self.assertEqual(0, result.stickers_on_album)
        self.assertEqual(0, result.stickers_on_my_stickers_section)
        self.assertEqual(0, result.total_stickers_collected)
        self.assertEqual(0, result.album_completion_pct)
        self.assertEqual(0, result.exchanges_amount)

    @pytest.mark.asyncio
    async def test_get_user_by_mail(self):
        # Given
        user = UserModel(
            _id=PyObjectId("1"),
            mail="usermail@gmail.com",
            stickers=[],
            name="Maria",
            lastname="Sra",
            date_of_birth="28-04-12",
            stickers_on_album=0,
            stickers_on_my_stickers_section=0,
            total_stickers_collected=0,
            album_completion_pct=0,
            exchanges_amount=0,
            register_date="2022-11-02"
        )
        self.db["users"].find_one = MagicMock(return_value=user)

        user_manager = UserManager(self.db)

        # When
        result = await user_manager.get_user_by_mail("usermail@gmail.com")

        # Then
        self.assertIsNotNone(result)
        self.assertEqual("1", result.id)
        self.assertEqual("usermail@gmail.com", result.mail)
        self.assertEqual("Maria", result.name)
        self.assertEqual("Sra", result.lastname)
        self.assertEqual("28-04-12", result.date_of_birth)
        self.assertEqual(0, result.stickers_on_album)
        self.assertEqual(0, result.stickers_on_my_stickers_section)
        self.assertEqual(0, result.total_stickers_collected)
        self.assertEqual(0, result.album_completion_pct)
        self.assertEqual(0, result.exchanges_amount)

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
            stickers=[sticker],
            name="Maria",
            lastname="Sra",
            date_of_birth="28-04-12",
            stickers_on_album=0,
            stickers_on_my_stickers_section=2,
            total_stickers_collected=2,
            album_completion_pct=0,
            exchanges_amount=0,
            register_date="2022-11-02"
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
        self.assertEqual(0, result.stickers_on_album)
        self.assertEqual(2, result.stickers_on_my_stickers_section)
        self.assertEqual(2, result.total_stickers_collected)
        self.assertEqual(0, result.album_completion_pct)
        self.assertEqual(0, result.exchanges_amount)

    @pytest.mark.asyncio
    async def test_paste_sticker(self):
        # Given
        sticker_paste = MyStickerModel(
            id="sticker_id",
            is_on_album=True,
            quantity=1
        )

        user_after_paste = UserModel(
            _id=PyObjectId("2"),
            mail="usermail@gmail.com",
            stickers=[sticker_paste],
            name="Maria",
            lastname="Sra",
            date_of_birth="28-04-12",
            stickers_on_album=1,
            stickers_on_my_stickers_section=0,
            total_stickers_collected=1,
            album_completion_pct=0.001,
            exchanges_amount=0,
            register_date="2022-11-02"
        )

        self.db["users"].find_one = MagicMock(return_value=user_after_paste)
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
        self.assertEqual(1, result.stickers_on_album)
        self.assertEqual(0, result.stickers_on_my_stickers_section)
        self.assertEqual(1, result.total_stickers_collected)
        self.assertEqual(0.001, result.album_completion_pct)
        self.assertEqual(0, result.exchanges_amount)

    @pytest.mark.asyncio
    async def test_open_package_with_repeated_stickers(self):
        # Given
        in_package = []
        my_stickers = []
        for i in range(5):
            sticker = StickerModel(
                _id=PyObjectId(f"{i}"),
                image=f"img_{i}.png",
                type="normal"
            )
            my_sticker = MyStickerModel(
                _id=f"{i}",
                quantity=1,
                is_on_album=False
            )
            my_stickers.append(my_sticker)
            in_package.append(sticker)

        package = PackageModel(user_id="10", stickers=in_package)

        user = UserModel(
            _id=PyObjectId("10"),
            mail="usermail@gmail.com",
            stickers=my_stickers,
            name="Maria",
            lastname="Sra",
            date_of_birth="28-04-12",
            stickers_on_album=0,
            stickers_on_my_stickers_section=5,
            total_stickers_collected=5,
            album_completion_pct=0.,
            exchanges_amount=0,
            register_date="2022-11-02"
        )

        self.db["users"].update_one = MagicMock(return_value=True)
        self.db["users"].find_one = MagicMock(return_value=user)

        user_manager = UserManager(self.db)

        # When
        result = await user_manager.open_package(package)

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        self.assertEqual("10", result[0].id)
        self.assertEqual(5, len(result.stickers[0]))
        self.assertEqual("1", result.stickers[0].id)
        self.assertEqual(1, result.stickers[0].quantity)
        self.assertEqual(False, result.stickers[0].is_on_album)
        self.assertEqual(0, result.stickers_on_album)
        self.assertEqual(5, result.stickers_on_my_stickers_section)
        self.assertEqual(5, result.total_stickers_collected)
        self.assertEqual(0, result.album_completion_pct)
        self.assertEqual(0, result.exchanges_amount)

    @pytest.mark.asyncio
    async def test_open_package_with_non_repeated_stickers(self):
        # Given
        in_package = []
        my_stickers = []
        for i in range(5):
            sticker = StickerModel(
                _id=PyObjectId(f"{i}"),
                image=f"img_{i}.png",
                type="normal"
            )
            my_sticker = MyStickerModel(
                _id=f"{i}",
                quantity=1,
                is_on_album=False
            )
            my_stickers.append(my_sticker)
            in_package.append(sticker)

        package = PackageModel(user_id="10", stickers=in_package)

        user = UserModel(
            _id=PyObjectId("10"),
            mail="usermail@gmail.com",
            stickers=my_stickers,
            name="Maria",
            lastname="Sra",
            date_of_birth="28-04-12",
            stickers_on_album=0,
            stickers_on_my_stickers_section=5,
            total_stickers_collected=5,
            album_completion_pct=0.,
            exchanges_amount=0,
            register_date="2022-11-02"
        )

        self.db["users"].update_one = MagicMock(return_value=False)
        self.db["users"].find_one = MagicMock(return_value=user)

        user_manager = UserManager(self.db)

        # When
        result = await user_manager.open_package(package)

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        self.assertEqual("10", result[0].id)
        self.assertEqual(5, len(result.stickers[0]))
        self.assertEqual("1", result.stickers[0].id)
        self.assertEqual(1, result.stickers[0].quantity)
        self.assertEqual(False, result.stickers[0].is_on_album)
        self.assertEqual(0, result.stickers_on_album)
        self.assertEqual(5, result.stickers_on_my_stickers_section)
        self.assertEqual(5, result.total_stickers_collected)
        self.assertEqual(0, result.album_completion_pct)
        self.assertEqual(0, result.exchanges_amount)

    @pytest.mark.asyncio
    async def test_get_user_by_mail(self):
        # Given
        info = {
            "28-04-12": 1
        }
        self.db["users"].aggregate = MagicMock(return_value=info)

        user_manager = UserManager(self.db)

        # When
        result = await user_manager.get_register_info()

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(1, result["2022-11-12"])
        