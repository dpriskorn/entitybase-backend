"""Download and stream Wikidata lexemes JSON dump."""

import requests
import gzip

url = "https://dumps.wikimedia.org/wikidatawiki/entities/latest-lexemes.json.gz"

with requests.get(url, stream=True) as r:
    r.raise_for_status()
    with gzip.GzipFile(fileobj=r.raw) as f:
        # Skip first line
        next(f)
        # Read second line
        second_line = next(f).decode("utf-8", errors="replace").strip()
        print(second_line)
