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
    """Ištraukia tūrį litrais iš pavadinimo (pvz. 1.5 l, 0.33 l, 4x0.33 l)"""
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
        session = requests.Session()
        res = session.get(url, headers=HEADERS, timeout=10)
        
        print(f"Barbora API statusas: {res.status_code}")
        if res.status_code != 200:
            return deals
        
        data = res.json()
        products = data.get('products', [])
        print(f"Rasta produktų: {len(products)}")
        
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

def main():
    all_deals = []
    
    barbora_deals = scrape_barbora()
    all_deals.extend(barbora_deals)
    
    # Jei nerasta nieko – sukuriam tuščią masyvą arba paliekam seną, kad lūžtų ne git push, o matytųsi loguose
    if not all_deals:
        print("Dėmesio: Barboros API negrąžino prekių. Rašomas tuščias masyvas arba stabdoma.")
        # Kad nepaliktume visiškai tuščio failo, įrašom bent tuščią sąrašą arba išeinam
        all_deals = []

    # Suteikiami ID
    for idx, item in enumerate(all_deals, 1):
        item["id"] = idx

    # Įrašymas į deals.json
    with open("deals.json", "w", encoding="utf-8") as f:
        json.dump(all_deals, f, ensure_ascii=False, indent=2)
        
    print(f"Sėkmingai atnaujinta {len(all_deals)} pasiūlymų.")

if __name__ == "__main__":
    main()
