import requests
from bs4 import BeautifulSoup
import json

def get_headers():
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def scrape_table_rows(table):
    results = []
    if not table: return []
    rows = table.find_all('tr')[1:] # Sla de header over
    for row in rows:
        cols = row.find_all('td')
        # We baseren ons op jouw lijn: 0=Pos, 1=Num, 2=Naam, 3=Bike, 4=Nation, 5=Points
        if len(cols) >= 6:
            name_cell = cols[2].find('a')
            name = name_cell.get_text(strip=True) if name_cell else cols[2].get_text(strip=True)
            results.append({
                "pos": cols[0].get_text(strip=True),
                "num": cols[1].get_text(strip=True).replace('#', ''),
                "name": name.upper(),
                "bike": cols[3].get_text(strip=True).upper(),
                "pts": cols[5].get_text(strip=True)
            })
    return results

def scrape_mxgp():
    data = {"mxgp": [], "mx2": [], "calendar": []}
    
    # 1. Standings
    for cat in ["mxgp", "mx2"]:
        res = requests.get(f"https://mxgpresults.com/{cat}/standings", headers=get_headers())
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('section', id='standings').find('table')
        data[cat] = scrape_table_rows(table)

    # 2. Kalender (We pakken ALLE rijen in de tabel, niet alleen SportsEvents)
    res = requests.get("https://mxgpresults.com/mxgp/calendar", headers=get_headers())
    soup = BeautifulSoup(res.text, 'html.parser')
    calendar_table = soup.find('table')
    if calendar_table:
        for row in calendar_table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 3:
                link_tag = cols[1].find('a')
                url = link_tag['href'] if link_tag else None
                
                event = {
                    "round": cols[0].get_text(strip=True),
                    "gp": cols[1].find('span', itemprop="name").get_text(strip=True).upper() if cols[1].find('span') else cols[1].get_text(strip=True).upper(),
                    "loc": cols[1].find('small').get_text(strip=True) if cols[1].find('small') else "",
                    "date": cols[2].get_text(strip=True),
                    "mxgp_res": [],
                    "mx2_res": []
                }
                
                if url:
                    # Haal de uitslag op als de link bestaat
                    res_page = requests.get(f"https://mxgpresults.com{url}", headers=get_headers())
                    res_soup = BeautifulSoup(res_page.text, 'html.parser')
                    # Zoek specifiek naar de uitslagentabel
                    res_table = res_soup.find('div', id='gpclassification')
                    if res_table:
                        event["mxgp_res"] = scrape_table_rows(res_table.find('table'))
                        # Probeer ook MX2 link
                        mx2_url = url.replace('/mxgp/', '/mx2/')
                        mx2_res_page = requests.get(f"https://mxgpresults.com{mx2_url}", headers=get_headers())
                        mx2_table = BeautifulSoup(mx2_res_page.text, 'html.parser').find('div', id='gpclassification')
                        if mx2_table:
                            event["mx2_res"] = scrape_table_rows(mx2_table.find('table'))
                
                data["calendar"].append(event)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    scrape_mxgp()
