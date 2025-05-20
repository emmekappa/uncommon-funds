import re
import json
import sys
import requests
import pandas as pd
import os
from datetime import datetime


# Sostituisce solo .numero con 0.numero, -.-numero con -0.numero, +.numero con +0.numero
def fix_dot_numbers(s):
    s = re.sub(r'(?<=\[|,)\s*\.(\d+)', r' 0.\1', s)
    s = re.sub(r'([+-])\.(\d+)', r'\g<1>0.\2', s)
    return s


def fetcher(url: str, filename: str) -> None:
    sys.stdout.write(f"Fetching data from {url} and saving to {filename} (.csv, json)... ")
    if not url.endswith("/grafico"):
        raise Exception("The url must end with /grafico")
    response = requests.get(url)

    if response.status_code == 200:
        page_content = response.text
    else:
        raise Exception(f"Error while fetching URL: {response.status_code}")

    pattern_snippet = r'historical:(\[\[.*\]\])'
    matches = re.findall(pattern_snippet, page_content, re.DOTALL | re.MULTILINE)

    if not matches:
        raise Exception("Cannot find historical data in the page")

    entries = json.loads(fix_dot_numbers(matches[0]))

    data = []
    for entry in entries:
        timestamp = int(entry[0]) / 1000
        date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
        price = float(entry[1])
        data.append((date, price))

    new_df = pd.DataFrame(data, columns=['Date', 'Price'])

    csv_filename = f"{filename}.csv"
    if os.path.exists(csv_filename):
        existing_df = pd.read_csv(csv_filename)
        combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['Date'], keep='last')
    else:
        combined_df = new_df

    combined_df.to_csv(csv_filename, index=False)

    combined_df.to_json(f"{filename}.json", orient='records', indent=2)
    sys.stdout.write("Done.\n")
