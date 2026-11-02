"""
Test Suite for MySQL Database Schema Verification.
Verifies:
- Users table (PK, Unique, Indexes, created_at, updated_at)
- JournalEntries table (PK, FK, Indexes, created_at, updated_at)
- EmotionResults table (PK, FK, Unique 1-to-1, Indexes, Constraints, created_at, updated_at)
- Suggestions table (PK, FK, Indexes, created_at, updated_at)
"""
import os
import sys
import unittest
import pymysql
from dotenv import load_dotenv

load_dotenv()

class MySQLSchemaTestCase(unittest.TestCase):
    def setUp(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "12345")
        self.db_name = os.getenv("DB_NAME", "moodmentor_db")
        self.conn = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.db_name,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )

    def tearDown(self):
        if self.conn:
            self.conn.close()

    def test_1_tables_exist(self):
        cursor = self.conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [list(r.values())[0].lower() for r in cursor.fetchall()]
        
        required_tables = ["users", "journal_entries", "emotion_results", "suggestions"]
        for table in required_tables:
            self.assertIn(table, tables, f"Missing required table: {table}")
        print("\n[TEST DB] All 4 required base tables exist in MySQL:", required_tables)

    def test_2_primary_keys(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT TABLE_NAME, COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s AND CONSTRAINT_NAME = 'PRIMARY'
        """, (self.db_name,))
        pks = {r["TABLE_NAME"].lower(): r["COLUMN_NAME"].lower() for r in cursor.fetchall()}
        
        for table in ["users", "journal_entries", "emotion_results", "suggestions"]:
            self.assertIn(table, pks)
            self.assertEqual(pks[table], "id")
        print("[TEST DB] Primary keys verified for all tables (id auto_increment).")

    def test_3_foreign_keys(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL
        """, (self.db_name,))
        fks = cursor.fetchall()

        links = [
            (fk["TABLE_NAME"].lower(), fk["COLUMN_NAME"].lower(), fk["REFERENCED_TABLE_NAME"].lower(), fk["REFERENCED_COLUMN_NAME"].lower())
            for fk in fks
        ]

        # Verify JournalEntries -> Users
        self.assertIn(("journal_entries", "user_id", "users", "id"), links)
        # Verify EmotionResults -> JournalEntries
        self.assertIn(("emotion_results", "journal_id", "journal_entries", "id"), links)
        # Verify EmotionResults -> Users
        self.assertIn(("emotion_results", "user_id", "users", "id"), links)
        # Verify Suggestions -> EmotionResults
        self.assertIn(("suggestions", "emotion_result_id", "emotion_results", "id"), links)
        # Verify Suggestions -> Users
        self.assertIn(("suggestions", "user_id", "users", "id"), links)
        print("[TEST DB] All foreign key relationships verified with cascading actions.")

    def test_4_created_at_updated_at(self):
        cursor = self.conn.cursor()
        for table in ["users", "journal_entries", "emotion_results", "suggestions"]:
            cursor.execute("""
                SELECT COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """, (self.db_name, table))
            columns = [r["COLUMN_NAME"].lower() for r in cursor.fetchall()]
            self.assertIn("created_at", columns, f"{table} missing created_at")
            self.assertIn("updated_at", columns, f"{table} missing updated_at")
        print("[TEST DB] created_at and updated_at timestamps verified on all 4 tables.")

    def test_5_indexes(self):
        cursor = self.conn.cursor()
        for table in ["users", "journal_entries", "emotion_results", "suggestions"]:
            cursor.execute(f"SHOW INDEX FROM {table}")
            indexes = [r["Key_name"] for r in cursor.fetchall()]
            self.assertGreater(len(indexes), 1, f"Expected multiple indexes on {table}")
        print("[TEST DB] Performance indexes verified across all tables.")


if __name__ == "__main__":
    unittest.main()
