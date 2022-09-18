import unittest
import pytest
from unittest.mock import MagicMock

from app.db.impl.user_manager import UserManager
from app.db.model.sticker import StickerModel
from app.db.model.package import PackageModel
from app.db.model.py_object_id import PyObjectId


class TestStickerManager(unittest.TestCase):
    db = MagicMock()

    @pytest.mark.asyncio
    async def test_get_sticker(self):
        # Given
        sticker = StickerModel(
            _id=PyObjectId("1"),
            image="img_messi.png",
            type="rare"
        )
        self.db["stickers"].find_one = MagicMock(return_value=sticker)

        sticker_manager = StickerManager(self.db)

        # When
        result = await sticker_manager.get_by_id("1")

        # Then
        self.assertIsNotNone(result)
        self.assertEqual("1", result.id)
        self.assertEqual("img_messi.png", result.image)
        self.assertEqual("rare", result.type)

    @pytest.mark.asyncio
    async def test_create_package(self):
        # Given
        in_package = []

        for i in range(5):
            sticker = StickerModel(
                _id=PyObjectId(f"{i}"),
                image=f"img_{i}.png",
                type="normal"
            )
            in_package.append(sticker)

        package = PackageModel(user_id="10", stickers=in_package)

        self.db["stickers"].find.to_list = MagicMock(return_value=in_package)

        sticker_manager = StickerManager(self.db)

        # When
        result = await sticker_manager.create_package("10")

        # Then
        self.assertIsNotNone(result)
        self.assertEqual("10", result.user_id)
        self.assertEqual("img_0.png", result.sticker[0].image)
        self.assertEqual("normal", result.sticker[0].type)
