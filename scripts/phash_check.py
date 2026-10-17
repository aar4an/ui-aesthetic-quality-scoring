import os
import pandas as pd
from PIL import Image
import imagehash

OLD_DIR = os.path.join("dataset", "images")
NEW_DIR = os.path.join("dataset_new", "raw")
LABELS = os.path.join("dataset_new", "labels_raw.csv")
THRESH = 6  # hamming distance <= 6 => near duplicate


def phash(path):
    with Image.open(path) as im:
        return imagehash.phash(im.convert("RGB"))


lab = pd.read_csv(LABELS)
if "label" in lab.columns:
    lab = lab[~lab["label"].astype(str).str.lower().isin(["skip", "skipped", "nan"])]
new_files = [f for f in lab["filename"] if os.path.exists(os.path.join(NEW_DIR, f))]
old_files = [f for f in os.listdir(OLD_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
print("old:", len(old_files), "| new labelled:", len(new_files))

old_h = {f: phash(os.path.join(OLD_DIR, f)) for f in old_files}
new_h = {f: phash(os.path.join(NEW_DIR, f)) for f in new_files}

rows = []
for nf, nh in new_h.items():
    for of, oh in old_h.items():
        d = nh - oh
        if d <= THRESH:
            rows.append((nf, of, "new_vs_old", d))

names = list(new_h)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        d = new_h[names[i]] - new_h[names[j]]
        if d <= THRESH:
            rows.append((names[i], names[j], "new_vs_new", d))

out = pd.DataFrame(rows, columns=["file_a", "file_b", "type", "distance"])
out.to_csv("near_duplicates.csv", index=False)
print("Near-duplicate pairs found:", len(out))
if len(out):
    print(out["type"].value_counts())
    print(out.sort_values("distance").head(15).to_string(index=False))