import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_mxgp_results(year, category="mxgp"):
    # URL structuur voor mxgpresults: mxgp of mx2
    url = f"https://mxgpresults.com/{category}/standings/{year}/{category}.html"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    riders = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        # De tabel op mxgpresults heeft meestal geen class, maar is de enige grote tabel
        table = soup.find('table')
        if not table: return None
        
        rows = table.find_all('tr')[1:] # Skip header row
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                # Kolom mapping mxgpresults: 
                # 0:Pos, 1:Nr, 2:Rider, 3:Bike, ..., last: Points
                riders.append({
                    "pos": cols[0].get_text(strip=True),
                    "number": cols[1].get_text(strip=True),
                    "name": cols[2].get_text(strip=True).upper(),
                    "bike": cols[3].get_text(strip=True).upper(),
                    "points": cols[-1].get_text(strip=True)
                })
        return riders
    except Exception as e:
        print(f"Error scraping {category} {year}: {e}")
        return None

def main():
    # We focussen nu op het huidige jaar (2026)
    year = 2026 
    print(f"Starting V2 Scraping for {year}...")
    
    mxgp_riders = scrape_mxgp_results(year, "mxgp")
    mx2_riders = scrape_mxgp_results(year, "mx2")
    
    # We houden de kalender voorlopig simpel of halen deze later op
    # (mxgpresults heeft een andere kalender-url, dit is een placeholder)
    calendar_data = [
        {"round": "1", "date": "March 2026", "gp": "Coming Soon", "loc": "Track TBD"}
    ]

    full_data = {
        "year": year,
        "calendar": calendar_data,
        "mxgp": {"title": f"MXGP STANDINGS {year}", "riders": mxgp_riders or []},
        "mx2": {"title": f"MX2 STANDINGS {year}", "riders": mx2_riders or []}
    }

    # Opslaan voor de website
    with open(f"data_{year}.json", 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=4, ensure_ascii=False)
    
    # Index bestand maken
    with open('years_index.json', 'w') as f:
        json.dump({"available_years": [year]}, f)
    
    print("V2 Data update complete.")

if __name__ == "__main__":
    main()
