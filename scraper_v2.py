import requests
from bs4 import BeautifulSoup
import json

def get_headers():
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def parse_mxgp_table(table):
    """Universele functie voor zowel Standings als Race Results"""
    results = []
    if not table: return []
    rows = table.find_all('tr')[1:] # Sla de header over
    for row in rows:
        cols = row.find_all('td')
        # Structuur: 0:Pos, 1:Num, 2:Rider, 3:Bike, 4:Nat, 5:Points
        if len(cols) >= 5:
            # Pak de naam uit de link, of gewoon de tekst
            name_link = cols[2].find('a')
            name = name_link.get_text(strip=True) if name_link else cols[2].get_text(strip=True)
            
            results.append({
                "pos": cols[0].get_text(strip=True),
                "number": cols[1].get_text(strip=True).replace('#', ''),
                "name": name.upper(),
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
                title_h2 = section.find('h2')
                if title_h2: data[cat]["title"] = title_h2.get_text(strip=True).upper()
                data[cat]["riders"] = parse_mxgp_table(section.find('table'))
        except: pass

    # 2. Kalender
    try:
        res = requests.get("https://mxgpresults.com/mxgp/calendar", headers=get_headers())
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.find_all('tr', itemtype="https://schema.org/SportsEvent") or soup.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                link = cols[1].find('a')
                gp_name = cols[1].find('span', itemprop="name")
                event = {
                    "round": cols[0].get_text(strip=True),
                    "gp": gp_name.get_text(strip=True).upper() if gp_name else cols[1].get_text(strip=True).split('\n')[0].upper(),
                    "loc": cols[1].find('small').get_text(strip=True) if cols[1].find('small') else "",
                    "date": cols[2].get_text(strip=True),
                    "mxgp_res": [], "mx2_res": []
                }
                if link:
                    url = link['href']
                    # Haal uitslagen voor deze specifieke GP
                    for c_cat in ["mxgp", "mx2"]:
                        r_url = f"https://mxgpresults.com{url.replace('/mxgp/', f'/{c_cat}/')}"
                        r_res = requests.get(r_url, headers=get_headers())
                        r_soup = BeautifulSoup(r_res.text, 'html.parser')
                        container = r_soup.find('div', id='gpclassification')
                        if container:
                            event[f"{c_cat}_res"] = parse_mxgp_table(container.find('table'))
                data["calendar"].append(event)
    except: pass

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    scrape_mxgp()
