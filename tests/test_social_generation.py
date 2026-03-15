import os
import sys
import json
from google import genai
from dotenv import load_dotenv

# Ensure we can import from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generator.generators import generate_social_content
from models import SocialContentOutput

load_dotenv()

def test_social_content_generation():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found!")
        return

    client = genai.Client(api_key=api_key)
    
    phrase = "I survived 2025 and all I got was this lousy t-shirt"
    niche = "Funny"
    print(f"Testing Social Content generation for: '{phrase}' in niche '{niche}'")
    
    try:
        social = generate_social_content(phrase, niche, client)
        
        print("\nGenerated Social Content:")
        print(f"TikTok Hook: {social.tiktok_hook}")
        print(f"Pinterest Title: {social.pinterest_title}")
        print(f"Instagram Caption: {social.instagram_caption}")
        
        # Validation
        if "#" in social.instagram_caption and len(social.tiktok_hook) > 5:
            print("\n✅ Verification SUCCESS: Social content contains hashtags and valid hooks.")
        else:
            print(f"\n❌ Verification FAILED: Constraints violated (likely missing hashtags).")
                
    except Exception as e:
        print(f"\n❌ Error during social content generation: {e}")

if __name__ == "__main__":
    test_social_content_generation()
