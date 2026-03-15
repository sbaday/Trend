"""
Output Generators
-----------------
Yüksek skorlu trendler için üç çıktı üretir:
  1. design_prompt   — Midjourney / Kittl için görsel prompt
  2. etsy_listing    — Başlık + açıklama + 13 tag
  3. social_content  — TikTok + Pinterest + Instagram

Kullanım:
    python generators.py
"""

import os
import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from models import EtsyListingOutput, SocialContentOutput
from db.database import init_db, insert_output, get_top_trends, get_outputs_for_trend
try:
    from generator.printify_api import create_product_draft
except ImportError:
    # Fallback to local import if run as standalone inside generator directory
    from printify_api import create_product_draft

load_dotenv()

MODEL = "gemini-2.5-flash"
SCORE_THRESHOLD = 7.0


PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")

with open(os.path.join(PROMPTS_DIR, "design_system.md"), "r", encoding="utf-8") as f:
    DESIGN_PROMPT_SYSTEM = f.read()
with open(os.path.join(PROMPTS_DIR, "design_user.md"), "r", encoding="utf-8") as f:
    DESIGN_USER_TEMPLATE = f.read()

with open(os.path.join(PROMPTS_DIR, "listing_system.md"), "r", encoding="utf-8") as f:
    LISTING_SYSTEM = f.read()
with open(os.path.join(PROMPTS_DIR, "listing_user.md"), "r", encoding="utf-8") as f:
    LISTING_USER_TEMPLATE = f.read()

with open(os.path.join(PROMPTS_DIR, "social_system.md"), "r", encoding="utf-8") as f:
    SOCIAL_SYSTEM = f.read()
with open(os.path.join(PROMPTS_DIR, "social_user.md"), "r", encoding="utf-8") as f:
    SOCIAL_USER_TEMPLATE = f.read()


def generate_design_prompt(phrase: str, niche: str, client: genai.Client) -> str:
    prompt = DESIGN_USER_TEMPLATE.format(phrase=phrase, niche=niche)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=DESIGN_PROMPT_SYSTEM)
    )
    return response.text.strip()


def generate_etsy_listing(phrase: str, niche: str, client: genai.Client) -> EtsyListingOutput:
    prompt = LISTING_USER_TEMPLATE.format(phrase=phrase, niche=niche)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=LISTING_SYSTEM,
            response_mime_type="application/json",
            response_schema=EtsyListingOutput
        )
    )
    import json
    data = json.loads(response.text)
    return EtsyListingOutput(**data)


def generate_social_content(phrase: str, niche: str, client: genai.Client) -> SocialContentOutput:
    prompt = SOCIAL_USER_TEMPLATE.format(phrase=phrase, niche=niche)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SOCIAL_SYSTEM,
            response_mime_type="application/json",
            response_schema=SocialContentOutput
        )
    )
    import json
    data = json.loads(response.text)
    return SocialContentOutput(**data)


def run_output_pipeline(verbose: bool = True) -> int:
    """
    Skor >= threshold olan ve henüz çıktısı üretilmemiş trendleri işle.
    Döndürür: işlenen trend sayısı
    """
    init_db()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    trends = get_top_trends(limit=50, min_score=SCORE_THRESHOLD)
    processed = 0

    for row in trends:
        trend_id, phrase, source, subreddit, score, niche = row[:6]

        # Zaten çıktısı var mı?
        existing = get_outputs_for_trend(trend_id)
        if existing:
            continue

        if verbose:
            print(f"\n  🎨 [{trend_id}] '{phrase}' (skor={score:.2f}, niş={niche})")

        try:
            # 1. Tasarım promptu
            dp = generate_design_prompt(phrase, niche, client)
            insert_output(trend_id, "design_prompt", dp)
            if verbose:
                print(f"     ✓ Design prompt üretildi")

            # 2. Etsy listing
            listing = generate_etsy_listing(phrase, niche, client)
            import json
            insert_output(trend_id, "etsy_listing", json.dumps(listing.model_dump(), ensure_ascii=False))
            if verbose:
                print(f"     ✓ Etsy listing üretildi")
                
            # 2.5. Printify Draft
            try:
                draft_res = create_product_draft(
                    title=listing.title,
                    description=listing.description,
                    tags=listing.tags
                )
                if draft_res and draft_res.get("status") == "success":
                    insert_output(trend_id, "printify_draft", json.dumps(draft_res, ensure_ascii=False))
                    if verbose:
                        print(f"     ✓ Printify Draft oluşturuldu")
                elif draft_res and verbose:
                    print(f"     ✗ Printify Warning: {draft_res.get('message')}")
            except Exception as pe:
                if verbose:
                    print(f"     ✗ Printify HATA: {pe}")

            # 3. Sosyal içerik
            social = generate_social_content(phrase, niche, client)
            insert_output(trend_id, "social_content", json.dumps(social.model_dump(), ensure_ascii=False))
            if verbose:
                print(f"     ✓ Sosyal içerik üretildi")

            processed += 1

        except Exception as e:
            if verbose:
                print(f"     ✗ HATA: {e}")

    return processed


if __name__ == "__main__":
    print("Output Generator başlıyor...\n")
    n = run_output_pipeline(verbose=True)
    print(f"\nToplam {n} trend için içerik üretildi.")
