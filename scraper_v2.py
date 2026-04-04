import requests
from bs4 import BeautifulSoup
import json

def get_headers():
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def clean_table(table):
    results = []
    if not table: return []
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td', recursive=False)
        if len(cols) >= 5:
            pos = cols[0].get_text(strip=True)
            if not pos.isdigit(): continue 
            num = cols[1].get_text(strip=True).replace('#', '')
            name_cell = cols[2]
            name = name_cell.find('a').get_text(strip=True) if name_cell.find('a') else name_cell.get_text(strip=True)
            bike = cols[3].get_text(strip=True)
            pts_or_time = cols[-1].get_text(strip=True) # Punten bij race, tijd bij Quali
            
            results.append({
                "pos": pos, "num": num, "name": name.upper(),
                "bike": bike.upper(), "val": pts_or_time
            })
    return results

def scrape_mxgp():
    data = {"mxgp": {"title": "MXGP STANDINGS 2026", "riders": []}, "mx2": {"title": "MX2 STANDINGS 2026", "riders": []}, "calendar": []}
    
    # 1. Klassementen
    for cat in ["mxgp", "mx2"]:
        try:
            res = requests.get(f"https://mxgpresults.com/{cat}/standings", headers=get_headers(), timeout=10)
            soup = BeautifulSoup(res.text, 'lxml')
            container = soup.find('section', id='standings') or soup
            table = container.find('table')
            if table:
                # Hergebruik clean_table maar hernoem 'val' naar 'pts' voor standings
                raw_riders = clean_table(table)
                data[cat]["riders"] = [{"pos": r["pos"], "num": r["num"], "name": r["name"], "bike": r["bike"], "pts": r["val"]} for r in raw_riders]
        except Exception as e: print(f"Error standings {cat}: {e}")

    # 2. Kalender & Sessie Resultaten
    try:
        res = requests.get("https://mxgpresults.com/mxgp/calendar", headers=get_headers(), timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        main_table = soup.find('table')
        if main_table:
            for row in main_table.find_all('tr')[1:]:
                cols = row.find_all('td', recursive=False)
                if len(cols) >= 3:
                    link_tag = cols[1].find('a')
                    event = {
                        "round": cols[0].get_text(strip=True),
                        "gp": cols[1].find('span', itemprop="name").get_text(strip=True).upper() if cols[1].find('span') else cols[1].get_text(strip=True).upper(),
                        "loc": cols[1].find('small').get_text(strip=True) if cols[1].find('small') else "",
                        "date": cols[2].get_text(strip=True),
                        "mxgp": {"overall": [], "quali": [], "r1": [], "r2": []},
                        "mx2": {"overall": [], "quali": [], "r1": [], "r2": []}
                    }
                    
                    if link_tag:
                        base_url = link_tag['href']
                        for c_cat in ["mxgp", "mx2"]:
                            r_url = f"https://mxgpresults.com{base_url.replace('/mxgp/', f'/{c_cat}/')}"
                            r_soup = BeautifulSoup(requests.get(r_url, headers=get_headers()).text, 'lxml')
                            
                            # Map de div ID's naar onze JSON structuur
                            sessions = {"gpclassification": "overall", "qualifying": "quali", "race1": "r1", "race2": "r2"}
                            for div_id, key in sessions.items():
                                section = r_soup.find('div', id=div_id)
                                if section:
                                    event[c_cat][key] = clean_table(section.find('table'))
                    data["calendar"].append(event)
    except Exception as e: print(f"Error calendar: {e}")

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    scrape_mxgp()
