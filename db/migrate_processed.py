import os
import sys
from dotenv import load_dotenv

# Path adjust
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import get_connection

def migrate():
    print("🚀 Starting migration: Adding 'processed' column to 'signals' table...")
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Add column if not exists
        cur.execute("""
            ALTER TABLE signals 
            ADD COLUMN IF NOT EXISTS processed BOOLEAN DEFAULT FALSE;
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Migration SUCCESS: 'processed' column added (or already exists).")
    except Exception as e:
        print(f"❌ Migration FAILED: {e}")

if __name__ == "__main__":
    load_dotenv()
    migrate()
