import unittest

from app import create_app
from app.extensions import db
from app.users.models import User


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def register(self, username="nazar", email="nazar@example.com", password="secret123"):
        return self.client.post("/users/register", data={
            "username": username, "email": email,
            "password": password, "confirm_password": password,
        }, follow_redirects=True)

    def logout(self):
        return self.client.get("/users/logout", follow_redirects=True)

    def test_registration_page_loads(self):
        response = self.client.get("/users/register")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Username", response.data)

    def test_login_page_loads(self):
        response = self.client.get("/users/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Email", response.data)

    def test_registration_saves_bcrypt_hash_and_logs_user_in(self):
        response = self.register()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Вітаємо, nazar".encode(), response.data)
        user = db.session.scalar(db.select(User).where(User.email == "nazar@example.com"))
        self.assertIsNotNone(user)
        self.assertNotEqual(user.password, "secret123")
        self.assertTrue(user.check_password("secret123"))

    def test_duplicate_username_is_rejected(self):
        self.register()
        self.logout()
        response = self.client.post("/users/register", data={
            "username": "nazar", "email": "other@example.com",
            "password": "secret123", "confirm_password": "secret123",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("вже зайняте".encode(), response.data)

    def test_duplicate_email_is_rejected(self):
        self.register()
        self.logout()
        response = self.client.post("/users/register", data={
            "username": "another", "email": "nazar@example.com",
            "password": "secret123", "confirm_password": "secret123",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("вже зареєстрований".encode(), response.data)

    def test_password_confirmation_is_validated(self):
        response = self.client.post("/users/register", data={
            "username": "nazar", "email": "nazar@example.com",
            "password": "secret123", "confirm_password": "different",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(db.session.scalar(db.select(User)))

    def test_login_and_logout(self):
        self.register()
        self.logout()
        response = self.client.post("/users/login", data={
            "email": "nazar@example.com", "password": "secret123",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Вітаємо, nazar".encode(), response.data)
        response = self.logout()
        self.assertIn("Вхід".encode(), response.data)

    def test_invalid_login_is_rejected(self):
        self.register()
        self.logout()
        response = self.client.post("/users/login", data={
            "email": "nazar@example.com", "password": "wrong-password",
        }, follow_redirects=True)
        self.assertIn("Неправильна електронна пошта або пароль".encode(), response.data)

    def test_account_and_users_list_require_login(self):
        self.assertEqual(self.client.get("/users/account").status_code, 302)
        self.assertEqual(self.client.get("/users/all").status_code, 302)
        self.register()
        self.assertEqual(self.client.get("/users/account").status_code, 200)
        users_response = self.client.get("/users/all")
        self.assertEqual(users_response.status_code, 200)
        self.assertIn(b"(1)", users_response.data)


if __name__ == "__main__":
    unittest.main()
