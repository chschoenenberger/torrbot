from bs4 import BeautifulSoup
import requests
import pandas as pd

def search_piratebay(query):
    response = requests.get(f"https://piratebay.party/search/{query}/1/99/200")
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.find_all("tr")

    results = pd.DataFrame(columns=['Name', 'Link', 'Size', 'Seeders'])

    for idx, row in enumerate(rows):
        cols = row.find_all('td')
        if len(cols) > 1:
            results = results.append({
                'Name': cols[1].text.strip(),
                'Link': cols[3].find('a')['href'],
                'Size': cols[4].text,
                'Seeders': cols[5].text
            }, ignore_index=True)

    return results
