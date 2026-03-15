"""
Gemini Trend Analyzer
---------------------
DB'deki ham trendleri Gemini (google-genai) ile puanlar.

Ağırlıklı skor:
  final = humor*0.35 + identity*0.25 + giftability*0.25 + design*0.15

Threshold: 7.0+ → output pipeline'a gönderilir.

Kullanım:
    python gemini_scoring.py
"""

import os
import sys
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db.database import init_db, get_unanalyzed, update_scores
from models import ScoringOutput
from validation.momentum import hybrid_validate

load_dotenv()

SCORE_THRESHOLD = 7.0
MODEL = "gemini-flash-latest"

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")
with open(os.path.join(PROMPTS_DIR, "scoring_system.md"), "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

with open(os.path.join(PROMPTS_DIR, "scoring_user.md"), "r", encoding="utf-8") as f:
    USER_TEMPLATE = f.read()

def compute_score(humor: float, identity: float, giftability: float, design: float) -> float:
    return round(humor * 0.35 + identity * 0.25 + giftability * 0.25 + design * 0.15, 2)


def analyze_batch(verbose: bool = True, min_mentions: int = 3) -> int:
    """
    DB'deki analiz edilmemiş trendleri Gemini ile puanla.
    min_mentions: Gemini'ye gönderilmek için geçilmesi gereken minimum tekrar sayısı.
    Döndürür: analiz edilen kayıt sayısı
    """
    init_db()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    rows = get_unanalyzed(limit=30, min_mentions=min_mentions)
    if not rows:
        if verbose:
            print(f"  Analiz edilecek trend yok (min_mentions={min_mentions}).")
        return 0

    analyzed = 0
    for trend_id, phrase, source, subreddit, total_mentions in rows:
        if verbose:
            print(f"  → [{trend_id}] '{phrase[:50]}...' (Mentions: {total_mentions})", end=" ", flush=True)

        try:
            # Sadece mention sayısını loglayalım
            prompt = USER_TEMPLATE.format(
                phrase=phrase,
                source=source,
                subreddit=subreddit or "N/A"
            )
            
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=ScoringOutput,
                ),
            )
            
            raw = response.text
            # It's guaranteed to be JSON matching the schema if it succeeds
            data = json.loads(raw)

            humor       = float(data.get("humor", 5))
            identity    = float(data.get("identity", 5))
            giftability = float(data.get("giftability", 5))
            design      = float(data.get("design_simplicity", 5))
            niche       = data.get("niche", "general")
            score       = compute_score(humor, identity, giftability, design)

            update_scores(trend_id, humor, identity, giftability, design, score, niche)
            analyzed += 1

            if verbose:
                flag = "🔥" if score >= SCORE_THRESHOLD else "  "
                print(f"{flag} skor={score:.2f} niş={niche}")

            # API rate limit — küçük bekleme
            time.sleep(0.3)

        except Exception as e:
            if verbose:
                print(f"HATA: {e}")

    return analyzed


if __name__ == "__main__":
    print("Gemini Trend Analyzer başlıyor...\n")
    n = analyze_batch(verbose=True)
    print(f"\nToplam {n} trend analiz edildi.")
    print(f"Threshold {SCORE_THRESHOLD}+ olanlar output pipeline'a hazır.")
