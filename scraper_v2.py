import requests
from bs4 import BeautifulSoup
import json
import time

def get_headers():
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean_results_table(table):
    """Universele, surgical-precision tabel scraper"""
    results = []
    if not table: return []
    rows = table.find_all('tr')[1:] # Sla header over
    for row in rows:
        cols = row.find_all('td')
        
        # We mikken op de 6-koloms structuur uit jouw voorbeeld:
        # 0=Pos, 1=Num, 2=Rider, 3=Bike, 4=Nat, 5=Points
        if len(cols) >= 5:
            # Pak de pure tekst uit de vakjes, zonder hekjes of rommel
            clean_name = cols[2].get_text(strip=True).upper()
            
            results.append({
                "pos": cols[0].get_text(strip=True),
                "number": cols[1].get_text(strip=True).replace('#', ''),
                "name": clean_name,
                "bike": cols[3].get_text(strip=True).upper(),
                "points": cols[-1].get_text(strip=True) # Pak altijd de laatste kolom voor punten
            })
    return results

def scrape_mxgp():
    data = {"mxgp": {"title": "MXGP STANDINGS", "riders": []}, "mx2": {"title": "MX2 STANDINGS", "riders": []}, "calendar": []}
    
    # 1. Standings
    for cat in ["mxgp", "mx2"]:
        try:
            res = requests.get(f"https://mxgpresults.com/{cat}/standings", headers=get_headers())
            soup = BeautifulSoup(res.text, 'html.parser')
            section = soup.find('section', id='standings')
            if section:
                h2 = section.find('h2')
                if h2: data[cat]["title"] = h2.get_text(strip=True).upper()
                
                # Standings tabel kan soms 5 of 6 kolommen hebben, de helper fixt het
                data[cat]["riders"] = clean_results_table(section.find('table'))
        except: pass

    # 2. Kalender & Resultaten (Surgical fix toegepast op alle races)
    try:
        res = requests.get("https://mxgpresults.com/mxgp/calendar", headers=get_headers())
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.find_all('tr')[1:] # Sla header over
        
        for row in rows:
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
                    url = link['href']
                    # Haal uitslagen op voor beide klasses
                    for c_cat in ["mxgp", "mx2"]:
                        # Wissel mxgp naar mx2 in de URL voor de andere klasse
                        class_url = f"https://mxgpresults.com{url.replace('/mxgp/', f'/{c_cat}/')}"
                        r_res = requests.get(class_url, headers=get_headers())
                        r_soup = BeautifulSoup(r_res.text, 'html.parser')
                        # Zoek de tabel in 'gpclassification' of met class 'ses'
                        r_container = r_soup.find('div', id='gpclassification')
                        if r_container:
                            r_table = r_container.find('table')
                            if r_table:
                                # Gebruik onze universele cleantable logica
                                event[f"{c_cat}_res"] = clean_results_table(r_table)
                        # Slaap even tegen blocking
                        time.sleep(1)
                data["calendar"].append(event)
    except: pass

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    scrape_mxgp()
