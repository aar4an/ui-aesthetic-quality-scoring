import os, pandas as pd

R = "dataset_final"
imgs = set(os.listdir(os.path.join(R, "images")))
tot = 0
for s in ("train", "val", "test"):
    df = pd.read_csv(os.path.join(R, f"{s}.csv"))
    missing = [f for f in df.filename if f not in imgs]
    print(s, len(df), "| missing files:", len(missing), "| duplicate names:", df.filename.duplicated().sum())
    tot += len(df)
lab = pd.read_csv(os.path.join(R, "labels.csv"))
print("labels.csv rows:", len(lab), "| images in folder:", len(imgs), "| csv total:", tot)
print("files in folder not in labels.csv:", len(imgs - set(lab.filename)))