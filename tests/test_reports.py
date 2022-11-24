import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.db.impl.sticker_manager import GetStickerManager, StickerManager
from app.db.impl.user_manager import UserManager, GetUserManager
from app.db.model.package_counter import PackageCounterModel
from app.db.model.user import UserModel
from app.firebase import FirebaseManager, GetFirebaseManager
from unittest.mock import MagicMock, AsyncMock, ANY, Mock
import requests


class TestReportsManager(unittest.TestCase):
    def test_get_top_5_report(self):
        client = TestClient(app)
        stickerManagerMock = MagicMock()
        app.dependency_overrides[GetStickerManager] = lambda: stickerManagerMock

        top5List = [
            {'name': 'Julian Alvarez', 'country': 'ARG', 'counter': 1},
            {'name': 'Lionel Messi', 'country': 'ARG', 'counter': 1},
            {'name': 'Neymar Junior', 'country': 'BRA', 'counter': 2},
            {'name': 'Casco', 'country': 'URU', 'counter': 8},
            {'name': 'Gary Medel', 'country': 'CHI', 'counter': 34},
        ]
        stickerManagerMock.get_sticker_metrics_freq = AsyncMock(return_value=top5List)
        stickerManagerMock.get_package_counter = AsyncMock(return_value=PackageCounterModel(counter=10))

        response = client.get('/reports/stickers-metrics-freq?top5=True')

        assert response.status_code == 200
        stickerManagerMock.get_sticker_metrics_freq.assert_called_once_with(top5=True)
        for s in top5List:
            s['percentage'] = round(s['counter'] / 10 * 100, 2)

        assert response.json() == top5List

    def test_unexpected_error_calling_mongo(self):
        client = TestClient(app)
        stickerManagerMock = MagicMock()
        app.dependency_overrides[GetStickerManager] = lambda: stickerManagerMock

        stickerManagerMock.get_sticker_metrics_freq = AsyncMock(side_effect=Exception('mongo died'))

        response = client.get('/reports/stickers-metrics-freq?top5=True')

        assert response.status_code == 500
        stickerManagerMock.get_sticker_metrics_freq.assert_called_once_with(top5=True)
        assert response.json()['detail'] == 'Unexpected error getting stickers freq report. Exception: mongo died'

    def test_get_distribution_freq_stickers_and_generate_bin(self):
        client = TestClient(app)
        stickerManagerMock = MagicMock()
        firebaseManagerMock = MagicMock()
        app.dependency_overrides[GetStickerManager] = lambda: stickerManagerMock
        app.dependency_overrides[GetFirebaseManager] = lambda: firebaseManagerMock

        freqList = [
            {'name': 'Julian Alvarez', 'country': 'ARG', 'counter': 1},
            {'name': 'Lionel Messi', 'country': 'ARG', 'counter': 1},
            {'name': 'Neymar Junior', 'country': 'BRA', 'counter': 2},
            {'name': 'Casco', 'country': 'URU', 'counter': 8},
            {'name': 'Gary Medel', 'country': 'CHI', 'counter': 34},
        ]
        stickerManagerMock.get_sticker_metrics_freq = AsyncMock(return_value=freqList)
        stickerManagerMock.get_package_counter = AsyncMock(return_value=PackageCounterModel(counter=12))
        firebaseManagerMock.uploadFile = MagicMock(return_value='ok')

        response = client.get('/reports/stickers-metrics-freq?generate_binary=true')

        for s in freqList:
            s['percentage'] = round(s['counter'] / 12 * 100, 2)

        assert response.status_code == 200
        firebaseManagerMock.uploadFile.assert_called_once_with('stickers_freq.csv')
        assert response.json() == freqList

