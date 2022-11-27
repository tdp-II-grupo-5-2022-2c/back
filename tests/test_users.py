import json
import unittest
from unittest.mock import MagicMock, AsyncMock

from starlette.testclient import TestClient

from app.db.impl.user_manager import GetUserManager
from app.db.model.user import UserModel
from app.main import app


class TestUsersManager(unittest.TestCase):

    def test_put_daily_packages_successfully(self):
        client = TestClient(app)
        user_manager_mock = MagicMock()

        app.dependency_overrides[GetUserManager] = lambda: user_manager_mock

        user = UserModel(mail="mail1", name="name1", lastname="lastname1",
                         date_of_birth="birth1", has_daily_packages_available=True,
                         package_counter=1)
        user_manager_mock.get_by_id = AsyncMock(return_value=user)
        user_manager_mock.update = AsyncMock(return_value=user)

        response = client.put('/users/123/packages/daily-package')

        response_parsed = json.loads(response.content)
        assert response.status_code == 200
        assert response_parsed["has_daily_packages_available"] is False
        assert response_parsed["package_counter"] == 3

    def test_put_daily_packages_fails(self):
        client = TestClient(app)
        user_manager_mock = MagicMock()

        app.dependency_overrides[GetUserManager] = lambda: user_manager_mock

        user = UserModel(mail="mail1", name="name1", lastname="lastname1",
                         date_of_birth="birth1", has_daily_packages_available=False)
        user_manager_mock.get_by_id = AsyncMock(return_value=user)

        response = client.put('/users/123/packages/daily-package')

        assert response.status_code == 400

    def test_put_daily_packages_to_all_users(self):
        client = TestClient(app)
        user_manager_mock = MagicMock()

        app.dependency_overrides[GetUserManager] = lambda: user_manager_mock

        users_list = [
            UserModel(mail="mail1", name="name1", lastname="lastname1",
                      date_of_birth="birth1", has_daily_packages_available=False),
            UserModel(mail="mail1", name="name1", lastname="lastname1",
                      date_of_birth="birth1", has_daily_packages_available=False),
        ]

        user_manager_mock.get_all = AsyncMock(return_value=users_list)
        user_manager_mock.update = AsyncMock(return_value=200)

        response = client.put('/users/packages/daily-package')

        response_parsed = json.loads(response.content)
        assert response.status_code == 200
        assert response_parsed[0]["has_daily_packages_available"] is True
        assert response_parsed[1]["has_daily_packages_available"] is True
