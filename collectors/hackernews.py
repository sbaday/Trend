import requests
import requests
import sys
import os
import time
import random

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db.database import insert_signal

def collect(verbose: bool = True) -> int:
    """
    HackerNews topstories API'sini kullanarak en popüler başlıkları alır
    ve signals tablosuna kaydeder.
    """
    total_collected = 0
    
    # En iyi gönderi ID'lerini al
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    try:
        response = requests.get(url, timeout=10)
        story_ids = response.json()
    except Exception as e:
        if verbose:
            print(f"[HW] API hatası: {e}")
        return 0
        
    if verbose:
        print("[HackerNews] Top 50 hikaye alınıyor...")

    for story_id in story_ids[:50]:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        try:
            item_data = requests.get(item_url, timeout=5).json()
            if not item_data or item_data.get("type") != "story":
                continue
                
            title = item_data.get("title", "")
            link = item_data.get("url", f"https://news.ycombinator.com/item?id={story_id}")
            score = item_data.get("score", 0)
            comments = item_data.get("descendants", 0)
            
            # Engagement formülü: score + comments * 2
            engagement = score + (comments * 2)
            
            if title:
                insert_signal(source="hackernews", subsource="topstories", raw_title=title, url=link, engagement=engagement)
                total_collected += 1
                
            time.sleep(random.uniform(0.5, 1.5))
                
        except Exception as e:
            if verbose:
                print(f"  ID {story_id} çekilemedi: {e}")

    return total_collected

if __name__ == "__main__":
    print(f"Toplam Hackernews hikayesi sayısı: {collect()}")
