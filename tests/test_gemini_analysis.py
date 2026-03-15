import os
import sys
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Ensure we can import from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer.gemini_scoring import compute_score
from models import ScoringOutput

load_dotenv()

def test_single_phrase_analysis():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found!")
        return

    client = genai.Client(api_key=api_key)
    
    phrase = "I survived 2025 and all I got was this lousy t-shirt"
    print(f"Testing Gemini analysis for: {phrase}")
    
    # Load prompts
    prompt_dir = "prompts"
    with open(os.path.join(prompt_dir, "scoring_system.md"), "r", encoding="utf-8") as f:
        system_prompt = f.read()
    with open(os.path.join(prompt_dir, "scoring_user.md"), "r", encoding="utf-8") as f:
        user_template = f.read()
        
    user_content = user_template.format(phrase=phrase, source="test", subreddit="N/A")
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=ScoringOutput,
            ),
        )
        
        data = json.loads(response.text)
        print("\nGemini Response:")
        print(json.dumps(data, indent=2))
        
        # Verify score calculation
        humor = data.get("humor", 0)
        identity = data.get("identity", 0)
        giftability = data.get("giftability", 0)
        design = data.get("design_simplicity", 0)
        
        score = compute_score(humor, identity, giftability, design)
        print(f"\nComputed AI Score: {score:.2f}")
        
        if score > 0:
            print("\n✅ Verification SUCCESS: Gemini analysis and scoring logic are working.")
        else:
            print("\n❌ Verification FAILED: Scoring logic returned 0.")
            
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")

if __name__ == "__main__":
    test_single_phrase_analysis()
