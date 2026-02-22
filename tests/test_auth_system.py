import unittest

from src.auth_system import AuthManager, UserStore, require_roles


class AuthSystemTests(unittest.TestCase):
    def setUp(self):
        self.store = UserStore()
        self.store.add_user("admin", "Admin", "secret")
        self.auth = AuthManager(self.store, jwt_secret="test-secret")

    def test_admin_can_create_technician_with_auto_login(self):
        created = self.auth.create_technician("Admin", "tech1")
        self.assertEqual(created["role"], "Technician")
        login = self.auth.login("tech1", created["temp_password"])
        self.assertEqual(login["role"], "Technician")
        self.assertTrue(login["must_change_password"])

    def test_non_admin_cannot_create_technician(self):
        with self.assertRaises(PermissionError):
            self.auth.create_technician("Coordinator", "tech2")

    def test_secure_jwt_and_permission_middleware(self):
        token = self.auth.create_jwt("admin", "Admin", ttl_seconds=60)
        payload = self.auth.verify_jwt(token)
        self.assertEqual(payload["role"], "Admin")
        require_roles(payload, ["Admin", "Coordinator"])
        with self.assertRaises(PermissionError):
            require_roles(payload, ["Technician"])

    def test_password_reset(self):
        token = self.auth.request_password_reset("admin")
        self.auth.confirm_password_reset(token, "new-secret")
        login = self.auth.login("admin", "new-secret")
        self.assertEqual(login["role"], "Admin")


if __name__ == "__main__":
    unittest.main()
