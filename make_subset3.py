import pandas as pd

SRC = "urls_batch3.csv"
DST = "urls_batch3_sub.csv"
SEED = 21

quota = {
    "curated": 70,
    "ecom": 65,
    "ecom_small": 249,
    "smallbiz": 200,
    "india": 120,
    "global": 80,
    "gov": 20,
}

df = pd.read_csv(SRC)
parts = []
for bucket, n in quota.items():
    sub = df[df["provisional_label"] == bucket]
    parts.append(sub.sample(n=min(n, len(sub)), random_state=SEED))

out = pd.concat(parts).sample(frac=1, random_state=SEED).reset_index(drop=True)
out.to_csv(DST, index=False)
print("Saved:", DST, "| total:", len(out))
print(out["provisional_label"].value_counts())