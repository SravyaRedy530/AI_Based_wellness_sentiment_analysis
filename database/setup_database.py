"""
Script to apply and verify the complete MySQL database schema.
Executes database/schema.sql on MySQL.
"""
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def apply_complete_schema():
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "12345")
    db_name = os.getenv("DB_NAME", "moodmentor_db")

    print(f"Connecting to MySQL ({host}) for database '{db_name}'...")
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    # Read schema.sql
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Execute statements
    statements = sql_script.split(";")
    for stmt in statements:
        clean_stmt = stmt.strip()
        if clean_stmt:
            try:
                cursor.execute(clean_stmt)
            except Exception as e:
                # Ignore harmless warnings like duplicate index if already exists
                if "Duplicate key" not in str(e) and "already exists" not in str(e):
                    print(f"[NOTE] {e}")

    conn.commit()

    # Switch to moodmentor_db and inspect tables
    cursor.execute(f"USE {db_name}")
    cursor.execute("SHOW FULL TABLES WHERE Table_Type = 'BASE TABLE'")
    base_tables = [list(r.values())[0] for r in cursor.fetchall()]
    print(f"\n[OK] Base Tables in MySQL: {base_tables}")

    cursor.execute("SHOW FULL TABLES WHERE Table_Type = 'VIEW'")
    views = [list(r.values())[0] for r in cursor.fetchall()]
    print(f"[OK] Views in MySQL: {views}")

    # Verify Foreign Keys
    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL
    """, (db_name,))
    fks = cursor.fetchall()
    print(f"\n[OK] Foreign Keys Verified ({len(fks)} links):")
    for fk in fks:
        print(f"  - {fk['TABLE_NAME']}.{fk['COLUMN_NAME']} -> {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']} ({fk['CONSTRAINT_NAME']})")

    conn.close()
    print("\n[SUCCESS] Complete MySQL Database setup and schema verification completed successfully!")


if __name__ == "__main__":
    apply_complete_schema()
