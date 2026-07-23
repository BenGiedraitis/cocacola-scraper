import json
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def extract_volume(title):
    """Ištraukti tūrį iš pavadinimo"""
    match = re.search(r'(\d+(?:[.,]\d+)?)\s*([lL]|ml)', title)
    if match:
        volume = float(match.group(1).replace(',', '.'))
        unit = match.group(2).lower()
        if unit == 'ml':
            volume_l = volume / 1000
            return f"{volume_l:.2f} l", volume_l
        return f"{volume} l", volume
    return "1 l", 1.0

def detect_type(title):
    """Nustatyti pakuotės tipą"""
    title_lower = title.lower()
    if 'skardin' in title_lower or 'can' in title_lower:
        return 'can'
    elif 'stikl' in title_lower or 'glass' in title_lower:
        return 'glass'
    return 'bottle'

def scrape_deals():
    deals = []
    
    # Pabandyk iš Maxima (pavyzdys)
    try:
        # Čia tavo scraperio kodas...
        # Kol kas naudojam pavyzdinius duomenis su visais laukais
        pass
    except Exception as e:
        print(f"Scraping error: {e}")
    
    # FALLBACK duomenys su visais reikalingais laukais
    fallback_deals = [
        {
            'store': 'Maxima',
            'title': 'Coca-Cola 2L',
            'price': 1.99,
            'oldPrice': 2.49,
            'volume': '2 l',
            'volumeLiters': 2.0,
            'discount': 20,
            'validUntil': '2026-08-01',
            'type': 'bottle'
        },
        {
            'store': 'IKI',
            'title': 'Coca-Cola 0.5L',
            'price': 0.89,
            'oldPrice': 1.19,
            'volume': '0.5 l',
            'volumeLiters': 0.5,
            'discount': 25,
            'validUntil': '2026-07-31',
            'type': 'bottle'
        },
        {
            'store': 'Rimi',
            'title': 'Coca-Cola skardinė 0.33L',
            'price': 0.59,
            'oldPrice': 0.79,
            'volume': '0.33 l',
            'volumeLiters': 0.33,
            'discount': 25,
            'validUntil': '2026-07-30',
            'type': 'can'
        },
        {
            'store': 'Lidl',
            'title': 'Coca-Cola 1.5L',
            'price': 1.49,
            'oldPrice': 1.99,
            'volume': '1.5 l',
            'volumeLiters': 1.5,
            'discount': 25,
            'validUntil': '2026-07-29',
            'type': 'bottle'
        },
        {
            'store': 'Norfa',
            'title': 'Coca-Cola stiklas 0.33L',
            'price': 0.99,
            'oldPrice': 1.29,
            'volume': '0.33 l',
            'volumeLiters': 0.33,
            'discount': 23,
            'validUntil': '2026-07-28',
            'type': 'glass'
        }
    ]
    
    # Panaudojam fallback, jei scraperis nieko negavo
    if not deals:
        deals = fallback_deals
    
    # Išsaugom
    with open('deals.json', 'w', encoding='utf-8') as f:
        json.dump({
            'lastUpdated': datetime.now().isoformat(),
            'deals': deals
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Išsaugota {len(deals)} pasiūlymų")

if __name__ == "__main__":
    scrape_deals()
