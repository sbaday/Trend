"""
Google Trends Collector
-----------------------
V2: Artık sadece niş odaklı değil, viral aramaları (RSS fallback ile) yakalıyoruz.
Ayrıca mevcut trendlerin radar/interest puanlarını güncelliyoruz.
"""

import os
import sys
import time
import random
import requests
import feedparser
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db.database import init_db, insert_signal, get_connection

load_dotenv()

PN = 'united_states'
GEO = 'US'
TIMEFRAME = "now 7-d"
HL = "en-US"

def build_client():
    return TrendReq(hl=HL, tz=360, timeout=(10, 25), retries=2, backoff_factor=0.5)

def validate_phrases(phrases: list[str], pytrends=None) -> dict[str, int]:
    if not phrases: return {}
    if pytrends is None: pytrends = build_client()
    
    results = {}
    for i in range(0, len(phrases), 5):
        batch = phrases[i:i+5]
        try:
            pytrends.build_payload(batch, timeframe=TIMEFRAME, geo=GEO)
            df = pytrends.interest_over_time()
            if df.empty:
                for p in batch: results[p] = 0
            else:
                for p in batch:
                    results[p] = int(df[p].mean()) if p in df.columns else 0
        except Exception as e:
            print(f"  pytrends validation hatası ({batch}): {e}")
            for p in batch: results[p] = 0
        time.sleep(random.uniform(1.5, 3.0))
    return results

def get_trending_rss(geo='US') -> list[str]:
    """
    RSS'den günün en çok arananlarını ve ilişkili haber başlıklarını çeker.
    Title tek başına (örn. 'penguin') yetersiz olduğu için alt haberleri de topluyoruz.
    """
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # feedparser kısıtlı kalabiliyor, BeautifulSoup ile XML'i derinlemesine kazıyoruz
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        results = []
        for item in items:
            main_title = item.find('title').text if item.find('title') else ""
            results.append(main_title)
            
            # Haber başlıklarını da ekleyelim (zengin bağlam için)
            news_items = item.find_all('ht:news_item')
            for ni in news_items[:2]: # Her trend için en iyi 2 haber başlığı yeterli
                news_title = ni.find('ht:news_item_title').text if ni.find('ht:news_item_title') else ""
                if news_title:
                    results.append(news_title)
                    
        return [r for r in results if r]
    except Exception as e:
        print(f"  RSS Fetch Hatası: {e}")
        return []

def discover_and_save(verbose: bool = True) -> int:
    init_db()
    pytrends = build_client()
    saved = 0
    
    if verbose:
        print(f"  → Google Trends ({PN}) viral aramalar çekiliyor...", end=" ", flush=True)

    # 1. Önce Pytrends dene
    trending = []
    try:
        df = pytrends.trending_searches(pn=PN)
        trending = df[0].tolist() if (df is not None and not df.empty) else []
    except:
        # 2. Hata verirse RSS Fallback
        trending = get_trending_rss(GEO)
    
    count = 0
    for phrase in trending:
        insert_signal(source="google_trends", subsource=f"trending_{GEO}", raw_title=phrase, engagement=100)
        count += 1
    
    if verbose:
        print(f"{count} viral sinyal kaydedildi.")
    return count

def update_google_interest(verbose: bool = True) -> int:
    init_db()
    conn = get_connection()
    # V2 column: normalized_phrase
    rows = conn.execute(
        "SELECT id, normalized_phrase FROM trends WHERE analyzed=0 LIMIT 30"
    ).fetchall()
    conn.close()

    if not rows: return 0
    
    phrases = [r[1] for r in rows]
    id_map = {r[1]: r[0] for r in rows}
    
    pytrends = build_client()
    scores = validate_phrases(phrases, pytrends)
    
    conn = get_connection()
    updated = 0
    for phrase, score in scores.items():
        if phrase in id_map:
            # V2: radar_score güncelleniyor
            conn.execute("UPDATE trends SET radar_score=? WHERE id=?", (float(score), id_map[phrase]))
            updated += 1
    conn.commit()
    conn.close()
    return updated

if __name__ == "__main__":
    print("Google Trends Engine V2 starting...")
    n1 = discover_and_save(verbose=True)
    n2 = update_google_interest(verbose=True)
    print(f"\nDone. {n1} new trending signals, {n2} interest scores updated.")
