"""
Database migration script to add preferred_support_style and theme to the MySQL users table.
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_users_table():
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "12345")
    db_name = os.getenv("DB_NAME", "moodmentor_db")

    conn = pymysql.connect(host=host, user=user, password=password, database=db_name)
    cursor = conn.cursor()

    cursor.execute("SHOW COLUMNS FROM users LIKE 'preferred_support_style'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE users ADD COLUMN preferred_support_style VARCHAR(100) DEFAULT 'Gentle and Compassionate'")
        print("[OK] Added preferred_support_style to users table.")
    else:
        print("[OK] preferred_support_style column already exists.")

    cursor.execute("SHOW COLUMNS FROM users LIKE 'theme'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE users ADD COLUMN theme VARCHAR(50) DEFAULT 'Light Mode'")
        print("[OK] Added theme to users table.")
    else:
        print("[OK] theme column already exists.")

    conn.commit()
    conn.close()
    print("[MIGRATION COMPLETE] users table schema updated in MySQL.")

if __name__ == "__main__":
    migrate_users_table()
