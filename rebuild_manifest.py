import csv, os
from PIL import Image, ImageStat

RAW = os.path.join("dataset_new", "raw")
URLS = "urls_batch1.csv"
MANIFEST = os.path.join("dataset_new", "manifest.csv")

with open(URLS, newline="", encoding="utf-8") as f:
    urls = [r["url"].strip() for r in csv.DictReader(f)]

rows = []
for fname in sorted(os.listdir(RAW)):
    if not fname.endswith(".png"):
        continue
    idx = int(fname.split("_")[1].split(".")[0])
    url = urls[idx - 1] if 0 < idx <= len(urls) else ""
    path = os.path.join(RAW, fname)
    try:
        with Image.open(path) as im:
            im.load()
            blank = ImageStat.Stat(im.convert("L")).stddev[0] < 4
        status = "blank" if blank else "ok"
    except Exception:
        status = "corrupt"
    rows.append([fname, url, "", status])

with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["filename", "url", "provisional_label", "status"])
    w.writerows(rows)

print("Total files:", len(rows))
for s in ("ok", "blank", "corrupt"):
    print(s, sum(r[3] == s for r in rows))