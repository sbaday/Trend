"""
Momentum Engine - Validation Module
-----------------------------------
Katman 1 (Internal): total_mentions >= threshold
Katman 2 (External): Google Trends validation via pytrends
"""

import time
import random
from pytrends.request import TrendReq

# Google Trends isteği için global instance
# hl='en-US' ve tz=360 (veya 0) genelde yeterlidir
pytrends = TrendReq(hl='en-US', tz=360)

def check_momentum_threshold(phrase: str, total_mentions: int, threshold: int = 20) -> bool:
    """
    Sistemin içindeki mention sayısına göre bir trendi 'Viral Adayı' olarak işaretler.
    """
    if total_mentions >= threshold:
        return True
    return False

def validate_with_google_trends(phrase: str, timeframe: str = 'now 7-d', geo: str = 'US') -> dict:
    """
    Bir phrase'in Google Trends üzerindeki son durumunu kontrol eder.
    Trend varsa True/Score döner.
    """
    try:
        # Rate limit yememek için kısa bir bekleme (jitter)
        time.sleep(random.uniform(1.0, 3.0))
        
        kw_list = [phrase]
        pytrends.build_payload(kw_list, cat=0, timeframe=timeframe, geo=geo, gprop='')
        
        interest_over_time_df = pytrends.interest_over_time()
        
        if interest_over_time_df.empty:
            return {"valid": False, "score": 0, "reason": "No data in timeframe"}
            
        # Son 3 periyottaki ortalama ilgi düzeyi
        recent_scores = interest_over_time_df[phrase].iloc[-3:]
        avg_score = recent_scores.mean()
        
        # Eğer ilgi 25'in üzerindeyse veya yükseliş varsa geçerli sayalım
        is_valid = avg_score > 25
        
        return {
            "valid": is_valid,
            "score": round(avg_score, 2),
            "recent_values": recent_scores.tolist()
        }
        
    except Exception as e:
        return {"valid": False, "score": 0, "error": str(e)}

def hybrid_validate(phrase: str, total_mentions: int, threshold: int = 20) -> dict:
    """
    Hem içsel hem dışsal doğrulamayı birleştirir.
    """
    internal_flag = check_momentum_threshold(phrase, total_mentions, threshold)
    
    result = {
        "phrase": phrase,
        "internal_viral": internal_flag,
        "external_validation": {"valid": False, "score": 0}
    }
    
    # Sadece belli bir eşiği geçenler için pahalı Google Trends sorgusu yapalım
    if internal_flag:
        external_res = validate_with_google_trends(phrase)
        result["external_validation"] = external_res
        
    return result
