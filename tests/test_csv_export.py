"""
Test suite to verify that the journal CSV export generates the exact 5 columns:
- Date
- Emotion
- Sentiment
- Journal
- Confidence
"""
import csv
import io
import uuid
import requests

BASE_URL = "http://localhost:5000"


def test_journal_csv_columns():
    print("=" * 60)
    print("  VERIFYING JOURNAL CSV EXPORT (5 EXACT COLUMNS)")
    print("=" * 60)

    session = requests.Session()
    unique_suffix = uuid.uuid4().hex[:6]
    email = f"csvexport_{unique_suffix}@example.com"
    password = "TestPassword123!"

    # 1. Register user
    r_reg = session.post(f"{BASE_URL}/register", json={
        "fullname": "Export Tester",
        "email": email,
        "password": password
    })
    assert r_reg.status_code == 201, f"Register failed: {r_reg.text}"
    token = r_reg.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create sample reflection
    sample_text = "I am so happy and thrilled that our wellness project is launched today!"
    r_ana = session.post(f"{BASE_URL}/analyze", json={"text": sample_text}, headers=headers)
    assert r_ana.status_code == 200, f"Analysis failed: {r_ana.text}"

    # 3. Export CSV with format=journal
    r_exp = session.get(f"{BASE_URL}/api/journal/export/csv?format=journal", headers=headers)
    assert r_exp.status_code == 200, f"Export failed: {r_exp.text}"
    csv_text = r_exp.text

    print("\n--- Raw CSV Content ---")
    print(csv_text.strip())
    print("------------------------\n")

    # 4. Verify columns
    reader = csv.reader(io.StringIO(csv_text))
    header = next(reader)
    expected_header = ["Date", "Emotion", "Sentiment", "Journal", "Confidence"]

    print(f"Detected Headers: {header}")
    print(f"Expected Headers: {expected_header}")
    assert header == expected_header, f"Header mismatch! Expected {expected_header}, got {header}"

    # 5. Verify row content
    rows = list(reader)
    assert len(rows) >= 1, "Expected at least 1 row in CSV export"
    first_row = rows[0]
    print(f"\nRow 1: Date={first_row[0]}, Emotion={first_row[1]}, Sentiment={first_row[2]}, Journal={first_row[3][:35]}..., Confidence={first_row[4]}")
    assert first_row[0], "Date is missing"
    assert first_row[1] == "Joy", f"Expected Emotion 'Joy', got {first_row[1]}"
    assert first_row[2] == "Positive", f"Expected Sentiment 'Positive', got {first_row[2]}"
    assert sample_text in first_row[3], "Journal content is missing"
    assert "%" in first_row[4], "Confidence percentage is missing"

    print("\n[SUCCESS] Journal CSV export generates the exact 5 requested columns!")


if __name__ == "__main__":
    test_journal_csv_columns()
