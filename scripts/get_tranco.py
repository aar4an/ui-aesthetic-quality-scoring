import urllib.request, zipfile, io

URL = "https://tranco-list.eu/top-1m.csv.zip"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
data = urllib.request.urlopen(req, timeout=120).read()

with zipfile.ZipFile(io.BytesIO(data)) as z:
    name = z.namelist()[0]
    z.extract(name, ".")
    print("Extracted:", name)

with open("top-1m.csv", encoding="utf-8") as f:
    lines = f.read().splitlines()
print("Total rows:", len(lines))
print("First 5:", lines[:5])
print("Row 50000:", lines[50000])