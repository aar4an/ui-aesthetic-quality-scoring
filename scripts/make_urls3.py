import csv, random

random.seed(11)

def doms_from(path, limit=None):
    with open(path, encoding="utf-8") as f:
        rows = [r["url"].replace("https://", "").strip() for r in csv.DictReader(f)]
    return set(rows[:limit] if limit else rows)

# exclude everything already captured: batch1 first 351, all of batch2
used = doms_from("urls_batch1.csv", 351) | doms_from("urls_batch2.csv")

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
    "gacor", "bokep", "lottery", "crack", "warez", "movie", "film", "stream", "tube",
    "vpn", "proxy", "download", "mirror", "cloud", "server", "host", "dns", "mail",
    "login", "admin", "cpanel", "webmail", "tracker", "sync", "gateway"]

INDIA = (".in", ".co.in", ".org.in", ".ac.in", ".edu.in")
GOV = (".gov.in", ".nic.in", ".ac.in", ".edu.in", ".res.in")
GLOBAL = (".com", ".org", ".net", ".io", ".co", ".ai", ".app", ".edu", ".us")

def ok(dom):
    d = dom.lower()
    if dom in used:
        return False
    if any(w in d for w in skip_words) or any(o in d for o in old):
        return False
    dots = d.count(".")
    if dots > 3 or (dots == 3 and not d.endswith((".co.in", ".org.in", ".ac.in", ".edu.in", ".gov.in"))):
        return False
    return True

rows = []
with open("top-1m.csv", encoding="utf-8") as f:
    for line in f:
        rank, dom = line.strip().split(",", 1)
        rows.append((int(rank), dom))
pool = [(r, d) for r, d in rows if ok(d)]

glob_hi = [x for x in pool if x[1].endswith(GLOBAL) and 3000 <= x[0] <= 150000]
india = [x for x in pool if x[1].endswith(INDIA) and not x[1].endswith(GOV) and x[0] <= 500000]
smallbiz = [x for x in pool if x[1].endswith((".com", ".in", ".co", ".org", ".co.in"))
            and not x[1].endswith(GOV) and 150000 < x[0] <= 800000]
gov = [x for x in pool if x[1].endswith(GOV)]

EKW = ("shop", "store", "fashion", "wear", "cloth", "apparel", "boutique", "jewel",
       "mart", "bazaar", "outlet", "threads", "garment", "saree", "kurti", "sneaker", "handloom")
ecom_small = [x for x in pool if any(k in x[1].lower() for k in EKW)
              and x[1].endswith((".com", ".in", ".co", ".co.in", ".store", ".shop"))
              and 20000 < x[0] <= 700000]

curated = """pitch.com craft.do raycast.com superhuman.com cal.com supabase.com planetscale.com
clerk.com resend.com aesop.com everlane.com rhodesskin.com summerfridays.com byredo.com
loewe.com acnestudios.com nothing.tech fairphone.com oura.com whoop.com peloton.com
readymag.com cargo.site are.na pentagram.com ideo.com wolffolins.com collinsnyc.com
metalab.com instrument.com hugeinc.com basicagency.com locomotive.ca activetheory.net
sleepyowl.co thesleepcompany.in rarerabbit.in bewakoof.com snitch.co.in thesouledstore.com
wakefit.co urbanladder.com pepperfry.com plumgoodness.com beminimalist.co mcaffeine.com
vahdam.com sugarfit.com jupiter.money fi.money slice.com niyo.co smallcase.com
kuvera.in coinswitch.co coindcx.com wazirx.com freecharge.in mobikwik.com bharatpe.com
curefit.com cult.fit healthifyme.com noise.com fireboltt.com gonoise.com bluestone.com
caratlane.com giva.co melorra.com""".split()
curated = [c for c in dict.fromkeys(curated) if c not in used and not any(o in c for o in old)]

ecom_brands = """westside.com pantaloons.com libas.in biba.in wforwoman.com manyavar.com
peterengland.com allensolly.com louisphilippe.com vanheusenindia.com shoppersstop.com
lifestylestores.com maxfashion.in zivame.com clovia.com limeroad.com snapdeal.com
jiomart.com croma.com vijaysales.com reliancedigital.in shopclues.com voonik.com
hm.com zara.com uniqlo.com gap.com levi.com nike.com adidas.com puma.com
urbanoutfitters.com asos.com forever21.com gymshark.com fashionnova.com
prettylittlething.com boohoo.com nastygal.com ssense.com farfetch.com nordstrom.com
macys.com target.com walmart.com bestbuy.com ebay.com etsy.com wayfair.com ikea.com
homedepot.com lowes.com sephora.com ulta.com chewy.com zappos.com revolve.com
anthropologie.com freepeople.com jcrew.com bananarepublic.com oldnavy.com
abercrombie.com aritzia.com lululemon.com""".split()
ecom_brands = [c for c in dict.fromkeys(ecom_brands) if c not in used and not any(o in c for o in old)]

def take(lst, n, bucket):
    n = min(n, len(lst))
    return [(r, d, bucket) for r, d in random.sample(lst, n)]

final = [(0, c, "curated") for c in curated]
final += take(glob_hi, 450, "global")
final += take(india, 420, "india")
final += take(smallbiz, 380, "smallbiz")
final += take(gov, 100, "gov")
final += [(0, c, "ecom") for c in ecom_brands]
final += take(ecom_small, 250, "ecom_small")
random.shuffle(final)

seen, out = set(), []
for r, d, b in final:
    if d not in seen:
        seen.add(d)
        out.append((r, d, b))

with open("urls_batch3.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["url", "provisional_label", "rank"])
    for r, d, b in out:
        w.writerow([f"https://{d}", b, r])

counts = {}
for r, d, b in out:
    counts[b] = counts.get(b, 0) + 1
print(counts)
print("Wrote", len(out), "URLs to urls_batch3.csv")