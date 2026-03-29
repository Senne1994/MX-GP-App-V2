import requests
from bs4 import BeautifulSoup
import json

def get_headers():
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def scrape_mxgp():
    data = {"mxgp": {"title": "MXGP STANDINGS", "riders": []}, "mx2": {"title": "MX2 STANDINGS", "riders": []}, "calendar": []}
    
    # 1. Standings ophalen
    for cat in ["mxgp", "mx2"]:
        try:
            res = requests.get(f"https://mxgpresults.com/{cat}/standings", headers=get_headers())
            soup = BeautifulSoup(res.text, 'html.parser')
            title_h2 = soup.find('section', id='standings').find('h2')
            if title_h2: data[cat]["title"] = title_h2.get_text(strip=True).upper()
            
            table = soup.find('section', id='standings').find('table')
            for row in table.find_all('tr')[1:]:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    data[cat]["riders"].append({
                        "pos": cols[0].get_text(strip=True),
                        "number": cols[1].get_text(strip=True).replace('#', ''),
                        "name": cols[2].get_text(strip=True).upper(),
                        "bike": cols[3].get_text(strip=True).upper(),
                        "points": cols[-1].get_text(strip=True)
                    })
        except: pass

    # 2. Kalender ophalen
    try:
        res = requests.get("https://mxgpresults.com/mxgp/calendar", headers=get_headers())
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.find_all('tr')
        for row in rows[1:]:
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
                    # Scrape GP Classification (Jouw specifieke tabel)
                    for c_cat in ["mxgp", "mx2"]:
                        r_url = f"https://mxgpresults.com{url.replace('/mxgp/', f'/{c_cat}/')}"
                        r_res = requests.get(r_url, headers=get_headers())
                        r_soup = BeautifulSoup(r_res.text, 'html.parser')
                        # Zoek in gpclassification div
                        container = r_soup.find('div', id='gpclassification')
                        target_table = container.find('table') if container else r_soup.find('table', class_='ses')
                        if target_table:
                            for r_row in target_table.find_all('tr')[1:]:
                                r_cols = r_row.find_all('td')
                                if len(r_cols) >= 6: # Gebruik jouw 6-koloms logica
                                    event[f"{c_cat}_res"].append({
                                        "pos": r_cols[0].get_text(strip=True),
                                        "number": r_cols[1].get_text(strip=True).replace('#', ''),
                                        "name": r_cols[2].get_text(strip=True).upper(),
                                        "bike": r_cols[3].get_text(strip=True).upper(),
                                        "points": r_cols[5].get_text(strip=True)
                                    })
                data["calendar"].append(event)
    except: pass

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    scrape_mxgp()
