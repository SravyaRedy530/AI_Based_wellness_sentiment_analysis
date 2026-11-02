"""
Test Suite for AI Emotion Analyzer Endpoint (/api/emotion/analyze).
Verifies:
- Joy: Celebrate achievements, Share appreciation, Take photos
- Fear: Breathing exercise, Grounding, Positive affirmations, Mindfulness
- Sadness: Music, Walk, Friend, Journaling
- Exact JSON structure returned
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import create_app


class PersonalizedSuggestionsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_1_joy_suggestions(self):
        """Tests that Joy returns Celebrate achievements, Share appreciation, Take photos."""
        res = self.client.post("/api/emotion/analyze", json={
            "text": "I am so happy and overjoyed with our team milestone today! Everything was wonderful."
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]

        self.assertEqual(data["emotion"], "Joy")
        suggestions = data.get("suggestions", [])
        self.assertIn("Celebrate achievements", suggestions)
        self.assertIn("Share appreciation", suggestions)
        self.assertIn("Take photos", suggestions)
        print(f"[TEST JOY] Passed. Suggestions: {suggestions}")

    def test_2_fear_suggestions(self):
        """Tests that Fear returns Breathing exercise, Grounding, Positive affirmations, Mindfulness."""
        res = self.client.post("/api/emotion/analyze", json={
            "text": "I am terrified and anxious about what might happen next. I feel nervous and scared."
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]

        self.assertEqual(data["emotion"], "Fear")
        suggestions = data.get("suggestions", [])
        self.assertIn("Breathing exercise", suggestions)
        self.assertIn("Grounding", suggestions)
        self.assertIn("Positive affirmations", suggestions)
        self.assertIn("Mindfulness", suggestions)
        print(f"[TEST FEAR] Passed. Suggestions: {suggestions}")

    def test_3_sadness_suggestions(self):
        """Tests that Sadness returns Music, Walk, Friend, Journaling."""
        res = self.client.post("/api/emotion/analyze", json={
            "text": "I feel so lonely, heartbroken, and completely down. I am in tears and depressed."
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]

        self.assertEqual(data["emotion"], "Sadness")
        suggestions = data.get("suggestions", [])
        self.assertIn("Music", suggestions)
        self.assertIn("Walk", suggestions)
        self.assertIn("Friend", suggestions)
        self.assertIn("Journaling", suggestions)
        print(f"[TEST SADNESS] Passed. Suggestions: {suggestions}")

    def test_4_json_schema(self):
        """Verifies full JSON response schema."""
        res = self.client.post("/api/emotion/analyze", json={"text": "A nice sunny afternoon in the park."})
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(body["success"])
        self.assertIn("data", body)
        data = body["data"]
        for key in ["emotion", "sentiment", "sentiment_score", "confidence", "suggestions", "personalized_suggestions"]:
            self.assertIn(key, data, f"Missing key in JSON response: {key}")
        print("[TEST JSON SCHEMA] Passed. All required fields are present in response JSON.")


if __name__ == "__main__":
    unittest.main()
