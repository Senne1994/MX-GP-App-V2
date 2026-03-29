import requests
from bs4 import BeautifulSoup
import json

def scrape_mxgp_results(category="mxgp"):
    url = f"https://mxgpresults.com/{category}/standings"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    data = {"title": f"{category.upper()} STANDINGS", "riders": []}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Zoek specifiek de standings sectie
        section = soup.find('section', id='standings')
        if not section: return None

        # Haal de titel live van de website (h2)
        title_h2 = section.find('h2')
        if title_h2:
            data["title"] = title_h2.get_text(strip=True).upper()
        
        # Pak de tabel binnen deze sectie
        table = section.find('table')
        if not table: return None
        
        rows = table.find_all('tr')[1:] 
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                # .replace('#', '') verwijdert het hekje van de bronwebsite
                raw_number = cols[1].get_text(strip=True)
                clean_number = raw_number.replace('#', '')
                
                data["riders"].append({
                    "pos": cols[0].get_text(strip=True),
                    "number": clean_number,
                    "name": cols[2].get_text(strip=True).upper(),
                    "bike": cols[3].get_text(strip=True).upper(),
                    "points": cols[-1].get_text(strip=True)
                })
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    mxgp_data = scrape_mxgp_results("mxgp")
    mx2_data = scrape_mxgp_results("mx2")
    
    full_data = {
        "calendar": [],
        "mxgp": mxgp_data,
        "mx2": mx2_data
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=4, ensure_ascii=False)
    print("Klaar! Hekjes zijn verwijderd en titels zijn live.")

if __name__ == "__main__":
    main()
