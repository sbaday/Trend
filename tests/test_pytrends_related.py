import sys
import os
import time
import random
from pytrends.request import TrendReq

# Mocking database calls
def mock_insert_signal(source, subsource, raw_title, url=None, engagement=0):
    print(f"[MOCK SAVE] {source} | {subsource} | {raw_title} | Engagement: {engagement}")

# Borrowing logic from collectors/google_trends.py
PN = 'united_states'
GEO = 'US'
TIMEFRAME = "now 7-d"
HL = "en-US"

def build_client():
    return TrendReq(hl=HL, tz=360, timeout=(10, 25), retries=2, backoff_factor=0.5)

def test_get_related_signals(pytrends=None):
    if pytrends is None: pytrends = build_client()
    seeds = ["t-shirt design", "gift ideas"] # Small set for testing
    
    print(f"Testing Related Queries discovery for: {seeds}")
    
    for kw in seeds:
        try:
            print(f"  → Checking {kw}...")
            pytrends.build_payload([kw], timeframe=TIMEFRAME, geo=GEO)
            related = pytrends.related_queries()
            
            if kw in related:
                # 1. Rising Queries
                rising = related[kw]['rising']
                if rising is not None and not rising.empty:
                    print(f"    - Found {len(rising)} Rising queries")
                    for query in rising['query'].tolist()[:3]: # Show top 3
                        mock_insert_signal("google_trends", "related_queries_rising", query, engagement=50)
                
                # 2. Top Queries
                top = related[kw]['top']
                if top is not None and not top.empty:
                    print(f"    - Found {len(top)} Top queries")
                    for query in top['query'].tolist()[:3]: # Show top 3
                        mock_insert_signal("google_trends", "related_queries_top", query, engagement=30)
            
            time.sleep(2) # Minimal jitter for test
        except Exception as e:
            print(f"    [!] Error for {kw}: {e}")

if __name__ == "__main__":
    test_get_related_signals()
