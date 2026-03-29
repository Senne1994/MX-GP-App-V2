import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_headers():
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def scrape_mxgp_results(category="mxgp"):
    url = f"https://mxgpresults.com/{category}/standings"
    data = {"title": f"{category.upper()} STANDINGS", "riders": []}
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.text, 'html.parser')
        section = soup.find('section', id='standings')
        if not section: return None
        title_h2 = section.find('h2')
        if title_h2: data["title"] = title_h2.get_text(strip=True).upper()
        table = section.find('table')
        if not table: return None
        rows = table.find_all('tr')[1:] 
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
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
        print(f"Error standings {category}: {e}")
        return None

def scrape_race_results(race_url):
    """Haalt de eerste tabel (uitslag) op van een specifieke GP pagina"""
    results = []
    try:
        full_url = f"https://mxgpresults.com{race_url}"
        response = requests.get(full_url, headers=get_headers(), timeout=10)
        if response.status_code != 200: return []
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # We pakken de allereerste tabel op de pagina (meestal Overall uitslag)
        table = soup.find('table')
        if not table: return []
        
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                results.append({
                    "pos": cols[0].get_text(strip=True),
                    "number": cols[1].get_text(strip=True).replace('#', ''),
                    "name": cols[2].get_text(strip=True).upper(),
                    "bike": cols[3].get_text(strip=True).upper(),
                    "points": cols[-1].get_text(strip=True)
                })
        return results
    except:
        return []

def scrape_calendar():
    url = "https://mxgpresults.com/mxgp/calendar"
    events = []
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        if response.status_code != 200: return []
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr', itemtype="https://schema.org/SportsEvent")
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                # Check of er een link is naar race resultaten
                link_tag = row.find('span', itemprop="name").find('a')
                race_link = link_tag['href'] if link_tag else None
                
                gp_name = link_tag.get_text(strip=True) if link_tag else row.find('span', itemprop="name").get_text(strip=True)
                
                location_tag = row.find('small', itemprop="location")
                location = location_tag.find('span', itemprop="name").get_text(strip=True) if location_tag else "TBD"
                
                event = {
                    "round": cols[0].get_text(strip=True),
                    "gp": gp_name.upper(),
                    "loc": location,
                    "date": cols[2].get_text(strip=True),
                    "results_url": race_link,
                    "mxgp_results": [],
                    "mx2_results": []
                }
                
                # Als er een link is, haal de resultaten op voor beide klasses
                if race_link:
                    print(f"Scraping race results for {gp_name}...")
                    event["mxgp_results"] = scrape_race_results(race_link)
                    # Wissel mxgp naar mx2 in de URL voor de andere klasse
                    mx2_link = race_link.replace('/mxgp/', '/mx2/')
                    event["mx2_results"] = scrape_race_results(mx2_link)
                
                events.append(event)
        return events
    except Exception as e:
        print(f"Error calendar: {e}")
        return []

def main():
    print(f"Scraping started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
    print("Done! data.json contains standings and race results.")

if __name__ == "__main__":
    main()
