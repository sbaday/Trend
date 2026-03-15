import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
    "about", "by", "from", "up", "down", "out", "of", "this", "that", "it", "is",
    "are", "was", "were", "be", "been", "I", "you", "he", "she", "we", "they",
    "whose", "how", "why", "where", "when", "can", "will", "would", "should", "could",
    # Custom POD noise filters
    "people", "thing", "things", "really", "today", "someone", "something", 
    "just", "like", "them", "then", "than", "there", "theyre", "weve", "im", "dont",
    "didnt", "doesnt", "wouldnt", "couldnt", "shouldnt", "wasnt", "werent", "aint"
}

def clean_text(text: str) -> str:
    """Temel metin temizliği yapar (noktalama, küçük harf, url silme)"""
    # URL'leri sil
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    # Rakamları ve gereksiz karakterleri sil
    text = re.sub(r'\[.*?\]|\(.*?\)|\<.*?\>', '', text)
    # Noktalama işaretlerini boşlukla değiştir (bazı dillerde kelimeyi böler, İngilizcede tire iş görebilir ama genel cleanup yapıyoruz)
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    text = text.translate(translator)
    # Küçük harf ve boşlukları temizle
    return " ".join(text.lower().split())

def extract_phrases_tfidf(texts: list[str]) -> dict[str, str]:
    """
    Basit TF-IDF yaklaşımı ile n-gram'lar çıkarır.
    Input: Orijinal raw title'lar listesi
    Output: {orijinal_title: normalized_phrase} sözlüğü
    """
    cleaned_texts = [clean_text(t) for t in texts]
    
    # 2-3 kelimelik phrase'leri arıyoruz (POD tişört tasarımları için en uygunu)
    vectorizer = TfidfVectorizer(
        stop_words=list(STOP_WORDS),
        ngram_range=(2, 4),
        max_features=1000
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
        feature_names = vectorizer.get_feature_names_out()
    except ValueError:
        # Metin kümesi TF-IDF için çok küçükse veya boşsa fallback
        return {texts[i]: cleaned_texts[i] for i in range(len(texts))}
        
    results = {}
    for i, _ in enumerate(texts):
        # Bu dokümandaki tf-idf skorlarını al
        doc_vector = tfidf_matrix.getrow(i).toarray()[0]
        # Max skora sahip n-gram'ı bul
        if doc_vector.max() > 0:
            best_phrase_idx = doc_vector.argmax()
            results[texts[i]] = feature_names[best_phrase_idx]
        else:
            results[texts[i]] = cleaned_texts[i][:50] # Bulamadıysa temiz halini koy
            
    return results

def fallback_extract(raw_title: str) -> str:
    """TF-IDF yetersiz kalırsa kullanılacak temizleyici."""
    return clean_text(raw_title)
