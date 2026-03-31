import requests
from bs4 import BeautifulSoup
import json

def get_headers():
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean_table(table):
    """De 'Argentina' logica toegepast op elke tabel"""
    results = []
    if not table: return []
    rows = table.find_all('tr')[1:] 
    for row in rows:
        cols = row.find_all('td')
        # We mikken op de 6-koloms structuur uit jouw voorbeeld
        if len(cols) >= 6:
            name_cell = cols[2].find('a').get_text(strip=True) if cols[2].find('a') else cols[2].get_text(strip=True)
            results.append({
                "pos": cols[0].get_text(strip=True),
                "num": cols[1].get_text(strip=True).replace('#', ''),
                "name": name_cell.upper(),
                "bike": cols[3].get_text(strip=True).upper(),
                "pts": cols[5].get_text(strip=True)
            })
    return results

def scrape_mxgp():
    data = {"mxgp": {"title": "MXGP STANDINGS", "riders": []}, "mx2": {"title": "MX2 STANDINGS", "riders": []}, "calendar": []}
    
    # 1. Standings
    for cat in ["mxgp", "mx2"]:
        res = requests.get(f"https://mxgpresults.com/{cat}/standings", headers=get_headers())
        soup = BeautifulSoup(res.text, 'html.parser')
        section = soup.find('section', id='standings')
        if section:
            h2 = section.find('h2')
            if h2: data[cat]["title"] = h2.get_text(strip=True).upper()
            # Standings hebben soms 5 kolommen (geen Nation), we passen de helper aan
            rows = section.find('table').find_all('tr')[1:]
            for r in rows:
                c = r.find_all('td')
                if len(c) >= 4:
                    data[cat]["riders"].append({
                        "pos": c[0].get_text(strip=True),
                        "num": c[1].get_text(strip=True).replace('#', ''),
                        "name": c[2].get_text(strip=True).upper(),
                        "bike": c[3].get_text(strip=True).upper(),
                        "pts": c[-1].get_text(strip=True)
                    })

    # 2. Kalender & Live Resultaten
    res = requests.get("https://mxgpresults.com/mxgp/calendar", headers=get_headers())
    soup = BeautifulSoup(res.text, 'html.parser')
    for row in soup.find_all('tr')[1:]:
        cols = row.find_all('td')
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
                # Haal uitslagen op via de Argentina-methode
                for c_cat in ["mxgp", "mx2"]:
                    r_url = f"https://mxgpresults.com{url.replace('/mxgp/', f'/{c_cat}/')}"
                    r_soup = BeautifulSoup(requests.get(r_url, headers=get_headers()).text, 'html.parser')
                    table = r_soup.find('div', id='gpclassification')
                    if table:
                        event[f"{c_cat}_res"] = clean_table(table.find('table'))
            data["calendar"].append(event)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    scrape_mxgp()
