import json
import re
from bs4 import BeautifulSoup
from curl_cffi import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "lt-LT,lt;q=0.9,en-US;q=0.8,en;q=0.7",
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

def normalize_store(name):
    n = name.lower()
    if 'maxima' in n: return 'Maxima'
    if 'iki' in n: return 'IKI'
    if 'rimi' in n: return 'Rimi'
    if 'lidl' in n: return 'Lidl'
    if 'norfa' in n: return 'Norfa'
    return 'Kita'

def scrape_pricer():
    deals = []
    url = "https://pricer.lt/cenos/search?query=coca-cola"
    
    try:
        # impersonate="chrome" apsaugo nuo 403 blokavimo simuliuodamas naršyklės TLS
        res = requests.get(url, headers=HEADERS, impersonate="chrome", timeout=15)
        if res.status_code != 200:
            print(f"Pricer.lt HTTP klaida: {res.status_code}")
            return deals

        soup = BeautifulSoup(res.text, 'html.parser')
        
        items = soup.select('.product-item, .search-result-item, tr.product-row, .product')
        
        if not items:
            items = soup.find_all(lambda tag: tag.name == 'div' and 'coca-cola' in tag.get_text().lower())

        for item in items:
            text = item.get_text(" ", strip=True)
            if 'coca-cola' not in text.lower():
                continue
            
            title_elem = item.find(['h3', 'h4', 'a', 'span'], class_=re.compile(name='title|name', flags=re.I))
            title = title_elem.get_text(strip=True) if title_elem else "Coca-Cola"
            
            if 'coca-cola' not in title.lower():
                title = "Coca-Cola"

            prices = re.findall(r'([\d\.,]+)\s*€', text)
            price = float(prices[0].replace(',', '.')) if prices else 0.0
            if price == 0.0:
                continue

            old_price = float(prices[1].replace(',', '.')) if len(prices) > 1 else None
            
            discount = 0
            if old_price and old_price > price:
                discount = int(round(((old_price - price) / old_price) * 100))

            vol_liters = parse_volume(title + " " + text)
            store = normalize_store(text)

            deals.append({
                "store": store,
                "title": title,
                "volume": f"{vol_liters} l",
                "volumeLiters": vol_liters,
                "price": price,
                "oldPrice": old_price,
                "discount": discount,
                "type": detect_type(title),
                "validUntil": "Pricer.lt"
            })

    except Exception as e:
        print(f"Pricer klaida: {e}")

    return deals

def main():
    all_deals = scrape_pricer()

    for idx, item in enumerate(all_deals, 1):
        item["id"] = idx

    with open("deals.json", "w", encoding="utf-8") as f:
        json.dump(all_deals, f, ensure_ascii=False, indent=2)
        
    print(f"Sėkmingai rasta ir įrašyta: {len(all_deals)} pasiūlymų.")

if __name__ == "__main__":
    main()
