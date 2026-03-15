import sqlite3
import os
import sys

# Ensure we use the same path logic as database.py
os.chdir(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join("data", "trends_v2.db")

print(f"Checking DB at: {os.path.abspath(DB_PATH)}")

if not os.path.exists(DB_PATH):
    print("FATAL: Database file missing!")
    sys.exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Total records
cursor.execute("SELECT COUNT(*) FROM signals")
print(f"Total Signals: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM trends")
print(f"Total Trends: {cursor.fetchone()[0]}")

# 2. Analyzed records
cursor.execute("SELECT COUNT(*) FROM trends WHERE analyzed=1")
analyzed_count = cursor.fetchone()[0]
print(f"Analyzed Trends (analyzed=1): {analyzed_count}")

# 3. High score records
cursor.execute("SELECT COUNT(*) FROM trends WHERE analyzed=1 AND ai_score >= 5.0")
print(f"Trends with Score >= 5.0: {cursor.fetchone()[0]}")

# 4. Snippet of all analyzed trends
print("\n--- All Analyzed Trends ---")
cursor.execute("SELECT id, normalized_phrase, ai_score FROM trends WHERE analyzed=1 ORDER BY ai_score DESC")
for row in cursor.fetchall():
    print(row)

conn.close()
