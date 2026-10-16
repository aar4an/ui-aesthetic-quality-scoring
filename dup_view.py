import os, glob
import pandas as pd
from PIL import Image

NEW_DIR = os.path.join("dataset_new", "raw")
OUT = "dup_preview"
os.makedirs(OUT, exist_ok=True)

urls = {}
for m in glob.glob(os.path.join("dataset_new", "manifest*.csv")):
    if "test_old" in m or "old_banners" in m:
        continue
    d = pd.read_csv(m)
    urls.update(dict(zip(d["filename"], d["url"])))

pairs = pd.read_csv("near_duplicates.csv")
for i, r in pairs.iterrows():
    a, b = r["file_a"], r["file_b"]
    ia = Image.open(os.path.join(NEW_DIR, a)).convert("RGB")
    ib = Image.open(os.path.join(NEW_DIR, b)).convert("RGB")
    w = 800
    ia = ia.resize((w, int(ia.height * w / ia.width)))
    ib = ib.resize((w, int(ib.height * w / ib.width)))
    canvas = Image.new("RGB", (w * 2 + 10, max(ia.height, ib.height)), "white")
    canvas.paste(ia, (0, 0))
    canvas.paste(ib, (w + 10, 0))
    p = os.path.join(OUT, f"pair{i+1}_{a[:-4]}__{b[:-4]}.png")
    canvas.save(p)
    print(f"pair{i+1} (dist {r['distance']}): {a} = {urls.get(a)}  |  {b} = {urls.get(b)}")

os.startfile(OUT)