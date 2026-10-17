import csv, random

random.seed(42)

# domains of the first 50 manually collected sites (exclude to avoid repeats)
old = """stripe notion linear apple figma bbc glossier bluetokai stanzaliving mercuryai
jimmychoo mea.gov.in serotoninn foxtale untld w3schools ndtv reverb vyome unidays
indianexpress amazon flipkart naukri makemytrip zomato paytm irctc myntra indiamart
justdial bookmyshow commonfloor shaadi cardekho cbse pib.gov.in mygov epfo
indianrailways delhidistrictcourts dda upbocw nvsp edistrict ugc nprocure lingscar
craigslist naaptol wikipedia""".split()

# infrastructure / non-website domains to skip
skip_words = ["cdn", "gstatic", "akamai", "amazonaws", "googleapis", "cloudfront",
              "doubleclick", "googlesyndication", "googleusercontent", "azure",
              "microsoftonline", "root-servers", "apple-dns", "ytimg", "fbcdn",
              "analytics", "tracking", "adservice", "adsystem", "pixel", "api.",
              "static", "edgekey", "edgesuite", "cloudflare", "windows.net"]
skip_words += ["porn", "xxx", "sex", "adult", "nude", "nsfw", "hentai", "escort",
               "erotic", "fuck", "milf", "fap", "xvideos", "xnxx", "onlyfans",
               "camgirl", ".xxx", ".porn", ".sex", ".adult", "casino", "betting",
               "poker", "torrent", "dramula", "motion"]
rows = []
with open("top-1m.csv", encoding="utf-8") as f:
    for line in f:
        rank, dom = line.strip().split(",", 1)
        rows.append((int(rank), dom))

def ok(dom):
    d = dom.lower()
    if any(w in d for w in skip_words):
        return False
    if any(o in d for o in old):
        return False
    return True

pool = [(r, d) for r, d in rows if ok(d)]

bands = [(1000, 10000, 200), (10000, 100000, 350),
         (100000, 500000, 300), (500000, 1000000, 200)]

picked = []
for lo, hi, n in bands:
    cand = [x for x in pool if lo <= x[0] < hi]
    picked += random.sample(cand, n)

# extra Indian sites (.in / .co.in) across all ranks
indian = [x for x in pool if x[1].endswith(".in") and x not in picked]
picked += random.sample(indian, 250)

random.shuffle(picked)

with open("urls.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["url", "provisional_label", "rank"])
    for r, d in picked:
        w.writerow([f"https://{d}", "", r])

print("Wrote", len(picked), "URLs to urls.csv")