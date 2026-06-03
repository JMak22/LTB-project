import requests
import re

from pathlib import Path
from html import unescape
from urllib.parse import (
    urljoin,
    urlsplit,
    urlunsplit,
    quote,
    unquote
)

# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_URL = "https://tribunalsontario.ca"
PAGE_URL = f"{BASE_URL}/en/about/open-data/"

OUT_DIR = Path("downloads")
OUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# --------------------------------------------------
# Download page
# --------------------------------------------------

print("Fetching Open Data page...")

html = requests.get(
    PAGE_URL,
    headers=HEADERS
).text

# --------------------------------------------------
# Find all Average Days to First Hearing files
# --------------------------------------------------

matches = re.findall(
    r'href="([^"]*LTBAvgDayFirstHearing[^"]*?xlsx)"',
    html,
    flags=re.IGNORECASE
)

links = []

for match in matches:

    # Convert HTML entities
    match = unescape(match)

    full_url = urljoin(BASE_URL, match)

    # URL-encode spaces and special characters
    parts = urlsplit(full_url)

    clean_url = urlunsplit((
        parts.scheme,
        parts.netloc,
        quote(unquote(parts.path)),
        parts.query,
        parts.fragment
    ))

    links.append(clean_url)

links = sorted(set(links))

print(f"Found {len(links)} files.")

# --------------------------------------------------
# Download files
# --------------------------------------------------

for i, url in enumerate(links, start=1):

    filename = unquote(
        urlsplit(url).path.split("/")[-1]
    )

    output_file = OUT_DIR / filename

    if output_file.exists():
        print(f"[{i}/{len(links)}] Skipping existing: {filename}")
        continue

    print(f"[{i}/{len(links)}] Downloading: {filename}")

    try:
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        output_file.write_bytes(r.content)

    except requests.exceptions.RequestException as e:
        print(f"FAILED: {filename}")
        print(e)
        continue

print("\nDone.")
print(f"Files saved to: {OUT_DIR.resolve()}")