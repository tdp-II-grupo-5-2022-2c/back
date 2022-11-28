import json
import unittest
from fastapi.testclient import TestClient

from app.db.impl.user_manager import GetUserManager
from app.db.model.user import UserModel
from app.main import app
from app.db.impl.sticker_manager import GetStickerManager
from app.db.model.package_counter import PackageCounterModel
from app.firebase import GetFirebaseManager
from unittest.mock import MagicMock, AsyncMock
from app.db.impl.report_manager import GetReportManager


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

        response = client.get('/reports/stickers-metrics-freq?top5=True')

        assert response.status_code == 200
        stickerManagerMock.get_sticker_metrics_freq.assert_called_once_with(top5=True)
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

    def test_post_album_completion_report(self):
        client = TestClient(app)
        user_manager_mock = MagicMock()
        report_manager_mock = MagicMock()

        app.dependency_overrides[GetUserManager] = lambda: user_manager_mock
        app.dependency_overrides[GetReportManager] = lambda: report_manager_mock

        users_list = [
            UserModel(mail="mail1", name="name1", lastname="lastname1",
                      date_of_birth="birth1", album_completion_pct=10),
            UserModel(mail="mail1", name="name1", lastname="lastname1",
                      date_of_birth="birth1", album_completion_pct=10),
            UserModel(mail="mail1", name="name1", lastname="lastname1",
                      date_of_birth="birth1", album_completion_pct=20),
            UserModel(mail="mail1", name="name1", lastname="lastname1",
                      date_of_birth="birth1", album_completion_pct=30),
            UserModel(mail="mail1", name="name1", lastname="lastname1",
                      date_of_birth="birth1", album_completion_pct=35),
            UserModel(mail="mail1", name="name1", lastname="lastname1",
                      date_of_birth="birth1", album_completion_pct=40),
            UserModel(mail="mail1", name="name1", lastname="lastname1",
                      date_of_birth="birth1", album_completion_pct=70),
            UserModel(mail="mail1", name="name1", lastname="lastname1",
                      date_of_birth="birth1", album_completion_pct=80),
            UserModel(mail="mail1", name="name1", lastname="lastname1",
                      date_of_birth="birth1", album_completion_pct=100),
        ]

        user_manager_mock.get_all = AsyncMock(return_value=users_list)
        report_manager_mock.save_album_completion_report = AsyncMock(return_value=200)

        response = client.post('/reports/album-completion')

        response_parsed = json.loads(response.content)
        assert response.status_code == 200
        assert response_parsed["p20"] == 2
        assert response_parsed["p40"] == 3
        assert response_parsed["p60"] == 1
        assert response_parsed["p80"] == 1
        assert response_parsed["p100"] == 2

    def test_get_album_completion_report_fails(self):
        client = TestClient(app)
        report_manager_mock = MagicMock()

        app.dependency_overrides[GetReportManager] = lambda: report_manager_mock

        report_manager_mock.get_album_completion_report = AsyncMock(return_value=None)

        response = client.get('/reports/album-completion?date=01-03-2022')

        assert response.status_code == 404

    def test_get_register_info(self):
        client = TestClient(app)
        user_manager_mock = MagicMock()

        app.dependency_overrides[GetUserManager] = lambda: user_manager_mock

        info = {"2022-11-27": 2}
        user_manager_mock.get_register_info = AsyncMock(return_value=info)

        response = client.get('/reports/registered-users')

        response_parsed = json.loads(response.content)
        assert response.status_code == 200
        assert response_parsed["2022-11-27"] is 2
