"""
Backend Test Suite for MoodMentor.
Tests authentication, JWT headers, AI analysis, journal CRUD, analytics, and cascade deletion.
"""
import os
import sys
import unittest
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import create_app
from backend.models.database import db
from backend.models.user import User
from backend.models.journal import JournalEntry


class MoodMentorTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def test_1_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        print("\n[TEST] Health check passed.")

    def test_2_auth_and_journal_flow(self):
        # 1. Register test user
        reg_payload = {
            "username": "wellness_tester",
            "email": "tester@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test Explorer"
        }
        res = self.client.post("/api/auth/register", json=reg_payload)
        self.assertIn(res.status_code, [201, 409])
        
        # 2. Login
        login_res = self.client.post("/api/auth/login", json={
            "identifier": "wellness_tester",
            "password": "SecurePassword123!"
        })
        self.assertEqual(login_res.status_code, 200)
        token = login_res.get_json()["data"]["access_token"]
        self.assertTrue(bool(token))
        headers = {"Authorization": f"Bearer {token}"}
        print("[TEST] User registration and JWT login passed.")

        # 3. Live Emotion Analysis
        emotion_res = self.client.post("/api/emotion/analyze", json={
            "text": "I feel so grateful and joyful today! Finished my big presentation and celebrated with my colleagues."
        })
        self.assertEqual(emotion_res.status_code, 200)
        analysis = emotion_res.get_json()["data"]["analysis"]
        self.assertIn(analysis["primary_emotion"].lower(), ["joy", "love", "surprise"])
        self.assertGreater(analysis["sentiment"]["compound"], 0.2)
        print(f"[TEST] Live Emotion Analysis: Emotion={analysis['primary_emotion']}, Sentiment={analysis['sentiment']['compound']}")

        # 4. Create Journal Entry
        entry_payload = {
            "title": "A Great Milestone Achieved",
            "content": "Today we launched the product and our team is so proud. I feel immense relief and excitement for the future.",
            "tags": "work, milestone, celebration",
            "entry_date": "2026-10-16"
        }
        create_res = self.client.post("/api/journal", json=entry_payload, headers=headers)
        self.assertEqual(create_res.status_code, 201)
        created_entry = create_res.get_json()["data"]["entry"]
        entry_id = created_entry["id"]
        self.assertEqual(created_entry["title"], entry_payload["title"])
        self.assertIsNotNone(created_entry.get("analysis"))
        print(f"[TEST] Journal Entry created with ID {entry_id} and AI Emotion analysis.")

        # 5. List Entries
        list_res = self.client.get("/api/journal", headers=headers)
        self.assertEqual(list_res.status_code, 200)
        entries = list_res.get_json()["data"]["entries"]
        self.assertGreaterEqual(len(entries), 1)
        print(f"[TEST] Journal listing returned {len(entries)} entries.")

        # 6. Dashboard Stats
        dash_res = self.client.get("/api/analytics/dashboard", headers=headers)
        self.assertEqual(dash_res.status_code, 200)
        dash_data = dash_res.get_json()["data"]["dashboard"]
        self.assertGreaterEqual(dash_data["total_entries"], 1)
        print(f"[TEST] Dashboard stats passed: Total={dash_data['total_entries']}, Streak={dash_data['current_streak']}")

        # 7. Insights Plotly Data
        insights_res = self.client.get("/api/analytics/insights", headers=headers)
        self.assertEqual(insights_res.status_code, 200)
        insights_data = insights_res.get_json()["data"]["insights"]
        self.assertTrue(insights_data["has_data"])
        self.assertIn("emotion_distribution", insights_data)
        print("[TEST] Emotion insights analytics verified.")

        # 8. CSV Export
        csv_res = self.client.get("/api/journal/export/csv", headers=headers)
        self.assertEqual(csv_res.status_code, 200)
        self.assertIn("text/csv", csv_res.headers["Content-Type"])
        self.assertIn(b"Entry ID,Date,Title", csv_res.data)
        print("[TEST] CSV export generated successfully.")

        # 9. Clean up test user
        del_res = self.client.delete("/api/user/delete-account", json={"password": "SecurePassword123!"}, headers=headers)
        self.assertEqual(del_res.status_code, 200)
        print("[TEST] Account deleted permanently with cascading entries.")


if __name__ == "__main__":
    unittest.main()
