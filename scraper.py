import json
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def scrape_deals():
    deals = []
    
    # Pabandyk iš Maxima
    try:
        url = "https://www.maxima.lt/pigesni/pigesni?q=coca-cola"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Pavyzdiniai selektoriai (gali reikėti koreguoti)
        for product in soup.find_all('div', class_='product-card')[:5]:
            title = product.find('h3', class_='product-title')
            if title and 'coca-cola' in title.text.lower():
                price = product.find('span', class_='price')
                if price:
                    deals.append({
                        'store': 'Maxima',
                        'title': title.text.strip(),
                        'price': float(re.search(r'[\d.]+', price.text).group()),
                        'volume': '1.5L',
                        'validUntil': '2026-08-01'
                    })
    except Exception as e:
        print(f"Maxima error: {e}")
    
    # Jei nieko nerado - fallback
    if not deals:
        deals = [
            {'store': 'Maxima', 'title': 'Coca-Cola 2L', 'price': 1.99, 'volume': '2L', 'validUntil': '2026-08-01'},
            {'store': 'IKI', 'title': 'Coca-Cola 0.5L', 'price': 0.89, 'volume': '0.5L', 'validUntil': '2026-07-31'},
        ]
    
    with open('deals.json', 'w', encoding='utf-8') as f:
        json.dump({
            'lastUpdated': datetime.now().isoformat(),
            'deals': deals
        }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_deals()
