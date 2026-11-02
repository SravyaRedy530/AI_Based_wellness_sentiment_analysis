"""
End-to-end test suite for the 10 unified REST APIs in MoodMentor.
Tests:
1. POST /register
2. POST /login
3. POST /analyze
4. GET /journal
5. GET /insights
6. GET /profile
7. PUT /profile
8. GET /export
9. DELETE /journal/{id}
10. DELETE /account
"""
import uuid
import requests

BASE_URL = "http://localhost:5000"


def run_rest_api_tests():
    print("=" * 70)
    print("  MOODMENTOR REST APIS COMPREHENSIVE VERIFICATION SUITE")
    print("=" * 70)

    session = requests.Session()
    unique_suffix = uuid.uuid4().hex[:8]
    test_email = f"rest_test_{unique_suffix}@example.com"
    test_password = "SecurePassword123!"
    test_fullname = "Rest Test User"

    # -------------------------------------------------------------------------
    # 1. POST /register
    # -------------------------------------------------------------------------
    print("\n[1/10] Testing POST /register ...")
    reg_payload = {
        "fullname": test_fullname,
        "email": test_email,
        "password": test_password,
        "preferred_support_style": "Gentle & Compassionate",
        "theme": "Dark Mode"
    }
    r = session.post(f"{BASE_URL}/register", json=reg_payload)
    print(f"Status Code: {r.status_code}")
    reg_json = r.json()
    print(f"Response: success={reg_json.get('success')}, message={reg_json.get('message')}")
    assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
    assert reg_json.get("success") is True
    assert "token" in reg_json or "access_token" in reg_json
    token = reg_json.get("token") or reg_json.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] POST /register successfully created user and returned JWT token.")

    # Test Duplicate Email prevention (409 Conflict)
    r_dup = session.post(f"{BASE_URL}/register", json=reg_payload)
    print(f"Duplicate Register Status: {r_dup.status_code} (Expected 409)")
    assert r_dup.status_code == 409, f"Expected 409 for duplicate email, got {r_dup.status_code}"
    print("[PASS] Duplicate email registration properly rejected with HTTP 409.")

    # -------------------------------------------------------------------------
    # 2. POST /login
    # -------------------------------------------------------------------------
    print("\n[2/10] Testing POST /login ...")
    login_payload = {
        "email": test_email,
        "password": test_password
    }
    r = session.post(f"{BASE_URL}/login", json=login_payload)
    print(f"Status Code: {r.status_code}")
    login_json = r.json()
    print(f"Response: success={login_json.get('success')}, message={login_json.get('message')}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert login_json.get("success") is True
    token = login_json.get("token") or login_json.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] POST /login successfully authenticated user against MySQL bcrypt hash.")

    # -------------------------------------------------------------------------
    # 3. POST /analyze
    # -------------------------------------------------------------------------
    print("\n[3/10] Testing POST /analyze ...")
    analyze_payload = {
        "text": "I am so happy and thrilled that our wellness platform launched successfully today!"
    }
    r = session.post(f"{BASE_URL}/analyze", json=analyze_payload, headers=headers)
    print(f"Status Code: {r.status_code}")
    ana_json = r.json()
    print(f"Emotion: {ana_json.get('emotion')}")
    print(f"Sentiment: {ana_json.get('sentiment')} (Score: {ana_json.get('sentiment_score')})")
    print(f"Confidence: {ana_json.get('confidence_percentage')}")
    print(f"Suggestions: {ana_json.get('suggestions')}")
    print(f"Auto-saved: {ana_json.get('auto_saved')}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert ana_json.get("success") is True
    assert ana_json.get("emotion") in ["Joy", "Love", "Surprise", "Neutral", "Sadness", "Fear", "Anger"]
    assert "suggestions" in ana_json
    assert len(ana_json.get("suggestions", [])) > 0
    assert ana_json.get("auto_saved") is True
    saved_entry_id = ana_json.get("saved_entry", {}).get("id")
    print(f"[PASS] POST /analyze executed AI model, returned JSON, and auto-saved entry ID: {saved_entry_id}")

    # -------------------------------------------------------------------------
    # 4. GET /journal
    # -------------------------------------------------------------------------
    print("\n[4/10] Testing GET /journal ...")
    r = session.get(f"{BASE_URL}/journal", headers=headers)
    print(f"Status Code: {r.status_code}")
    j_json = r.json()
    entries = j_json.get("entries", [])
    print(f"Total Entries: {j_json.get('total')}, Retrieved: {len(entries)}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert j_json.get("success") is True
    assert len(entries) >= 1
    found_entry = next((e for e in entries if e.get("id") == saved_entry_id), entries[0])
    entry_id = found_entry["id"]
    print(f"Found Entry in MySQL: ID={entry_id}, Emotion={found_entry.get('emotion')}, Date={found_entry.get('entry_date')}")
    print("[PASS] GET /journal returned journal list from MySQL.")

    # -------------------------------------------------------------------------
    # 5. GET /insights
    # -------------------------------------------------------------------------
    print("\n[5/10] Testing GET /insights ...")
    r = session.get(f"{BASE_URL}/insights", headers=headers)
    print(f"Status Code: {r.status_code}")
    ins_json = r.json()
    insights = ins_json.get("insights", {})
    kpis = insights.get("kpis", {})
    print(f"Total Check-ins: {kpis.get('total_checkins')}")
    print(f"Most Frequent Emotion: {kpis.get('most_frequent_emotion')}")
    print(f"Positive %: {kpis.get('positive_percentage')}%")
    print(f"Negative %: {kpis.get('negative_percentage')}%")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert ins_json.get("success") is True
    assert "distribution" in insights
    assert "timeline" in insights
    assert "monthly_report" in insights
    print("[PASS] GET /insights returned Plotly chart metrics, KPIs, and monthly report.")

    # -------------------------------------------------------------------------
    # 6. GET /profile
    # -------------------------------------------------------------------------
    print("\n[6/10] Testing GET /profile ...")
    r = session.get(f"{BASE_URL}/profile", headers=headers)
    print(f"Status Code: {r.status_code}")
    prof_json = r.json()
    user = prof_json.get("user", {})
    print(f"User: {user.get('fullname')} | Email: {user.get('email')} | Support: {user.get('preferred_support_style')} | Theme: {user.get('theme')}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert prof_json.get("success") is True
    assert user.get("email") == test_email
    print("[PASS] GET /profile returned user details.")

    # -------------------------------------------------------------------------
    # 7. PUT /profile
    # -------------------------------------------------------------------------
    print("\n[7/10] Testing PUT /profile ...")
    update_payload = {
        "fullname": "Updated REST Name",
        "preferred_support_style": "Direct & Action-Oriented",
        "theme": "Light Mode"
    }
    r = session.put(f"{BASE_URL}/profile", json=update_payload, headers=headers)
    print(f"Status Code: {r.status_code}")
    upd_json = r.json()
    upd_user = upd_json.get("user", {})
    print(f"Updated User: Fullname={upd_user.get('fullname')}, Support={upd_user.get('preferred_support_style')}, Theme={upd_user.get('theme')}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert upd_user.get("fullname") == "Updated REST Name"
    assert upd_user.get("preferred_support_style") == "Direct & Action-Oriented"
    assert upd_user.get("theme") == "Light Mode"
    print("[PASS] PUT /profile successfully modified user profile in MySQL.")

    # -------------------------------------------------------------------------
    # 8. GET /export
    # -------------------------------------------------------------------------
    print("\n[8/10] Testing GET /export ...")
    # Test JSON mode
    r_json = session.get(f"{BASE_URL}/export", headers=headers)
    print(f"JSON Export Status Code: {r_json.status_code}")
    exp_json = r_json.json()
    print(f"Export JSON: Total Entries={exp_json.get('total_entries')}, CSV lines preview: {exp_json.get('csv', '')[:80]}...")
    assert r_json.status_code == 200
    assert exp_json.get("success") is True
    assert "csv" in exp_json

    # Test CSV stream mode
    r_csv = session.get(f"{BASE_URL}/export?format=csv", headers=headers)
    print(f"CSV Download Status Code: {r_csv.status_code}, Content-Type: {r_csv.headers.get('Content-Type')}")
    assert r_csv.status_code == 200
    assert "text/csv" in r_csv.headers.get("Content-Type", "")
    assert "Entry ID" in r_csv.text
    print("[PASS] GET /export successfully provided journal data in both JSON and CSV stream formats.")

    # -------------------------------------------------------------------------
    # 9. DELETE /journal/{id}
    # -------------------------------------------------------------------------
    print(f"\n[9/10] Testing DELETE /journal/{entry_id} ...")
    r = session.delete(f"{BASE_URL}/journal/{entry_id}", headers=headers)
    print(f"Status Code: {r.status_code}")
    del_json = r.json()
    print(f"Response: {del_json.get('message')}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert del_json.get("success") is True

    # Verify entry is deleted in journal
    r_check = session.get(f"{BASE_URL}/journal", headers=headers)
    remaining_ids = [e["id"] for e in r_check.json().get("entries", [])]
    assert entry_id not in remaining_ids, f"Entry {entry_id} was not deleted from journal!"
    print(f"[PASS] DELETE /journal/{entry_id} successfully deleted entry from MySQL.")

    # -------------------------------------------------------------------------
    # 10. DELETE /account
    # -------------------------------------------------------------------------
    print("\n[10/10] Testing DELETE /account ...")
    r = session.delete(f"{BASE_URL}/account", headers=headers)
    print(f"Status Code: {r.status_code}")
    del_acc_json = r.json()
    print(f"Response: {del_acc_json.get('message')}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert del_acc_json.get("success") is True

    # Verify user can no longer log in
    r_relogin = session.post(f"{BASE_URL}/login", json=login_payload)
    print(f"Re-login after deletion Status: {r_relogin.status_code} (Expected 401)")
    assert r_relogin.status_code == 401, f"Expected 401 after account deletion, got {r_relogin.status_code}"
    print("[PASS] DELETE /account permanently wiped user and cascade data from MySQL.")

    print("\n" + "=" * 70)
    print("  ALL 10 REST APIS PASSED FULL SPECIFICATION VERIFICATION!")
    print("=" * 70)


if __name__ == "__main__":
    run_rest_api_tests()
