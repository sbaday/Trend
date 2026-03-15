"""
Etsy Search Scraper
-------------------
Belirtilen nişlerde Etsy arama sonuçlarındaki ürün başlıklarını kazıyarak
trend olabilecek cümleleri veya kelimeleri veritabanına kaydeder.

Kullanım:
    python etsy_scraper.py
"""

import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db.database import init_db, insert_trend

load_dotenv()

# Hedef arama terimleri (nişler)
NICHES = [
    "funny shirt",
    "cat shirt quotes",
    "dad joke shirt",
    "introvert shirt",
    "gym humor shirt",
    "sarcastic shirt"
]

def clean_title(title: str) -> str:
    """Başlığı temizle, fazla boşlukları sil."""
    # Genelde satıcılar " - " veya "," ile farklı kelimeleri ayırır
    title = re.sub(r"http\S+", "", title)
    title = re.sub(r"[^\x00-\x7F]+", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title

def extract_phrases(title: str) -> list:
    """Etsy başlıkları genelde 'Keyword 1, Keyword 2 - Keyword 3' şeklinde olur. 
    Bunları parçalayıp daha anlamlı phrase'ler çıkar."""
    separators = r'[,|\-|\/]+'
    parts = re.split(separators, title)
    phrases = []
    for p in parts:
        pt = p.strip()
        if 10 <= len(pt) <= 120:
            phrases.append(pt)
    return phrases

def collect(verbose: bool = True) -> int:
    init_db()
    saved = 0
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    }

    session = requests.Session()
    session.headers.update(headers)

    for niche in NICHES:
        if verbose:
            print(f"  → Etsy'de aranıyor: {niche}...", end=" ", flush=True)
            
        try:
            url = f"https://www.etsy.com/search?q={niche.replace(' ', '+')}"
            response = session.get(url, timeout=15)
            
            if response.status_code != 200:
                if verbose:
                    print(f"HATA: HTTP {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            # Etsy ürün kartı başlık class'ları genelde "v2-listing-card__title" vb. oluyor.
            # Alternatif olarak tüm h3 etiketlerine bakıyoruz (ürün isimleri genelde h3 içindedir).
            titles = soup.find_all('h3')
            
            count = 0
            for t in titles:
                raw_text = t.get_text()
                # Çok kısa h3'ler kategori ismi olabilir
                if len(raw_text.strip()) < 10:
                    continue
                    
                title_text = clean_title(raw_text)
                phrases = extract_phrases(title_text)
                
                for phrase in phrases:
                    # Kaydet
                    insert_trend(
                        phrase=phrase,
                        source="etsy",
                        subreddit=None,
                        etsy_interest=1
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
    print("Etsy Collector başlıyor...\n")
    n = collect(verbose=True)
    print(f"\nToplam {n} trend phrase kaydedildi.")
