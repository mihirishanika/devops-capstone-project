import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"

class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        pass

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test"""
        db.session.remove()

    def _create_account(self):
        """Helper: Create an account using the factory and API"""
        account = AccountFactory()
        response = self.client.post(BASE_URL, json=account.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.get_json()

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(BASE_URL, json=account.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], account.name)

    def test_list_accounts(self):
        """It should List all accounts"""
        for _ in range(3):
            self._create_account()
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)

    def test_read_an_account(self):
        """It should Read a single Account"""
        created = self._create_account()
        account_id = created["id"]
        response = self.client.get(f"{BASE_URL}/{account_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["id"], account_id)

    def test_read_account_not_found(self):
        """It should return 404 when account not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_account(self):
        """It should Update an existing Account"""
        created = self._create_account()
        account_id = created["id"]
        updated_data = created.copy()
        updated_data["name"] = "Updated Name"
        response = self.client.put(f"{BASE_URL}/{account_id}", json=updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Updated Name")

    def test_update_account_not_found(self):
        """It should return 404 when updating non-existent account"""
        updated_data = {"name": "No Account"}
        response = self.client.put(f"{BASE_URL}/0", json=updated_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_account(self):
        """It should Delete an existing Account"""
        created = self._create_account()
        account_id = created["id"]
        response = self.client.delete(f"{BASE_URL}/{account_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Confirm it's deleted
        get_resp = self.client.get(f"{BASE_URL}/{account_id}")
        self.assertEqual(get_resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_account_not_found(self):
        """It should return 404 when deleting non-existent account"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
