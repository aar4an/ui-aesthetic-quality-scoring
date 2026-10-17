import os, shutil
import pandas as pd
from sklearn.model_selection import train_test_split

OLD_DIR = os.path.join("dataset", "images")
OLD_LABELS = os.path.join("dataset", "labels.csv")
NEW_DIR = os.path.join("dataset_new", "raw")
NEW_LABELS = os.path.join("dataset_new", "labels_raw.csv")
OUT = "dataset_final"
OUT_IMG = os.path.join(OUT, "images")
SEED = 42

# near-duplicates found by phash_check.py (same page): keep first, drop these
EXCLUDE = {"b3_0460.png", "b3_0644.png", "b3_0753.png", "b3_0488.png"}

if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT_IMG, exist_ok=True)

# old 200: rename to old_NNNN.png (sorted), keep original name
old = pd.read_csv(OLD_LABELS)
old["label"] = old["label"].str.strip().str.lower()
old = old.sort_values("filename").reset_index(drop=True)
rows = []
for i, r in old.iterrows():
    src = os.path.join(OLD_DIR, r["filename"])
    if not os.path.exists(src):
        print("MISSING old file:", r["filename"]); continue
    new_name = f"old_{i+1:04d}.png"
    shutil.copy2(src, os.path.join(OUT_IMG, new_name))
    rows.append((new_name, r["label"], "", "old", r["filename"]))

# new labelled (drop skips, keep last entry if a file was relabelled)
new = pd.read_csv(NEW_LABELS)
new["label"] = new["label"].astype(str).str.strip().str.lower()
new = new.drop_duplicates("filename", keep="last")
new = new[new["label"].isin(["good", "average", "poor"])]

dropped = new[new["filename"].isin(EXCLUDE)]
print("Excluded near-duplicates:", dropped[["filename", "score", "label"]].to_dict("records"))
new = new[~new["filename"].isin(EXCLUDE)]

for _, r in new.iterrows():
    src = os.path.join(NEW_DIR, r["filename"])
    if not os.path.exists(src):
        print("MISSING new file:", r["filename"]); continue
    shutil.copy2(src, os.path.join(OUT_IMG, r["filename"]))
    src_tag = r["filename"].split("_")[0]
    src_tag = "b1" if src_tag == "new" else src_tag
    score = "" if pd.isna(r["score"]) else int(r["score"])
    rows.append((r["filename"], r["label"], score, src_tag, r["filename"]))

df = pd.DataFrame(rows, columns=["filename", "label", "score", "source", "orig_filename"])
df.to_csv(os.path.join(OUT, "labels.csv"), index=False)

# stratified 70/15/15
train, temp = train_test_split(df, test_size=0.30, stratify=df["label"], random_state=SEED)
val, test = train_test_split(temp, test_size=0.50, stratify=temp["label"], random_state=SEED)
for name, part in [("train", train), ("val", val), ("test", test)]:
    part.sort_values("filename").to_csv(os.path.join(OUT, f"{name}.csv"), index=False)

# leakage check
s_tr, s_va, s_te = set(train.filename), set(val.filename), set(test.filename)
assert not (s_tr & s_va) and not (s_tr & s_te) and not (s_va & s_te), "LEAKAGE!"
assert len(s_tr) + len(s_va) + len(s_te) == len(df), "count mismatch"
assert df["filename"].is_unique, "duplicate filenames"

print("TOTAL:", len(df))
print(df["label"].value_counts().to_dict())
print(df["source"].value_counts().to_dict())
for name, part in [("train", train), ("val", val), ("test", test)]:
    print(name, len(part), part["label"].value_counts().to_dict())
print("Leakage check: OK")