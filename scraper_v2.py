import json

def generate_test_data():
    # De data gebaseerd op jouw HTML-input
    argentina_results = [
        {"pos": "1", "num": "1", "name": "ROMAIN FEBVRE", "bike": "KAWASAKI", "pts": "45"},
        {"pos": "2", "num": "16", "name": "TOM VIALLE", "bike": "HONDA", "pts": "42"},
        {"pos": "3", "num": "84", "name": "JEFFREY HERLINGS", "bike": "HONDA", "pts": "37"},
        {"pos": "4", "num": "70", "name": "RUBEN FERNANDEZ", "bike": "HONDA", "pts": "33"},
        {"pos": "5", "num": "41", "name": "PAULS JONASS", "bike": "KAWASAKI", "pts": "32"},
        {"pos": "6", "num": "5", "name": "LUCAS COENEN", "bike": "KTM", "pts": "31"},
        {"pos": "7", "num": "959", "name": "MAXIME RENAUX", "bike": "YAMAHA", "pts": "29"},
        {"pos": "8", "num": "243", "name": "TIM GAJSER", "bike": "YAMAHA", "pts": "29"},
        {"pos": "9", "num": "80", "name": "ANDREA ADAMO", "bike": "KTM", "pts": "28"},
        {"pos": "10", "num": "253", "name": "JAN PANCAR", "bike": "KTM", "pts": "19"}
    ]

    data = {
        "mxgp": {
            "title": "MXGP STANDINGS",
            "riders": argentina_results # Even als test voor de standings
        },
        "mx2": {
            "title": "MX2 STANDINGS",
            "riders": []
        },
        "calendar": [
            {
                "round": "1",
                "gp": "MXGP OF ARGENTINA",
                "loc": "BARILOCHE",
                "date": "01 MAR",
                "mxgp_res": argentina_results,
                "mx2_res": []
            }
        ],
        "argentina_test": argentina_results
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    generate_test_data()
