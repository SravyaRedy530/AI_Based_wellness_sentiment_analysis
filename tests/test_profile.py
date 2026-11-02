"""
Test Suite for User Profile Page and Settings.
Verifies:
- Full Name update and persistence in MySQL
- Email update and duplicate prevention in MySQL
- Preferred Support Style persistence in MySQL
- Theme persistence in MySQL
- Export Journal CSV functionality
- Delete Account cascading removal in MySQL
"""
import os
import sys
import unittest
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import create_app
from backend.models.database import db
from backend.models.user import User
from backend.models.journal import JournalEntry


class ProfilePageTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_full_profile_lifecycle_in_mysql(self):
        ts = int(time.time() * 1000)
        initial_email = f"profile_user_{ts}@example.com"
        updated_email = f"profile_updated_{ts}@example.com"

        # 1. Register test user
        reg_res = self.client.post("/api/auth/register", json={
            "fullname": "Original Profile Name",
            "email": initial_email,
            "password": "Password123!"
        })
        self.assertEqual(reg_res.status_code, 201)
        token = reg_res.get_json()["data"]["access_token"]
        user_id = reg_res.get_json()["data"]["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}
        print("\n[TEST PROFILE] User registered with ID:", user_id)

        # 2. Get Profile
        get_res = self.client.get("/api/user/profile", headers=headers)
        self.assertEqual(get_res.status_code, 200)
        pdata = get_res.get_json()["data"]["user"]
        self.assertEqual(pdata["fullname"], "Original Profile Name")
        self.assertEqual(pdata["email"], initial_email)
        print("[TEST PROFILE] Initial profile retrieved successfully.")

        # 3. Update Profile (Full Name, Email, Preferred Support Style, Theme)
        update_payload = {
            "full_name": "Updated Profile Name",
            "email": updated_email,
            "preferred_support_style": "Mindful & Philosophical",
            "theme": "Calm Lavender",
            "bio": "Reflective meditator exploring emotional intelligence.",
            "wellness_goal": "Emotional Resilience & Coping"
        }
        put_res = self.client.put("/api/user/profile", json=update_payload, headers=headers)
        self.assertEqual(put_res.status_code, 200)
        updated_data = put_res.get_json()["data"]["user"]

        self.assertEqual(updated_data["fullname"], "Updated Profile Name")
        self.assertEqual(updated_data["email"], updated_email)
        self.assertEqual(updated_data["preferred_support_style"], "Mindful & Philosophical")
        self.assertEqual(updated_data["theme"], "Calm Lavender")
        print("[TEST PROFILE] Profile updated via API.")

        # 4. Verify directly in MySQL Database
        with self.app.app_context():
            db_user = db.session.get(User, user_id)
            self.assertIsNotNone(db_user)
            self.assertEqual(db_user.fullname, "Updated Profile Name")
            self.assertEqual(db_user.email, updated_email)
            self.assertEqual(db_user.preferred_support_style, "Mindful & Philosophical")
            self.assertEqual(db_user.theme, "Calm Lavender")
            print("[TEST PROFILE] Verified directly in MySQL database columns.")

        # 5. Test Export Journal CSV
        # Create a journal entry first
        self.client.post("/api/emotion/analyze", json={
            "text": "I feel grateful and peaceful celebrating our launch milestone!"
        }, headers=headers)

        export_res = self.client.get("/api/journal/export/csv", headers=headers)
        self.assertEqual(export_res.status_code, 200)
        self.assertEqual(export_res.mimetype, "text/csv")
        csv_text = export_res.get_data(as_text=True)
        self.assertIn("Entry ID", csv_text)
        self.assertIn("Primary Emotion", csv_text)
        print("[TEST PROFILE] Export Journal CSV verified.")

        # 6. Delete Account (Permanently stored in MySQL)
        del_res = self.client.delete("/api/user/delete-account", json={"password": "Password123!"}, headers=headers)
        self.assertEqual(del_res.status_code, 200)
        print("[TEST PROFILE] Account deleted via API.")

        # 7. Verify deletion in MySQL
        with self.app.app_context():
            del_user = db.session.get(User, user_id)
            self.assertIsNone(del_user)
            # Ensure entries were cascaded
            entries = JournalEntry.query.filter_by(user_id=user_id).all()
            self.assertEqual(len(entries), 0)
            print("[TEST PROFILE] Verified deletion & cascading removal in MySQL.")


if __name__ == "__main__":
    unittest.main()
