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

    for sub in SUBREDDITS:
        for ep, base_engagement in endpoints:
            url = f"https://www.reddit.com/r/{sub}/{ep}"
            # User-Agent eklemek kritik, yoksa Reddit bot olarak görüp boş döner veya 403 verir
            # User-Agent eklemek kritik, yoksa Reddit bot olarak görüp boş döner veya 403 verir
            feed = feedparser.parse(url, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            status = getattr(feed, 'status', 'Unknown')
            entries_count = len(feed.entries)

            if verbose:
                print(f"  [Reddit RSS] r/{sub}/{ep.split('/')[0]} -> Status: {status} | Bulunan: {entries_count}")

            if status == 403:
                print(f"  ⚠️ [Reddit] 403 Forbidden! User-Agent engellenmiş olabilir.")
            elif status == 429:
                print(f"  ⚠️ [Reddit] 429 Rate Limit! Çok sık deniyoruz.")

            # Rising endpoint'leri daha az sonuç verebilir, normaldir
            for entry in feed.entries[:15]:
                title = entry.title
                link = entry.link
                
                # Sinyal kalitesini endpoint sırasına göre dummy olarak ağırlıklandıralım
                engagement = base_engagement 
                
                insert_signal(source="reddit_rss", subsource=f"r/{sub}", raw_title=title, url=link, engagement=engagement)
                total_collected += 1
            
            # API rate limit ve caching takılmamak için rastgele jitter
            time.sleep(random.uniform(1.5, 4.0))
            
    return total_collected

if __name__ == "__main__":
    print(f"Toplam alınan subreddit gönderisi: {collect()}")
