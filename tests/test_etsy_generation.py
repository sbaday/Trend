import os
import sys
import json
from google import genai
from dotenv import load_dotenv

# Ensure we can import from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generator.generators import generate_etsy_listing
from models import EtsyListingOutput

load_dotenv()

def test_etsy_listing_generation():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found!")
        return

    client = genai.Client(api_key=api_key)
    
    phrase = "I survived 2025 and all I got was this lousy t-shirt"
    niche = "Funny"
    print(f"Testing Etsy Listing generation for: '{phrase}' in niche '{niche}'")
    
    try:
        listing = generate_etsy_listing(phrase, niche, client)
        
        print("\nGenerated Etsy Listing:")
        print(f"Title: {listing.title}")
        print(f"Description: {listing.description}")
        print(f"Tags: {', '.join(listing.tags)}")
        
        # Validation
        if len(listing.title) <= 140 and len(listing.tags) == 13:
            print("\n✅ Verification SUCCESS: Etsy listing meets constraints.")
        else:
            print(f"\n❌ Verification FAILED: Constraints violated.")
            if len(listing.title) > 140:
                print(f"   - Title is too long: {len(listing.title)} chars")
            if len(listing.tags) != 13:
                print(f"   - Incorrect tag count: {len(listing.tags)}")
                
    except Exception as e:
        print(f"\n❌ Error during listing generation: {e}")

if __name__ == "__main__":
    test_etsy_listing_generation()
