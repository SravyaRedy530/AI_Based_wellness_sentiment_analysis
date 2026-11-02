"""
Comprehensive Test Suite for Secure Authentication.
Tests:
- Register
- Login
- Logout (JWT Token Revocation)
- Password Hashing (bcrypt salted verification)
- JWT Authentication (Bearer authorization)
- Email Validation
- Duplicate Email Prevention
- MySQL Database Connectivity
"""
import os
import sys
import unittest
import pymysql

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import create_app
from backend.models.database import db
from backend.models.user import User, TokenBlocklist


class SecureAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def test_1_email_validation(self):
        """Tests that invalid email formats are rejected with 400 Bad Request."""
        invalid_emails = [
            "plainaddress",
            "@missingusername.com",
            "username@.com",
            "username@domain..com",
            "user spaces@domain.com"
        ]
        for bad_email in invalid_emails:
            res = self.client.post("/api/auth/register", json={
                "fullname": "Validation Tester",
                "email": bad_email,
                "password": "ValidPassword123!"
            })
            self.assertEqual(res.status_code, 400, f"Expected 400 for bad email: {bad_email}")
            self.assertIn("valid email address", res.get_json()["message"].lower())
        print("[TEST 1/6] Email format validation passed.")

    def test_2_register_and_password_hashing(self):
        """Tests successful registration and confirms password is encrypted with bcrypt."""
        test_email = "secure_auth_test@example.com"
        raw_password = "SecretPassword!2026"

        with self.app.app_context():
            existing = User.query.filter_by(email=test_email).first()
            if existing:
                db.session.delete(existing)
                db.session.commit()

        # 1. Register
        res = self.client.post("/api/auth/register", json={
            "fullname": "Sravya Wellness",
            "email": test_email,
            "password": raw_password
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()["data"]
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["fullname"], "Sravya Wellness")
        self.assertEqual(data["user"]["email"], test_email)

        # 2. Verify Bcrypt Hashing directly in database
        with self.app.app_context():
            user_in_db = User.query.filter_by(email=test_email).first()
            self.assertIsNotNone(user_in_db)
            self.assertNotEqual(user_in_db.password, raw_password)
            self.assertTrue(user_in_db.password.startswith("$2b$") or user_in_db.password.startswith("$2a$"))
            # Test check_password
            self.assertTrue(user_in_db.check_password(raw_password))
            self.assertFalse(user_in_db.check_password("WrongPassword123!"))

        print("[TEST 2/6] User registration and salted bcrypt hashing verified.")

    def test_3_duplicate_email_prevention(self):
        """Tests that attempting to register with an existing email returns 409 Conflict."""
        test_email = "secure_auth_test@example.com"

        res = self.client.post("/api/auth/register", json={
            "fullname": "Another Person",
            "email": test_email,
            "password": "AnotherPassword123!"
        })
        self.assertEqual(res.status_code, 409)
        self.assertIn("already registered", res.get_json()["message"].lower())
        print("[TEST 3/6] Duplicate email prevention verified (HTTP 409 Conflict).")

    def test_4_login_flow(self):
        """Tests login with valid credentials and failure with invalid credentials."""
        test_email = "secure_auth_test@example.com"
        correct_pwd = "SecretPassword!2026"

        # Incorrect password
        fail_res = self.client.post("/api/auth/login", json={
            "email": test_email,
            "password": "WrongPassword999"
        })
        self.assertEqual(fail_res.status_code, 401)
        self.assertIn("invalid", fail_res.get_json()["message"].lower())

        # Correct login
        success_res = self.client.post("/api/auth/login", json={
            "email": test_email,
            "password": correct_pwd
        })
        self.assertEqual(success_res.status_code, 200)
        data = success_res.get_json()["data"]
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["email"], test_email)
        print("[TEST 4/6] Login authentication and credential verification passed.")

    def test_5_jwt_protected_route_and_logout_revocation(self):
        """Tests JWT Bearer authorization and token revocation upon Logout."""
        test_email = "secure_auth_test@example.com"
        correct_pwd = "SecretPassword!2026"

        # 1. Login to get token
        login_res = self.client.post("/api/auth/login", json={
            "email": test_email,
            "password": correct_pwd
        })
        token = login_res.get_json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Access protected endpoint /api/auth/me
        me_res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.get_json()["data"]["user"]["email"], test_email)

        # 3. Call Logout to revoke the token
        logout_res = self.client.post("/api/auth/logout", headers=headers)
        self.assertEqual(logout_res.status_code, 200)
        self.assertIn("logged out", logout_res.get_json()["message"].lower())

        # 4. Attempt to access protected route again with the SAME revoked token
        revoked_res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(revoked_res.status_code, 401)
        self.assertEqual(revoked_res.get_json().get("error"), "token_revoked")
        print("[TEST 5/6] JWT protection and secure token revocation (Logout) passed.")

    def test_6_mysql_direct_connectivity(self):
        """Verifies direct MySQL connection and users table inspection."""
        try:
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="12345",
                database="moodmentor_db",
                port=3306
            )
            with conn.cursor() as cursor:
                cursor.execute("DESCRIBE users;")
                columns = [row[0] for row in cursor.fetchall()]
                self.assertIn("id", columns)
                self.assertIn("fullname", columns)
                self.assertIn("email", columns)
                self.assertIn("password", columns)
                self.assertIn("created_at", columns)
            conn.close()
            print("[TEST 6/6] MySQL direct database connectivity and schema verified.")
        except Exception as e:
            self.fail(f"MySQL connectivity failed: {e}")


if __name__ == "__main__":
    unittest.main()
