"""
Pinterest Collector
-------------------
Pinterest arama sonuçlarındaki gönderilerin açıklama ve başlıklarından
trend olabilecek cümleleri bulup veritabanına kaydeder.

Kullanım:
    python pinterest_collector.py
"""

import os
import re
import sys
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db.database import init_db, insert_signal

load_dotenv()

NICHES = [
    "funny shirt sayings",
    "sarcastic quotes tshirts",
    "gym humor shirts",
    "mom life quotes funny"
]

def clean_title(title: str) -> str:
    title = re.sub(r"http\S+", "", title)
    title = re.sub(r"[^\x00-\x7F]+", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title

def is_useful_phrase(title: str) -> bool:
    if len(title) < 10 or len(title) > 120:
        return False
    # Filtreler (ÖRN: "Buy now", "Link in bio" gibi spamları eleyebiliriz)
    lower = title.lower()
    junk = ["buy now", "link in bio", "click here", "sale", "% off", "my shop"]
    if any(j in lower for j in junk):
        return False
    return True

def collect(verbose: bool = True) -> int:
    init_db()
    saved = 0
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    session = requests.Session()
    session.headers.update(headers)

    for niche in NICHES:
        if verbose:
            print(f"  → Pinterest'te aranıyor: {niche}...", end=" ", flush=True)
            
        try:
            # Pinterest araması
            query = requests.utils.quote(niche)
            url = f"https://www.pinterest.com/search/pins/?q={query}"
            
            response = session.get(url, timeout=15)
            if response.status_code != 200:
                if verbose:
                    print(f"HATA: HTTP {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Pinterest SSR (Server Side Rendering) sayfası içinde genellikle resim alt metinleri 
            # veya initial data objesi (json) bulunur. Basic bir yöntem olarak sayfa içindeki
            # resimlerin alt(description) attribute'larını alıyoruz.
            
            phrases = set()
            images = soup.find_all('img')
            
            for img in images:
                alt = img.get('alt', '')
                if alt:
                    clean = clean_title(alt)
                    if is_useful_phrase(clean):
                        phrases.add(clean)
            
            count = 0
            # Sınırlandırmak iyi olabilir, her niche için max 30-40 sonuç
            for phrase in list(phrases)[:40]:
                insert_signal(
                    source="pinterest",
                    raw_title=phrase,
                    engagement=1
                )
                count += 1
                
            saved += count
            if verbose:
                print(f"{count} phrase kaydedildi")
                
        except Exception as e:
            if verbose:
                print(f"HATA: {e}")
                
    return saved


if __name__ == "__main__":
    print("Pinterest Collector başlıyor...\n")
    n = collect(verbose=True)
    print(f"\nToplam {n} trend phrase kaydedildi.")
