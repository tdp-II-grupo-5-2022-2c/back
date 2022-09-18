import unittest
from unittest.mock import MagicMock

import pytest

from app.db.impl.sticker_manager import StickerManager
from app.db.model.package import PackageModel
from app.db.model.py_object_id import PyObjectId
from app.db.model.sticker import StickerModel


class TestStickerManager(unittest.TestCase):
    db = MagicMock()

    @pytest.mark.asyncio
    async def test_get_sticker(self):
        # Given
        sticker = StickerModel(
            _id=PyObjectId("1"),
            image="img_messi.png",
            weight=5
        )
        self.db["stickers"].find_one = MagicMock(return_value=sticker)

        sticker_manager = StickerManager(self.db)

        # When
        result = await sticker_manager.get_by_id("1")

        # Then
        self.assertIsNotNone(result)
        self.assertEqual("1", result.id)
        self.assertEqual("img_messi.png", result.image)
        self.assertEqual(5, result.weight)

    @pytest.mark.asyncio
    async def test_create_package(self):
        # Given
        in_package = []

        for i in range(5):
            sticker = StickerModel(
                _id=PyObjectId(f"{i}"),
                image=f"img_{i}.png",
                weight=1
            )
            in_package.append(sticker)

        package = PackageModel(stickers=in_package)

        self.db["stickers"].find.to_list = MagicMock(return_value=package)

        sticker_manager = StickerManager(self.db)

        # When
        result = await sticker_manager.create_package()

        # Then
        self.assertIsNotNone(result)
        self.assertEqual("img_0.png", result.sticker[0].image)
        self.assertEqual(1, result.sticker[0].weight)