import json
import re
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "lt-LT,lt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.barbora.lt/",
    "Origin": "https://www.barbora.lt"
}

def parse_volume(title):
    multi_match = re.search(r'(\d+)\s*x\s*([\d\.,]+)\s*l', title, re.IGNORECASE)
    if multi_match:
        count = int(multi_match.group(1))
        vol = float(multi_match.group(2).replace(',', '.'))
        return round(count * vol, 2)
    
    single_match = re.search(r'([\d\.,]+)\s*l', title, re.IGNORECASE)
    if single_match:
        return float(single_match.group(1).replace(',', '.'))
    
    return 1.0

def detect_type(title):
    text = title.lower()
    if 'skard' in text or 'can' in text:
        return 'can'
    if 'stikl' in text or 'glass' in text:
        return 'glass'
    return 'bottle'

def scrape_barbora():
    deals = []
    url = "https://barbora.lt/api/eshop/v1/search?q=coca-cola"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            return deals
        
        data = res.json()
        products = data.get('products', [])
        
        for item in products:
            title = item.get('title', '')
            if 'coca-cola' not in title.lower():
                continue

            price = float(item.get('price', 0))
            strike_price = item.get('strike_through_price')
            old_price_val = float(strike_price) if strike_price else None
            
            discount = 0
            if old_price_val and old_price_val > price:
                discount = int(round(((old_price_val - price) / old_price_val) * 100))

            vol_liters = parse_volume(title)

            deals.append({
                "store": "Maxima",
                "title": title,
                "volume": f"{vol_liters} l",
                "volumeLiters": vol_liters,
                "price": price,
                "oldPrice": old_price_val,
                "discount": discount,
                "type": detect_type(title),
                "validUntil": "Barbora"
            })
    except Exception as e:
        print(f"Barbora klaida: {e}")
    return deals

def scrape_rimi():
    deals = []
    url = "https://www.rimi.lt/e-parduotuve/api/v1/products?query=coca-cola&lang=lt"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            return deals

        data = res.json()
        products = data.get('results', [])
        
        for item in products:
            title = item.get('name', '')
            if 'coca-cola' not in title.lower():
                continue

            price = float(item.get('price', 0))
            old_price = item.get('oldPrice')
            old_price_val = float(old_price) if old_price else None
            
            discount = 0
            if old_price_val and old_price_val > price:
                discount = int(round(((old_price_val - price) / old_price_val) * 100))

            vol_liters = parse_volume(title)

            deals.append({
                "store": "Rimi",
                "title": title,
                "volume": f"{vol_liters} l",
                "volumeLiters": vol_liters,
                "price": price,
                "oldPrice": old_price_val,
                "discount": discount,
                "type": detect_type(title),
                "validUntil": "Rimi"
            })
    except Exception as e:
        print(f"Rimi klaida: {e}")
    return deals

def main():
    all_deals = []
    
    all_deals.extend(scrape_barbora())
    all_deals.extend(scrape_rimi())

    if not all_deals:
        print("Nerasta jokių pasiūlymų.")
        return

    for idx, item in enumerate(all_deals, 1):
        item["id"] = idx

    with open("deals.json", "w", encoding="utf-8") as f:
        json.dump(all_deals, f, ensure_ascii=False, indent=2)
        
    print(f"Iš viso sėkmingai atnaujinta: {len(all_deals)} pasiūlymų.")

if __name__ == "__main__":
    main()
