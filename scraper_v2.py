import requests
from bs4 import BeautifulSoup
import json

def get_headers():
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def clean_table(table):
    """Parsen van de GP resultaten tabel (6 kolommen: Pos, Num, Rider, Bike, Nation, Pts)"""
    results = []
    if not table: return []
    
    # We zoeken de rijen in de body
    rows = table.find('tbody').find_all('tr') if table.find('tbody') else table.find_all('tr')[1:]
    
    for row in rows:
        cols = row.find_all('td')
        # De tabel heeft 6 kolommen volgens jouw voorbeeld
        if len(cols) >= 5:
            # Rider naam zit vaak in een <a> tag
            name_cell = cols[2]
            rider_name = name_cell.find('a').get_text(strip=True) if name_cell.find('a') else name_cell.get_text(strip=True)
            
            results.append({
                "pos": cols[0].get_text(strip=True),
                "num": cols[1].get_text(strip=True).replace('#', ''),
                "name": rider_name.upper(),
                "bike": cols[3].get_text(strip=True).upper(),
                "pts": cols[-1].get_text(strip=True) # Pak de laatste kolom voor punten
            })
    return results

def scrape_mxgp():
    data = {"mxgp": {"title": "MXGP STANDINGS", "riders": []}, "mx2": {"title": "MX2 STANDINGS", "riders": []}, "calendar": []}
    
    # 1. Standings (Algemeen klassement)
    for cat in ["mxgp", "mx2"]:
        try:
            res = requests.get(f"https://mxgpresults.com/{cat}/standings", headers=get_headers())
            soup = BeautifulSoup(res.text, 'html.parser')
            section = soup.find('section', id='standings')
            if section:
                h2 = section.find('h2')
                if h2: data[cat]["title"] = h2.get_text(strip=True).upper()
                
                table = section.find('table')
                if table:
                    rows = table.find_all('tr')[1:]
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
        except Exception as e:
            print(f"Error bij standings {cat}: {e}")

    # 2. Kalender & Live Resultaten per GP
    try:
        res = requests.get("https://mxgpresults.com/mxgp/calendar", headers=get_headers())
        soup = BeautifulSoup(res.text, 'html.parser')
        calendar_table = soup.find('table')
        
        if calendar_table:
            for row in calendar_table.find_all('tr')[1:]:
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
                        # Haal uitslagen op voor beide klassen
                        for c_cat in ["mxgp", "mx2"]:
                            r_url = f"https://mxgpresults.com{url.replace('/mxgp/', f'/{c_cat}/')}"
                            r_res = requests.get(r_url, headers=get_headers())
                            r_soup = BeautifulSoup(r_res.text, 'html.parser')
                            
                            # Zoek de classificatie tabel (jouw HTML snippet toont class 'ses')
                            table = r_soup.find('table', class_='ses')
                            if not table:
                                # Fallback naar id als class niet werkt
                                table_div = r_soup.find('div', id='gpclassification')
                                if table_div: table = table_div.find('table')
                            
                            if table:
                                event[f"{c_cat}_res"] = clean_table(table)
                    
                    data["calendar"].append(event)
    except Exception as e:
        print(f"Error bij calendar: {e}")

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    scrape_mxgp()
