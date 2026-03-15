import requests
import feedparser
import sys
import os
import time
import random

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db.database import insert_signal

# Reddit'te print-on-demand trendleri çıkarılabilecek ana hedef kitle subredditleri
SUBREDDITS = [
    "funny", "memes", "gaming", "cats", "dogs", "programmerhumor",
    "aww", "fitness", "outdoors", "mommit", "daddit", "teachers",
    "etymology", "hiking", "introvert", "camping", "adhdmemes"
]

def collect(verbose: bool = True) -> int:
    """
    Belirli subredditlerin RRS feed'lerini okuyarak popüler gönderilerin 
    başlıklarını signals tablosuna kaydeder.
    """
    total_collected = 0
    endpoints = [
        ("rising/.rss", 150),       # En erken sinyal, novelty boost
        ("hot/.rss", 100),          # Mevcut gündem
        ("top/.rss?t=week", 50)     # Validasyon ve geçmiş onaylı trendler
    ]

    # Gerçek tarayıcı taklidi için genişletilmiş header seti
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    }

    for sub in SUBREDDITS:
        for ep, base_engagement in endpoints:
            url = f"https://www.reddit.com/r/{sub}/{ep}"
            
            try:
                # requests ile manuel çekiyoruz (feedparser bazen cloudflare'e takılıyor)
                response = requests.get(url, headers=headers, timeout=10)
                status = response.status_code
                
                if status == 200:
                    feed = feedparser.parse(response.text)
                    entries_count = len(feed.entries)
                else:
                    feed = None
                    entries_count = 0

                if verbose:
                    print(f"  [Reddit RSS] r/{sub}/{ep.split('/')[0]} -> Status: {status} | Bulunan: {entries_count}")

                if status == 403:
                    print(f"  ⚠️ [Reddit] 403 Forbidden! Railway IP adresi Reddit tarafından engellenmiş olabilir.")
                elif status == 429:
                    print(f"  ⚠️ [Reddit] 429 Rate Limit! Çok sık deniyoruz, bekleme süresini artırın.")
                
                if feed and entries_count > 0:
                    for entry in feed.entries[:15]:
                        title = entry.title
                        link = entry.link
                        engagement = base_engagement 
                        insert_signal(source="reddit_rss", subsource=f"r/{sub}", raw_title=title, url=link, engagement=engagement)
                        total_collected += 1
            except Exception as e:
                print(f"  ❌ [Reddit Error] {sub}: {str(e)}")

            # API rate limit ve caching takılmamak için rastgele jitter
            time.sleep(random.uniform(2.0, 5.0))
            
    return total_collected

if __name__ == "__main__":
    print(f"Toplam alınan subreddit gönderisi: {collect()}")
