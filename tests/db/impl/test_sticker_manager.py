import unittest
import pytest
from unittest.mock import MagicMock

from app.db.impl.user_manager import UserManager
from app.db.model.sticker import StickerModel
from app.db.model.package import PackageModel
from app.db.model.py_object_id import PyObjectId
from app.db.impl.sticker_manager import StickerManager


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
    async def test_get_sticker_by_query(self):
        # Given
        sticker = StickerModel(
            _id=PyObjectId("1"),
            image="img_mbappe.png",
            country="Francia",
            weight=5
        )
        sticker_2 = StickerModel(
            _id=PyObjectId("2"),
            image="img_messi.png",
            country="Argentina",
            name="Messi",
            weight=5
        )
        self.db["stickers"].find = MagicMock(return_value=[sticker_2])

        sticker_manager = StickerManager(self.db)

        # When
        result = await sticker_manager.get_by_query(
            ["1", "2"], "Argentina", "Messi"
        )

        # Then
        self.assertIsNotNone(result)
        self.assertEqual("2", result[0].id)
        self.assertEqual("img_messi.png", result[0].image)
        self.assertEqual(5, result[0].weight)
        self.assertEqual("Argentina", result[0].country)
        self.assertEqual("Messi", result[0].name)

    @pytest.mark.asyncio
    async def test_create_normal_package(self):

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

        self.db["package-counter"].find_one = MagicMock(return_value=1)
        self.db["stickers"].find.to_list = MagicMock(return_value=package)
        self.db["package-counter"].update_one = MagicMock()

        sticker_manager = StickerManager(self.db)

        # When
        result = await sticker_manager.create_package()

        # Then
        self.assertIsNotNone(result)
        self.assertEqual("img_0.png", result.sticker[0].image)
        self.assertEqual(1, result.sticker[0].weight)

    @pytest.mark.asyncio
    async def test_create_special_package(self):
        # Given
        in_package = []

        for i in range(2):
            sticker = StickerModel(
                _id=PyObjectId(f"{i}"),
                image=f"img_{i}.png",
                weight=1
            )
            in_package.append(sticker)

        for i in range(2):
            sticker = StickerModel(
                _id=PyObjectId(f"{2 + i}"),
                image=f"img_{2 + i}.png",
                weight=4
            )
            in_package.append(sticker)

        sticker = StickerModel(
            _id=PyObjectId(f"4"),
            image=f"img_4.png",
            weight=5
        )
        in_package.append(sticker)

        package = PackageModel(stickers=in_package)

        self.db["package-counter"].find_one = MagicMock(return_value=11)
        self.db["stickers"].find.to_list = MagicMock(return_value=package)
        self.db["package-counter"].update_one = MagicMock()

        sticker_manager = StickerManager(self.db)

        # When
        result = await sticker_manager.create_package()

        # Then
        self.assertIsNotNone(result)
        self.assertEqual("img_0.png", result.sticker[0].image)
        self.assertEqual(1, result.sticker[0].weight)
        self.assertEqual(1, result.sticker[1].weight)
        self.assertEqual(4, result.sticker[2].weight)
        self.assertEqual(4, result.sticker[3].weight)
        self.assertEqual(5, result.sticker[4].weight)
