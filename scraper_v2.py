import requests
from bs4 import BeautifulSoup
import json
import time

def get_headers():
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def scrape_table_row_by_row(table):
    results = []
    if not table: return []
    rows = table.find_all('tr')[1:] # Skip header
    for row in rows:
        cols = row.find_all('td')
        # We baseren ons op jouw exacte HTML-voorbeeld (minimaal 6 kolommen)
        if len(cols) >= 6:
            # Haal de naam uit de <a> tag in de derde kolom
            name_link = cols[2].find('a')
            name_text = name_link.get_text(strip=True) if name_link else cols[2].get_text(strip=True)
            
            results.append({
                "pos": cols[0].get_text(strip=True),
                "num": cols[1].get_text(strip=True).replace('#', ''),
                "name": name_text.upper(),
                "bike": cols[3].get_text(strip=True).upper(),
                "pts": cols[5].get_text(strip=True)
            })
    return results

def scrape_mxgp():
    data = {"mxgp": {"title": "MXGP STANDINGS", "riders": []}, "mx2": {"title": "MX2 STANDINGS", "riders": []}, "calendar": []}
    
    # 1. Standings (Hoofdpagina)
    for cat in ["mxgp", "mx2"]:
        try:
            res = requests.get(f"https://mxgpresults.com/{cat}/standings", headers=get_headers())
            soup = BeautifulSoup(res.text, 'html.parser')
            table = soup.find('section', id='standings').find('table')
            data[cat]["riders"] = scrape_table_row_by_row(table)
        except: pass

    # 2. Kalender & Resultaten (Detailpagina's)
    try:
        res = requests.get("https://mxgpresults.com/mxgp/calendar", headers=get_headers())
        soup = BeautifulSoup(res.text, 'html.parser')
        calendar_rows = soup.find_all('tr')[1:]
        
        for row in calendar_rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                link = cols[1].find('a')
                event = {
                    "round": cols[0].get_text(strip=True),
                    "gp": cols[1].find('span', itemprop="name").get_text(strip=True).upper() if cols[1].find('span') else cols[1].get_text(strip=True).split('\n')[0].upper(),
                    "loc": cols[1].find('small').get_text(strip=True) if cols[1].find('small') else "",
                    "date": cols[2].get_text(strip=True),
                    "mxgp_res": [], "mx2_res": []
                }
                
                if link:
                    base_url = link['href']
                    for cat in ["mxgp", "mx2"]:
                        r_url = f"https://mxgpresults.com{base_url.replace('/mxgp/', f'/{cat}/')}"
                        r_res = requests.get(r_url, headers=get_headers())
                        r_soup = BeautifulSoup(r_res.text, 'html.parser')
                        # Zoek specifiek de tabel in het gpclassification blok
                        container = r_soup.find('div', id='gpclassification')
                        if container and container.find('table'):
                            event[f"{cat}_res"] = scrape_table_row_by_row(container.find('table'))
                        time.sleep(0.5)
                data["calendar"].append(event)
    except: pass

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    scrape_mxgp()
