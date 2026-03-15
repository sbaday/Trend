import sys
import os

# Ensure we can import from the project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extraction.phrase_extractor import extract_phrases_tfidf

def test_extraction():
    test_titles = [
        "I survived 2025 and all I got was this lousy t-shirt",
        "Vintage 1980 Limited Edition Birthday Gift for Men",
        "Cat Mom Life is the Best Life with my Fluffy Friends",
        "Crypto to the Moon 🚀 Bitcoin Bull Run 2024",
        "Just a girl who loves books and coffee",
        "Programming is my therapy, coding is my life"
    ]
    
    print("Testing TF-IDF Extraction (n-gram 1-3)...")
    results = extract_phrases_tfidf(test_titles)
    
    for title, phrase in results.items():
        print(f"\nRAW: {title}")
        print(f"EXTRACTED: {phrase}")

if __name__ == "__main__":
    test_extraction()
