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
            feed = feedparser.parse(url)
            
            if verbose:
                print(f"  [Reddit RSS] r/{sub}/{ep.split('/')[0]} taranıyor...")

            # Rising endpoint'leri daha az sonuç verebilir, normaldir
            for entry in feed.entries[:15]:
                title = entry.title
                link = entry.link
                
                # Sinyal kalitesini endpoint sırasına göre dummy olarak ağırlıklandıralım
                # (İleride comment veya upvote parse edilirse gerçek data konabilir)
                engagement = base_engagement 
                
                # Database zaten tüm sinyalleri farklı captured_at (veya uuid) ile
                # çoklu zaman serisi momentumu yaratacaktır.
                insert_signal(source="reddit_rss", subsource=f"r/{sub}", raw_title=title, url=link, engagement=engagement)
                total_collected += 1
            
            # API rate limit ve caching takılmamak için rastgele jitter
            time.sleep(random.uniform(1.5, 4.0))
            
    return total_collected

if __name__ == "__main__":
    print(f"Toplam alınan subreddit gönderisi: {collect()}")
