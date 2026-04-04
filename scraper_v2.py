import requests
from bs4 import BeautifulSoup
import json
import time

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

def clean_table(table):
    """Haalt data uit de cellen zonder dat tekst van andere kolommen 'lekt'"""
    results = []
    if not table: return []
    
    # Zoek rijen in de tbody of gewoon alle tr's
    rows = table.find_all('tr')
    
    for row in rows:
        cols = row.find_all('td', recursive=False)
        # We negeren de header (die heeft <th> of geen data)
        if len(cols) >= 5:
            pos = cols[0].get_text(strip=True)
            # Soms is de eerste rij de header die we moeten overslaan
            if not pos.isdigit(): continue 
                
            num = cols[1].get_text(strip=True).replace('#', '')
            # Pak de naam: zoek eerst een link, anders de tekst van de cel
            name_cell = cols[2]
            name = name_cell.find('a').get_text(strip=True) if name_cell.find('a') else name_cell.get_text(strip=True)
            bike = cols[3].get_text(strip=True)
            pts = cols[-1].get_text(strip=True)
            
            results.append({
                "pos": pos,
                "num": num,
                "name": name.upper(),
                "bike": bike.upper(),
                "pts": pts
            })
    return results

def scrape_mxgp():
    data = {"mxgp": {"title": "MXGP STANDINGS 2026", "riders": []}, "mx2": {"title": "MX2 STANDINGS 2026", "riders": []}, "calendar": []}
    
    # 1. Standings parsen
    for cat in ["mxgp", "mx2"]:
        try:
            res = requests.get(f"https://mxgpresults.com/{cat}/standings", headers=get_headers(), timeout=10)
            soup = BeautifulSoup(res.text, 'lxml')
            # Zoek de tabel in de standings sectie
            container = soup.find('section', id='standings') or soup
            table = container.find('table')
            if table:
                data[cat]["riders"] = clean_table(table)
                print(f"Gevonden: {len(data[cat]['riders'])} riders voor {cat}")
        except Exception as e:
            print(f"Error bij standings {cat}: {e}")

    # 2. Kalender parsen
    try:
        res = requests.get("https://mxgpresults.com/mxgp/calendar", headers=get_headers(), timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        main_table = soup.find('table')
        if main_table:
            rows = main_table.find_all('tr')[1:] # Sla header over
            for row in rows:
                cols = row.find_all('td', recursive=False)
                if len(cols) >= 3:
                    link_tag = cols[1].find('a')
                    event = {
                        "round": cols[0].get_text(strip=True),
                        "gp": cols[1].find('span', itemprop="name").get_text(strip=True).upper() if cols[1].find('span') else cols[1].get_text(strip=True).upper(),
                        "loc": cols[1].find('small').get_text(strip=True) if cols[1].find('small') else "",
                        "date": cols[2].get_text(strip=True),
                        "mxgp_res": [], "mx2_res": []
                    }
                    
                    # Alleen resultaten ophalen als er een link is naar de race
                    if link_tag and 'href' in link_tag.attrs:
                        base_url = link_tag['href']
                        for c_cat in ["mxgp", "mx2"]:
                            try:
                                r_url = f"https://mxgpresults.com{base_url.replace('/mxgp/', f'/{c_cat}/')}"
                                r_res = requests.get(r_url, headers=get_headers(), timeout=10)
                                r_soup = BeautifulSoup(r_res.text, 'lxml')
                                # Zoek tabel: probeer class 'ses', anders id 'gpclassification', anders de eerste tabel
                                r_table = r_soup.find('table', class_='ses') or \
                                          (r_soup.find('div', id='gpclassification').find('table') if r_soup.find('div', id='gpclassification') else None) or \
                                          r_soup.find('table')
                                
                                if r_table:
                                    event[f"{c_cat}_res"] = clean_table(r_table)
                            except:
                                pass
                    data["calendar"].append(event)
    except Exception as e:
        print(f"Error bij calendar: {e}")

    # Veiligheid: Alleen opslaan als we minstens iets hebben gevonden
    if len(data["mxgp"]["riders"]) > 0 or len(data["calendar"]) > 0:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print("Data succesvol opgeslagen in data.json")
    else:
        print("WAARSCHUWING: Geen data gevonden. data.json is NIET overschreven.")

if __name__ == "__main__":
    scrape_mxgp()
