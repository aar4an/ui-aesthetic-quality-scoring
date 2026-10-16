import os, csv
import streamlit as st
import streamlit.components.v1 as components

RAW = os.path.join("dataset_new", "raw")
MANIFEST = os.path.join("dataset_new", "manifest.csv")
LABELS = os.path.join("dataset_new", "labels_raw.csv")

st.set_page_config(layout="wide", page_title="Label tool")

def load_labels():
    d = {}
    if os.path.exists(LABELS):
        with open(LABELS, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                d[r["filename"]] = r
    return d

def save_labels(d):
    with open(LABELS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["filename", "score", "label"])
        w.writeheader()
        for r in d.values():
            w.writerow(r)

def to_class(s):
    return "poor" if s <= 3 else ("average" if s <= 6 else "good")

# files to label
import glob
urls = {}
files = []
manifests = sorted(m for m in glob.glob(os.path.join("dataset_new", "manifest*.csv"))
                   if "test_old" not in m)
for m in manifests:
    with open(m, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            urls[r["filename"]] = r["url"]
            if r["status"] == "ok":
                files.append(r["filename"])
if not manifests:
    files = sorted(x for x in os.listdir(RAW) if x.endswith(".png"))

labels = load_labels()
todo = [f for f in files if f not in labels]

def set_label(fname, score):
    labels[fname] = {"filename": fname,
                     "score": "" if score is None else score,
                     "label": "skip" if score is None else to_class(score)}
    save_labels(labels)
    st.rerun()

done_scored = [r for r in labels.values() if r["label"] != "skip"]
c = {k: sum(r["label"] == k for r in labels.values()) for k in ("good", "average", "poor", "skip")}
st.markdown(f"**Done:** {len(labels)} / {len(files)}  |  Good {c['good']}  Average {c['average']}  Poor {c['poor']}  Skipped {c['skip']}")

if not todo:
    st.success("All images labelled!")
    st.stop()

cur = todo[0]
st.caption(f"{cur}   {urls.get(cur, '')}")
st.image(os.path.join(RAW, cur), use_container_width=True)

st.caption("Score 1-3 = Poor, 4-6 = Average, 7-9 = Good. Keys: 1-9 score, s = skip (NSFW/blank/irrelevant), u = undo")
cols = st.columns(11)
for i in range(1, 10):
    if cols[i - 1].button(str(i), key=f"b{i}", use_container_width=True):
        set_label(cur, i)
if cols[9].button("Skip", key="skip", use_container_width=True):
    set_label(cur, None)
if cols[10].button("Undo", key="undo", use_container_width=True):
    if labels:
        labels.popitem()
        save_labels(labels)
        st.rerun()

components.html("""
<script>
const P = window.parent;
if (!P._lblKeys) {
  P._lblKeys = true;
  P.document.addEventListener('keydown', function(e) {
    const k = e.key.toLowerCase();
    let want = null;
    if (k >= '1' && k <= '9') want = k;
    else if (k === 's') want = 'Skip';
    else if (k === 'u') want = 'Undo';
    if (!want) return;
    const b = Array.from(P.document.querySelectorAll('button'))
                   .find(x => x.innerText.trim() === want);
    if (b) b.click();
  });
}
</script>
""", height=0)