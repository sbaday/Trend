"""
Printify API Entegrasyonu
-------------------------
Trend analiz sonuçlarını Printify üzerinde taslak ürüne (draft) dönüştürür.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("PRINTIFY_API_TOKEN")
SHOP_ID = os.getenv("PRINTIFY_SHOP_ID")

BASE_URL = "https://api.printify.com/v1"

def create_product_draft(title: str, description: str, tags: list, blueprint_id=1, print_provider_id=1) -> dict:
    """
    Belirtilen blueprint_id (örnek: 1 = Unisex Heavy Cotton Tee - Gildan 5000)
    ve print_provider_id ayarlarına göre bir ürün draftı oluşturur.
    Gerçek görseller gelene kadar placeholder bir tasarım yapısı kullanılır.
    """
    if not API_TOKEN or not SHOP_ID:
        return None  # Token yoksa sessizce atla

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    url = f"{BASE_URL}/shops/{SHOP_ID}/products.json"
    
    payload = {
        "title": title[:255],
        "description": description,
        "blueprint_id": blueprint_id,
        "print_provider_id": print_provider_id,
        "variants": [
            {
                "id": 17355, # S (Gildan 5000 Siyah vs. olabilir, blueprint dependent)
                "price": 2000,
                "is_enabled": True
            },
            {
                "id": 17356, # M
                "price": 2000,
                "is_enabled": True
            }
        ],
        "print_areas": [
            {
                "variant_ids": [17355, 17356],
                "placeholders": [
                    {
                        "position": "front",
                        "images": [] # Henüz resim eklemiyoruz, sadece draft bilgilerini kaydediyoruz
                    }
                ]
            }
        ],
        "tags": tags[:13]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code in [200, 201]:
            data = response.json()
            return {"status": "success", "id": data.get("id"), "url": f"https://network.printify.com/products/{data.get('id')}"}
        else:
            return {"status": "error", "message": response.text}
    except Exception as e:
        return {"status": "exception", "message": str(e)}

if __name__ == "__main__":
    print("Test Printify Draft...")
    res = create_product_draft("Test T-Shirt", "A very cool t-shirt", ["test", "funny"])
    print(res)
