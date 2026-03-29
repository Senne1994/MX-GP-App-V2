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
        section = soup.find('section', id='standings')
        if not section: return None
        title_h2 = section.find('h2')
        if title_h2: data["title"] = title_h2.get_text(strip=True).upper()
        table = section.find('table')
        rows = table.find_all('tr')[1:] 
        for row in rows:
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
        # We pakken de tabel van de resultaten
        table = soup.find('table')
        if not table: return []
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                # We slaan de 5e kolom (Land) over door specifiek te indexeren
                results.append({
                    "pos": cols[0].get_text(strip=True),
                    "number": cols[1].get_text(strip=True).replace('#', ''),
                    "name": cols[2].get_text(strip=True).upper(),
                    "bike": cols[3].get_text(strip=True).upper(),
                    "points": cols[-1].get_text(strip=True)
                })
        return results
    except: return []

def scrape_calendar():
    url = "https://mxgpresults.com/mxgp/calendar"
    events = []
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr', itemtype="https://schema.org/SportsEvent")
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
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
                    "mxgp_results": [],
                    "mx2_results": []
                }
                if race_link:
                    event["mxgp_results"] = scrape_race_results(race_link)
                    event["mx2_results"] = scrape_race_results(race_link.replace('/mxgp/', '/mx2/'))
                events.append(event)
        return events
    except: return []

def main():
    mxgp = scrape_mxgp_results("mxgp")
    mx2 = scrape_mxgp_results("mx2")
    cal = scrape_calendar()
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump({"calendar": cal, "mxgp": mxgp, "mx2": mx2}, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
