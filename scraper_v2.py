import requests
from bs4 import BeautifulSoup
import json

def scrape_mxgp_results(category="mxgp"):
    # URL naar de algemene standings pagina van mxgpresults
    url = f"https://mxgpresults.com/{category}/standings"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    riders = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        # De eerste tabel op de pagina bevat de kampioenschapsstand
        table = soup.find('table')
        if not table: return None
        
        rows = table.find_all('tr')[1:] # Skip de header-rij
        
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
        print(f"Error scraping {category}: {e}")
        return None

def main():
    print("Starting V2 Scraping from mxgpresults.com...")
    
    mxgp_riders = scrape_mxgp_results("mxgp")
    mx2_riders = scrape_mxgp_results("mx2")
    
    # We houden de structuur simpel voor data.json
    full_data = {
        "calendar": [], # Placeholder voor later
        "mxgp": {"title": "MXGP STANDINGS", "riders": mxgp_riders or []},
        "mx2": {"title": "MX2 STANDINGS", "riders": mx2_riders or []}
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=4, ensure_ascii=False)
    
    print("Scraping complete. Saved to data.json")

if __name__ == "__main__":
    main()
