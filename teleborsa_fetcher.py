import requests
import re
from datetime import datetime
import pandas as pd
import json
import os

def fetcher(ticker: str, filename: str) -> None:

    url = f"https://www.teleborsa.it/fondi/{ticker}/grafico"
    response = requests.get(url)

    if response.status_code == 200:
        page_content = response.text
    else:
        raise Exception(f"Errore nel download della pagina web: {response.status_code}")

    pattern_snippet = r'historical:(\[\[.*\]\])'
    matches = re.findall(pattern_snippet, page_content, re.DOTALL | re.MULTILINE)


    if not matches:
        raise Exception("Non è stato trovato lo snippet di codice con i dati storici")

    entries = json.loads(matches[0])

    data = []
    for entry in entries:
        timestamp = int(entry[0]) / 1000  # Convertire da millisecondi a secondi
        date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
        price = float(entry[1])
        data.append((date, price))

    new_df = pd.DataFrame(data, columns=['Date', 'Price'])

    if os.path.exists(filename):
        existing_df = pd.read_csv(filename)
        combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['Date'], keep='last')
    else:
        combined_df = new_df

    combined_df.to_csv(filename, index=False)
