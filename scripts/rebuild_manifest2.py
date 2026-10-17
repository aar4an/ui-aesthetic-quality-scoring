import os, sys
import pandas as pd
from PIL import Image
import numpy as np

prefix = sys.argv[1]
urls_file = sys.argv[2]

urls = pd.read_csv(urls_file)
url_col = "url" if "url" in urls.columns else urls.columns[0]
lab_col = "provisional_label" if "provisional_label" in urls.columns else None

raw = os.path.join("dataset_new", "raw")
rows = []
for i, r in urls.iterrows():
    fn = f"{prefix}_{i+1:04d}.png"
    path = os.path.join(raw, fn)
    label = r[lab_col] if lab_col else ""
    if not os.path.exists(path):
        rows.append((fn, r[url_col], label, "missing"))
        continue
    try:
        g = np.array(Image.open(path).convert("L"))
        status = "blank" if g.std() < 4 else "ok"
    except Exception:
        status = "corrupt"
    rows.append((fn, r[url_col], label, status))

out = os.path.join("dataset_new", f"manifest_{prefix}.csv")
pd.DataFrame(rows, columns=["filename", "url", "provisional_label", "status"]).to_csv(out, index=False)
d = pd.read_csv(out)
print("Saved:", out, "| total:", len(d))
print(d["status"].value_counts())