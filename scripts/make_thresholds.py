# Feedback thresholds ko dataset ke TRAIN split ke percentiles se banata hai (p15 = low, p85 = high)
# edge_density aur whitespace_ratio ko percent (0-100) me convert karta hai
# Output: feedback_thresholds.json (app aur notebook 07 dono isi ko padhenge)
import json
import numpy as np
import pandas as pd

DS = r"C:\Projects\Internship_Learning\dataset_final"
OUT = r"C:\Projects\Internship_Learning\feedback_thresholds.json"

# features_all.csv (22 features) aur train.csv load karta hai
feat = pd.read_csv(DS + r"\features_all.csv")
train = pd.read_csv(DS + r"\train.csv")[["filename"]]

# Sirf train images pe thresholds banata hai (val/test ko haath nahi lagata)
d = feat.merge(train, on="filename")
print("Train rows:", len(d))

# Fraction wale columns ko percent me convert karta hai
d["edge_density"] = d["edge_density"] * 100
d["whitespace_ratio"] = d["whitespace_ratio"] * 100

# Jin features pe feedback rules banenge
cols = ["brightness", "contrast", "edge_density", "whitespace_ratio", "saturation_mean",
        "lr_balance", "tb_balance", "text_like_regions", "layout_clutter_score"]

thresholds = {}
print("\nfeature               p15      p50      p85      min      max")
for c in cols:
    p15, p50, p85 = np.percentile(d[c], [15, 50, 85])
    thresholds[c] = {"p15": round(float(p15), 4), "p85": round(float(p85), 4)}
    print(f"{c:20s} {p15:8.3f} {p50:8.3f} {p85:8.3f} {d[c].min():8.3f} {d[c].max():8.3f}")

# Class-wise mean (sirf dekhne ke liye, taaki pata chale kaunsa feature class se related hai)
print("\nClass-wise mean (train):")
print(d.groupby("label")[cols].mean().round(2).T.to_string())

# JSON me save karta hai
with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"source": "train split percentiles (p15/p85), edge_density and whitespace_ratio in percent",
               "thresholds": thresholds}, f, indent=2)
print("\nSaved:", OUT)