import csv, random

random.seed(7)

# already captured in batch 1 (first 351 rows) + old 50 manual sites -> exclude
with open("urls_batch1.csv", encoding="utf-8") as f:
    b1 = [r["url"].replace("https://", "").strip() for r in csv.DictReader(f)][:351]
used = set(b1)

old = """stripe notion linear apple figma bbc glossier bluetokai stanzaliving mercuryai
jimmychoo mea.gov.in serotoninn foxtale untld w3schools ndtv reverb vyome unidays
indianexpress amazon flipkart naukri makemytrip zomato paytm irctc myntra indiamart
justdial bookmyshow commonfloor shaadi cardekho cbse pib.gov.in mygov epfo
indianrailways delhidistrictcourts dda upbocw nvsp edistrict ugc nprocure lingscar
craigslist naaptol wikipedia""".split()

skip_words = ["cdn", "gstatic", "akamai", "amazonaws", "googleapis", "cloudfront",
    "doubleclick", "googlesyndication", "googleusercontent", "azure", "microsoftonline",
    "root-servers", "apple-dns", "ytimg", "fbcdn", "analytics", "tracking", "adservice",
    "adsystem", "pixel", "api.", "static", "edgekey", "edgesuite", "cloudflare",
    "windows.net", "msedge", "porn", "xxx", "sex", "adult", "nude", "nsfw", "hentai",
    "escort", "erotic", "fuck", "milf", "fap", "xvideos", "xnxx", "onlyfans", "camgirl",
    "casino", "bet", "poker", "torrent", "dramula", "motion", "slot", "togel", "judi",
    "gacor", "bokep", "lottery", "crack", "warez", "movie", "film", "stream"]

INDIA = (".in", ".co.in", ".org.in", ".ac.in", ".edu.in")
GLOBAL = (".com", ".org", ".net", ".io", ".co", ".ai", ".app", ".edu", ".us")

def ok(dom):
    d = dom.lower()
    if dom in used:
        return False
    if any(w in d for w in skip_words) or any(o in d for o in old):
        return False
    dots = d.count(".")
    if dots > 3 or (dots == 3 and not d.endswith((".co.in", ".org.in", ".ac.in", ".edu.in"))):
        return False
    return True

rows = []
with open("top-1m.csv", encoding="utf-8") as f:
    for line in f:
        rank, dom = line.strip().split(",", 1)
        rows.append((int(rank), dom))

pool = [(r, d) for r, d in rows if ok(d)]
india = [x for x in pool if x[1].endswith(INDIA)]
glob = [x for x in pool if x[1].endswith(GLOBAL) and not x[1].endswith(INDIA) and 3000 <= x[0] <= 600000]

# curated candidates (many likely Good, some Average) - you still label by what you SEE
curated = """vercel.com framer.com webflow.com shopify.com airbnb.com spotify.com slack.com
asana.com monday.com mailchimp.com canva.com dropbox.com intercom.com loom.com miro.com
airtable.com calendly.com zapier.com hubspot.com squarespace.com wix.com medium.com
duolingo.com headspace.com calm.com patagonia.com allbirds.com warbyparker.com away.com
tesla.com polestar.com rivian.com sonos.com bang-olufsen.com framework.dev mailchimp.com
zerodha.com razorpay.com cred.club swiggy.com groww.in phonepe.com nykaa.com lenskart.com
boat-lifestyle.com mamaearth.in sugarcosmetics.com fabindia.com tanishq.co.in titan.co.in
tata.com tatamotors.com mahindra.com jio.com airtel.in hdfcbank.com icicibank.com
kotak.com upgrad.com byjus.com unacademy.com cleartrip.com olacabs.com urbancompany.com
meesho.com ajio.com tatacliq.com bigbasket.com blinkit.com pharmeasy.in 1mg.com practo.com
policybazaar.com paisabazaar.com acko.com godigit.com zoho.com freshworks.com postman.com
browserstack.com chargebee.com""".split()
curated = [c for c in dict.fromkeys(curated) if c not in used and not any(o in c for o in old)]

n_india = min(260, len(india))
n_glob = min(340, len(glob))
pick_india = random.sample(india, n_india)
pick_glob = random.sample(glob, n_glob)

doms = [(0, c) for c in curated] + pick_india + pick_glob
random.shuffle(doms)

seen, final = set(), []
for r, d in doms:
    if d not in seen:
        seen.add(d)
        final.append((r, d))

with open("urls_batch2.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["url", "provisional_label", "rank"])
    for r, d in final:
        w.writerow([f"https://{d}", "", r])

print("Curated:", len(curated), "| India:", n_india, "| Global English TLD:", n_glob)
print("Wrote", len(final), "URLs to urls_batch2.csv")