
import os
import sys
from datetime import datetime
import time

# Ensure project root is in path
sys.path.append(os.getcwd())

from db.database import get_connection
from analyzer.sentiment import score_sentiment

def backfill_metrics():
    conn = get_connection()
    cur = conn.cursor()
    
    print("Backfilling longevity_days and sentiment_score (RETRY MODE)...")
    
    # 1. Update longevity_days for all trends (fast SQL update)
    try:
        cur.execute("""
            UPDATE trends 
            SET longevity_days = ABS(EXTRACT(DAY FROM (last_seen - first_seen)))
            WHERE last_seen IS NOT NULL AND first_seen IS NOT NULL;
        """)
        conn.commit()
        print(f"Updated longevity for {cur.rowcount} trends.")
    except Exception as e:
        conn.rollback()
        print(f"Longevity update error: {e}")
    
    # 2. Update sentiment_score for remaining trends
    cur.execute("SELECT id, normalized_phrase FROM trends WHERE (sentiment_score IS NULL OR sentiment_score = 0.0)")
    trends = cur.fetchall()
    print(f"Calculating sentiment for {len(trends)} remaining trends...")
    
    count = 0
    errors = 0
    for tid, phrase in trends:
        try:
            score = score_sentiment(phrase)
            cur.execute("UPDATE trends SET sentiment_score = %s WHERE id = %s", (score, tid))
            count += 1
            if count % 50 == 0:
                print(f"  Processed {count}/{len(trends)}...")
                conn.commit()
        except Exception as e:
            conn.rollback()
            errors += 1
            print(f"  Error on ID {tid}: {e}")
            time.sleep(1) # Wait a bit on lock
            
    conn.commit()
    cur.close()
    conn.close()
    print(f"Successfully backfilled {count} trends. Errors: {errors}")

if __name__ == "__main__":
    backfill_metrics()
