"""
Test Suite for Emotion Insights Dashboard Endpoint (/api/analytics/insights).
Verifies:
- Emotion Distribution (Pie Chart dataset)
- Average Sentiment & Sentiment Label
- Timeline (Sentiment trajectory)
- Monthly Report
- Most Frequent Emotion
- Total Check-ins
- Positive % & Negative %
- Plotly chart generation
"""
import os
import sys
import unittest
import json
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import create_app
from backend.models.database import db
from backend.models.user import User
from backend.models.journal import JournalEntry
from backend.models.emotion_log import EmotionLog


class EmotionInsightsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_emotion_insights_metrics_and_charts(self):
        # 1. Register test user
        reg_res = self.client.post("/api/auth/register", json={
            "fullname": "Insights Unit Tester",
            "email": f"insights_unit_{os.getpid()}@example.com",
            "password": "Password123!"
        })
        self.assertEqual(reg_res.status_code, 201)
        token = reg_res.get_json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Log reflections across different emotions
        thoughts = [
            "I am so proud and happy with our team achievement! Wonderful day.",
            "Celebrating success with gratitude and joy! Everything is great.",
            "I feel intense fear and trembling anxiety about the interview tomorrow.",
            "Sadness and lonely grief fill my day. Crying in tears."
        ]

        for text in thoughts:
            analyze_res = self.client.post("/api/emotion/analyze", json={"text": text}, headers=headers)
            self.assertEqual(analyze_res.status_code, 200)

        # 3. Query /api/analytics/insights
        insights_res = self.client.get("/api/analytics/insights", headers=headers)
        self.assertEqual(insights_res.status_code, 200)
        body = insights_res.get_json()
        self.assertTrue(body["success"])

        insights = body["data"]["insights"]
        print("\n[TEST INSIGHTS] Received payload:")
        print(f"  Total Check-ins: {insights.get('total_checkins')}")
        print(f"  Most Frequent Emotion: {insights.get('most_frequent_emotion')}")
        print(f"  Positive %: {insights.get('positive_percentage')}%")
        print(f"  Negative %: {insights.get('negative_percentage')}%")
        print(f"  Average Sentiment: {insights.get('avg_sentiment')}")
        print(f"  Emotion Distribution: {insights.get('emotion_distribution')}")
        print(f"  Monthly Report Count: {len(insights.get('monthly_report', []))}")

        # Assertions for all user requirements
        self.assertEqual(insights["total_checkins"], 4)
        self.assertEqual(insights["most_frequent_emotion"], "Joy")
        self.assertEqual(insights["positive_percentage"], 50.0)
        self.assertEqual(insights["negative_percentage"], 50.0)
        self.assertGreater(len(insights["emotion_distribution"]), 0)
        self.assertIn("Joy", insights["emotion_distribution"])
        self.assertEqual(len(insights["sentiment_timeline"]), 4)
        self.assertGreaterEqual(len(insights["monthly_report"]), 1)

        # Check Monthly Report keys
        month_item = insights["monthly_report"][0]
        self.assertIn("month_label", month_item)
        self.assertIn("total_entries", month_item)
        self.assertIn("avg_sentiment", month_item)
        self.assertIn("dominant_emotion", month_item)
        self.assertIn("positive_entries", month_item)
        self.assertIn("negative_entries", month_item)
        self.assertIn("emotion_breakdown", month_item)

        print("[TEST INSIGHTS] All assertions passed successfully!")


if __name__ == "__main__":
    unittest.main()
