import requests
from bs4 import BeautifulSoup
import json

def get_headers():
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def scrape_mxgp_results(category="mxgp"):
    url = f"https://mxgpresults.com/{category}/standings"
    data = {"title": f"{category.upper()} STANDINGS", "riders": []}
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('section', id='standings').find('table')
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 5:
                data["riders"].append({
                    "pos": cols[0].get_text(strip=True),
                    "number": cols[1].get_text(strip=True).replace('#', ''),
                    "name": cols[2].get_text(strip=True).upper(),
                    "bike": cols[3].get_text(strip=True).upper(),
                    "points": cols[-1].get_text(strip=True)
                })
        return data
    except: return None

def scrape_race_results(race_url):
    results = []
    try:
        full_url = f"https://mxgpresults.com{race_url}"
        response = requests.get(full_url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # We zoeken de tabel in de div 'gpclassification' of met class 'ses'
        table = soup.find('table', class_='ses') or soup.find('div', id='gpclassification').find('table')
        if not table: return []
        
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            # Jouw HTML heeft 6 kolommen: 0=Pos, 1=Num, 2=Rider, 3=Bike, 4=Nation, 5=Points
            if len(cols) >= 6:
                results.append({
                    "pos": cols[0].get_text(strip=True),
                    "number": cols[1].get_text(strip=True).replace('#', ''),
                    "name": cols[2].get_text(strip=True).upper(),
                    "bike": cols[3].get_text(strip=True).upper(),
                    "points": cols[5].get_text(strip=True) # Pak specifiek kolom 5 (Points)
                })
        return results
    except: return []

def scrape_calendar():
    url = "https://mxgpresults.com/mxgp/calendar"
    events = []
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        for row in soup.find_all('tr', itemtype="https://schema.org/SportsEvent"):
            cols = row.find_all('td')
            link = row.find('span', itemprop="name").find('a')
            if link:
                race_link = link['href']
                events.append({
                    "round": cols[0].get_text(strip=True),
                    "gp": link.get_text(strip=True).upper(),
                    "loc": row.find('small', itemprop="location").get_text(strip=True),
                    "date": cols[2].get_text(strip=True),
                    "mxgp_results": scrape_race_results(race_link),
                    "mx2_results": scrape_race_results(race_link.replace('/mxgp/', '/mx2/'))
                })
        return events
    except: return []

if __name__ == "__main__":
    mxgp = scrape_mxgp_results("mxgp")
    mx2 = scrape_mxgp_results("mx2")
    cal = scrape_calendar()
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump({"calendar": cal, "mxgp": mxgp, "mx2": mx2}, f, indent=4)
