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
        
        # Target de specifieke standings sectie
        section = soup.find('section', id='standings')
        if not section: return None
        
        # Pak de titel van de pagina
        title_h2 = section.find('h2')
        if title_h2: data["title"] = title_h2.get_text(strip=True).upper()
        
        table = section.find('table')
        if not table: return None
        
        rows = table.find_all('tr')[1:] 
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                # Verwijder het hekje (#) uit het rugnummer
                clean_number = cols[1].get_text(strip=True).replace('#', '')
                data["riders"].append({
                    "pos": cols[0].get_text(strip=True),
                    "number": clean_number,
                    "name": cols[2].get_text(strip=True).upper(),
                    "bike": cols[3].get_text(strip=True).upper(),
                    "points": cols[-1].get_text(strip=True)
                })
        return data
    except Exception as e:
        print(f"Error standings: {e}")
        return None

def scrape_calendar():
    url = "https://mxgpresults.com/mxgp/calendar"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    events = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return []
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Zoek alle rijen die een SportsEvent zijn volgens de HTML structuur
        rows = soup.find_all('tr', itemtype="https://schema.org/SportsEvent")
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                round_num = cols[0].get_text(strip=True)
                gp_name = row.find('span', itemprop="name").get_text(strip=True)
                
                location_tag = row.find('small', itemprop="location")
                location = location_tag.find('span', itemprop="name").get_text(strip=True) if location_tag else "TBD"
                
                date_str = cols[2].get_text(strip=True)
                
                events.append({
                    "round": round_num,
                    "gp": gp_name.upper(),
                    "loc": location,
                    "date": date_str
                })
        return events
    except Exception as e:
        print(f"Error calendar: {e}")
        return []

def main():
    print("Scraping started...")
    mxgp_data = scrape_mxgp_results("mxgp")
    mx2_data = scrape_mxgp_results("mx2")
    calendar_data = scrape_calendar()
    
    full_data = {
        "calendar": calendar_data,
        "mxgp": mxgp_data,
        "mx2": mx2_data
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=4, ensure_ascii=False)
    print(f"Done! Saved {len(calendar_data)} events to data.json")

if __name__ == "__main__":
    main()
