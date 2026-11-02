import requests
import streamlit as st
from typing import Dict, Any, Optional, Tuple
from frontend.config import API_BASE_URL


class APIClient:
    """HTTP Client communicating with Flask REST API using JWT Authentication."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def _get_headers(self) -> Dict[str, str]:
        """Constructs headers including JWT Bearer token if user is authenticated."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        token = st.session_state.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def register(self, fullname: str, email: str, password: str, username: str = "") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Registers a new user account."""
        url = f"{self.base_url}/auth/register"
        payload = {
            "fullname": fullname,
            "full_name": fullname,
            "email": email,
            "password": password,
            "username": username or email.split("@")[0]
        }
        try:
            res = requests.post(url, json=payload, timeout=10)
            data = res.json()
            if res.status_code == 201 and data.get("success"):
                return True, data.get("message", "Registered successfully"), data.get("data")
            return False, data.get("message", "Registration failed"), None
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: Make sure Flask backend is running on port 5000 ({str(e)})", None

    def login(self, identifier: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Authenticates user with username or email."""
        url = f"{self.base_url}/auth/login"
        payload = {"identifier": identifier, "password": password}
        try:
            res = requests.post(url, json=payload, timeout=10)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                return True, data.get("message", "Login successful"), data.get("data")
            return False, data.get("message", "Invalid credentials"), None
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: Make sure Flask backend is running on port 5000 ({str(e)})", None

    def get_me(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Retrieves currently logged in user info."""
        url = f"{self.base_url}/auth/me"
        try:
            res = requests.get(url, headers=self._get_headers(), timeout=5)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                return True, data.get("data", {}).get("user")
            return False, None
        except Exception:
            return False, None

    def logout(self) -> Tuple[bool, str]:
        """Revokes JWT token on server and cleans session."""
        url = f"{self.base_url}/auth/logout"
        try:
            res = requests.post(url, headers=self._get_headers(), timeout=5)
            data = res.json()
            return True, data.get("message", "Logged out successfully")
        except Exception as e:
            return False, str(e)

    def analyze_emotion(self, text: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Analyzes text emotion, sentiment, keywords, and coping suggestions."""
        url = f"{self.base_url}/emotion/analyze"
        payload = {"text": text}
        try:
            res = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                return True, data.get("message", "Analysis complete"), data.get("data")
            return False, data.get("message", "Analysis failed"), None
        except requests.exceptions.RequestException as e:
            return False, f"Server connection error: {str(e)}", None

    def get_personalized_suggestions(self, emotion: str) -> Tuple[bool, list, list]:
        """Fetches personalized suggestions as JSON for any predicted emotion."""
        url = f"{self.base_url}/emotion/suggestions"
        try:
            res = requests.get(url, params={"emotion": emotion}, headers=self._get_headers(), timeout=10)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                return True, data.get("suggestions", []), data.get("detailed_suggestions", [])
            return False, [], []
        except Exception:
            return False, [], []


    def get_entries(
        self,
        search: str = "",
        emotion: str = "",
        sentiment: str = "",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sort_by: str = "date_desc"
    ) -> Tuple[bool, list]:
        """Retrieves filtered journal entries."""
        url = f"{self.base_url}/journal"
        params = {
            "search": search,
            "emotion": emotion,
            "sentiment": sentiment,
            "sort_by": sort_by
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        try:
            res = requests.get(url, params=params, headers=self._get_headers(), timeout=10)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                return True, data.get("data", {}).get("entries", [])
            return False, []
        except Exception:
            return False, []

    def create_entry(self, title: str, content: str, tags: str = "", entry_date: Optional[str] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Creates a new journal entry with AI analysis."""
        url = f"{self.base_url}/journal"
        payload = {
            "title": title,
            "content": content,
            "tags": tags,
            "entry_date": entry_date
        }
        try:
            res = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            data = res.json()
            if res.status_code == 201 and data.get("success"):
                return True, data.get("message", "Entry saved"), data.get("data", {}).get("entry")
            return False, data.get("message", "Failed to save entry"), None
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}", None

    def update_entry(self, entry_id: int, title: str, content: str, tags: str = "", entry_date: Optional[str] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Updates an existing journal entry."""
        url = f"{self.base_url}/journal/{entry_id}"
        payload = {
            "title": title,
            "content": content,
            "tags": tags,
            "entry_date": entry_date,
            "reanalyze": True
        }
        try:
            res = requests.put(url, json=payload, headers=self._get_headers(), timeout=30)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                return True, data.get("message", "Entry updated"), data.get("data", {}).get("entry")
            return False, data.get("message", "Update failed"), None
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}", None

    def delete_entry(self, entry_id: int) -> Tuple[bool, str]:
        """Deletes a journal entry."""
        url = f"{self.base_url}/journal/{entry_id}"
        try:
            res = requests.delete(url, headers=self._get_headers(), timeout=10)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                return True, data.get("message", "Entry deleted")
            return False, data.get("message", "Delete failed")
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

    def get_dashboard_stats(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Fetches dashboard statistics and metrics."""
        url = f"{self.base_url}/analytics/dashboard"
        try:
            res = requests.get(url, headers=self._get_headers(), timeout=10)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                return True, data.get("data", {}).get("dashboard")
            return False, None
        except Exception:
            return False, None

    def get_emotion_insights(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Fetches emotion insights dataset for Plotly charts."""
        url = f"{self.base_url}/analytics/insights"
        try:
            res = requests.get(url, headers=self._get_headers(), timeout=10)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                return True, data.get("data", {}).get("insights")
            return False, None
        except Exception:
            return False, None

    def export_csv_data(self, format_type: str = "journal") -> Tuple[bool, Optional[str]]:
        """Downloads journal CSV data with columns: Date, Emotion, Sentiment, Journal, Confidence."""
        url = f"{self.base_url}/journal/export/csv"
        try:
            res = requests.get(url, params={"format": format_type}, headers=self._get_headers(), timeout=15)
            if res.status_code == 200:
                return True, res.text
            return False, None
        except Exception:
            return False, None

    def update_profile(
        self,
        full_name: str,
        email: Optional[str] = None,
        preferred_support_style: Optional[str] = None,
        theme: Optional[str] = None,
        bio: Optional[str] = None,
        wellness_goal: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Updates user profile information, email, preferred support style, and theme."""
        url = f"{self.base_url}/user/profile"
        payload = {
            "full_name": full_name,
            "email": email,
            "preferred_support_style": preferred_support_style,
            "theme": theme,
            "bio": bio,
            "wellness_goal": wellness_goal
        }
        try:
            res = requests.put(url, json=payload, headers=self._get_headers(), timeout=10)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                return True, data.get("message", "Profile updated"), data.get("data", {}).get("user")
            return False, data.get("message", "Profile update failed"), None
        except Exception as e:
            return False, f"Error: {str(e)}", None

    def change_password(self, current_password: str, new_password: str) -> Tuple[bool, str]:
        """Changes user account password."""
        url = f"{self.base_url}/user/password"
        payload = {"current_password": current_password, "new_password": new_password}
        try:
            res = requests.put(url, json=payload, headers=self._get_headers(), timeout=10)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                return True, data.get("message", "Password changed successfully")
            return False, data.get("message", "Password change failed")
        except Exception as e:
            return False, f"Error: {str(e)}"

    def delete_account(self, password: str) -> Tuple[bool, str]:
        """Permanently deletes user account."""
        url = f"{self.base_url}/user/delete-account"
        payload = {"password": password}
        try:
            res = requests.delete(url, json=payload, headers=self._get_headers(), timeout=10)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                return True, data.get("message", "Account deleted")
            return False, data.get("message", "Account deletion failed")
        except Exception as e:
            return False, f"Error: {str(e)}"


# Singleton instance
api_client = APIClient()
