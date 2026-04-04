import requests
from bs4 import BeautifulSoup
import json

def get_headers():
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def clean_table(table):
    """Parsen van de GP resultaten met extra beveiliging tegen 'tekst-lekken'"""
    results = []
    if not table: return []
    
    # We zoeken specifiek de rijen in de tbody om de header over te slaan
    tbody = table.find('tbody')
    rows = tbody.find_all('tr', recursive=False) if tbody else table.find_all('tr')[1:]
    
    for row in rows:
        cols = row.find_all('td', recursive=False)
        # De tabel heeft 6 kolommen (Pos, Num, Rider, Bike, Nation, Pts)
        if len(cols) >= 5:
            # We pakken alleen de directe tekst van de cel (geen geneste rommel)
            pos = cols[0].get_text(strip=True)
            num = cols[1].get_text(strip=True).replace('#', '')
            
            # Naam zit vaak in een link, anders gewoon de tekst
            name_link = cols[2].find('a')
            name = name_link.get_text(strip=True) if name_link else cols[2].get_text(strip=True)
            
            bike = cols[3].get_text(strip=True)
            # Punten is meestal de laatste kolom
            pts = cols[-1].get_text(strip=True)
            
            if pos and name: # Alleen toevoegen als er echt data is
                results.append({
                    "pos": pos,
                    "num": num,
                    "name": name.upper(),
                    "bike": bike.upper(),
                    "pts": pts
                })
    return results

def scrape_mxgp():
    data = {"mxgp": {"title": "MXGP STANDINGS", "riders": []}, "mx2": {"title": "MX2 STANDINGS", "riders": []}, "calendar": []}
    
    # 1. Standings parsen met de robuuste lxml parser
    for cat in ["mxgp", "mx2"]:
        try:
            res = requests.get(f"https://mxgpresults.com/{cat}/standings", headers=get_headers())
            soup = BeautifulSoup(res.text, 'lxml') # Gebruik lxml!
            section = soup.find('section', id='standings')
            if section and section.find('table'):
                rows = section.find('table').find_all('tr')[1:]
                for r in rows:
                    c = r.find_all('td', recursive=False)
                    if len(c) >= 4:
                        data[cat]["riders"].append({
                            "pos": c[0].get_text(strip=True),
                            "num": c[1].get_text(strip=True).replace('#', ''),
                            "name": c[2].get_text(strip=True).upper(),
                            "bike": c[3].get_text(strip=True).upper(),
                            "pts": c[-1].get_text(strip=True)
                        })
        except Exception as e:
            print(f"Error standings {cat}: {e}")

    # 2. Kalender & Resultaten
    try:
        res = requests.get("https://mxgpresults.com/mxgp/calendar", headers=get_headers())
        soup = BeautifulSoup(res.text, 'lxml')
        rows = soup.find_all('tr')[1:]
        
        for row in rows:
            cols = row.find_all('td', recursive=False)
            if len(cols) >= 3:
                link = cols[1].find('a')
                event = {
                    "round": cols[0].get_text(strip=True),
                    "gp": cols[1].find('span', itemprop="name").get_text(strip=True).upper() if cols[1].find('span') else cols[1].get_text(strip=True).upper(),
                    "loc": cols[1].find('small').get_text(strip=True) if cols[1].find('small') else "",
                    "date": cols[2].get_text(strip=True),
                    "mxgp_res": [], "mx2_res": []
                }
                
                if link:
                    url = link['href']
                    for c_cat in ["mxgp", "mx2"]:
                        r_url = f"https://mxgpresults.com{url.replace('/mxgp/', f'/{c_cat}/')}"
                        r_res = requests.get(r_url, headers=get_headers())
                        r_soup = BeautifulSoup(r_res.text, 'lxml')
                        
                        # Zoek de specifieke resultaten-tabel
                        table = r_soup.find('table', class_='ses')
                        if not table:
                            div = r_soup.find('div', id='gpclassification')
                            if div: table = div.find('table')
                        
                        if table:
                            event[f"{c_cat}_res"] = clean_table(table)
                
                data["calendar"].append(event)
    except Exception as e:
        print(f"Error calendar: {e}")

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    scrape_mxgp()
