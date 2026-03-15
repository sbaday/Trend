import os
import sys
from google import genai
from dotenv import load_dotenv

# Ensure we can import from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generator.generators import generate_design_prompt

load_dotenv()

def test_design_prompt_generation():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found!")
        return

    client = genai.Client(api_key=api_key)
    
    phrase = "I survived 2025 and all I got was this lousy t-shirt"
    niche = "Funny"
    print(f"Testing Design Prompt generation for: '{phrase}' in niche '{niche}'")
    
    try:
        prompt = generate_design_prompt(phrase, niche, client)
        
        print("\nGenerated Design Prompt:")
        print(prompt)
        
        # Validation
        check_keywords = ["Midjourney", "Kittl", "vector", "white background", "isolated"]
        found = [kw for kw in check_keywords if kw.lower() in prompt.lower()]
        
        print(f"\nKeywords found: {', '.join(found)}")
        
        if len(prompt) > 20: # Basic length check
            print("\n✅ Verification SUCCESS: Design prompt generated successfully.")
        else:
            print(f"\n❌ Verification FAILED: Prompt too short.")
                
    except Exception as e:
        print(f"\n❌ Error during design prompt generation: {e}")

if __name__ == "__main__":
    test_design_prompt_generation()
