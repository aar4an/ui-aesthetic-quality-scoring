import asyncio, csv, os, re, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageStat

# usage: python capture.py urls_batch3.csv b3
URLS_FILE = sys.argv[1] if len(sys.argv) > 1 else "urls.csv"
PREFIX = sys.argv[2] if len(sys.argv) > 2 else "new"
OUT_DIR = os.path.join("dataset_new", "raw")
MANIFEST = os.path.join("dataset_new", "manifest.csv" if PREFIX == "new" else f"manifest_{PREFIX}.csv")
CONCURRENCY = 5
URL_TIMEOUT = 120  # seconds, hard limit per URL
VIEWPORT = {"width": 1900, "height": 968}
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

os.makedirs(OUT_DIR, exist_ok=True)

ACCEPT = re.compile(
    r"^\s*(accept all( cookies)?|accept( cookies)?|allow all( cookies)?|allow cookies|"
    r"i agree|agree|got it|ok|okay|i understand|understood|accept & close|accept and close|"
    r"alle akzeptieren|akzeptieren|alle cookies akzeptieren|zustimmen|einverstanden|"
    r"tout accepter|accepter|j'accepte|accepter et fermer|"
    r"aceptar todo|aceptar todas|aceptar|aceitar tudo|aceitar|"
    r"accetta tutti|accetta|accetto|"
    r"alles accepteren|accepteren|akkoord)\s*$", re.I)

HIDE_CSS = """
#onetrust-consent-sdk, #onetrust-banner-sdk, .onetrust-pc-dark-filter,
#CybotCookiebotDialog, #CybotCookiebotDialogBodyUnderlay, #cookiebanner,
.cc-window, .cc-banner, .cookie-banner, #cookie-banner, .cookie-consent,
#cookie-consent, .cookie-notice, #cookie-notice, #cookie-law-info-bar,
[class*="cookie-banner" i], [id*="cookie-banner" i], [class*="cookiebanner" i],
[class*="cookie-consent" i], [id*="cookie-consent" i], [class*="consent-banner" i],
[id*="consent-banner" i], [class*="cookie-modal" i], [class*="cookie-popup" i],
#usercentrics-root, #didomi-host, .didomi-popup-open, #truste-consent-track,
.truste_overlay, .fc-consent-root, #qc-cmp2-container, [id^="sp_message_container"],
.cmp-container, #cmpbox, #cmpbox2, .cmpboxBG, .osano-cm-window, #iubenda-cs-banner,
.cky-consent-container, .cli-modal-backdrop, #gdpr-cookie-notice, .gdpr-banner
{ display: none !important; visibility: hidden !important; }
html, body { overflow: auto !important; position: static !important; }
"""

STOP = set("the and to of in is for on with that this you your are we our be as at from or by an it will can all more not have has about us".split())


def is_blank(path):
    with Image.open(path) as im:
        return ImageStat.Stat(im.convert("L")).stddev[0] < 4


async def is_english(page):
    try:
        info = await page.evaluate("""() => {
            const lang = (document.documentElement.lang || '').toLowerCase();
            const txt = (document.body ? document.body.innerText : '').slice(0, 3000);
            return {lang: lang, txt: txt};
        }""")
    except Exception:
        return True
    lang, txt = info["lang"], info["txt"]
    letters = [c for c in txt if c.isalpha()]
    if len(letters) > 30:
        nonlatin = sum(1 for c in letters if ord(c) > 0x024F)
        if nonlatin / len(letters) > 0.25:
            return False
    words = re.findall(r"[a-z]+", txt.lower())
    if len(words) > 40:
        ratio = sum(w in STOP for w in words) / len(words)
        if ratio > 0.12:
            return True
    if lang and not lang.startswith("en"):
        return False
    return True


async def dismiss_banners(page):
    for frame in page.frames:
        try:
            loc = frame.locator(
                "button, a, [role='button'], input[type='button'], input[type='submit']"
            ).filter(has_text=ACCEPT)
            n = await loc.count()
            for i in range(min(n, 5)):
                el = loc.nth(i)
                if await el.is_visible():
                    await el.click(timeout=1500)
                    await page.wait_for_timeout(800)
                    return
        except Exception:
            continue


async def try_once(browser, url, path, wait_ms):
    ctx = await browser.new_context(
        viewport=VIEWPORT, ignore_https_errors=True, locale="en-US", user_agent=UA)
    page = await ctx.new_page()
    english = True
    try:
        try:
            await page.goto(url, wait_until="load", timeout=30000)
        except Exception:
            pass
        await page.wait_for_timeout(wait_ms)
        english = await is_english(page)
        if english:
            try:
                await dismiss_banners(page)
            except Exception:
                pass
            try:
                await page.add_style_tag(content=HIDE_CSS)
            except Exception:
                pass
            await page.wait_for_timeout(1000)
            await page.screenshot(path=path, full_page=False, timeout=20000)
    finally:
        try:
            await asyncio.wait_for(ctx.close(), timeout=10)
        except Exception:
            pass
    return english


async def work(browser, url, path):
    english = await try_once(browser, url, path, 3000)
    if not english:
        return "non_english"
    if is_blank(path):
        english = await try_once(browser, url, path, 8000)
        if not english:
            return "non_english"
        if is_blank(path):
            return "blank"
    return "ok"


def write_manifest(rows):
    snap = sorted(rows)
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["filename", "url", "provisional_label", "status"])
        w.writerows(snap)


async def shoot(sem, browser, idx, url, label, rows):
    fname = f"{PREFIX}_{idx:04d}.png"
    path = os.path.join(OUT_DIR, fname)
    async with sem:
        try:
            status = await asyncio.wait_for(work(browser, url, path), timeout=URL_TIMEOUT)
        except asyncio.TimeoutError:
            status = "timeout"
        except Exception as e:
            status = "fail: " + str(e)[:60]
    rows.append([fname, url, label, status])
    print(idx, status, url, flush=True)
    if len(rows) % 20 == 0:
        write_manifest(rows)


async def main():
    with open(URLS_FILE, newline="", encoding="utf-8") as f:
        items = [(r["url"].strip(), r.get("provisional_label", "").strip()) for r in csv.DictReader(f)]
    rows = []
    sem = asyncio.Semaphore(CONCURRENCY)
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                args=["--disable-blink-features=AutomationControlled"])
            try:
                await asyncio.gather(*[
                    shoot(sem, browser, i + 1, u if u.startswith("http") else "https://" + u, l, rows)
                    for i, (u, l) in enumerate(items)
                ])
            finally:
                write_manifest(rows)
                try:
                    await asyncio.wait_for(browser.close(), timeout=20)
                except Exception:
                    pass
    finally:
        write_manifest(rows)
    print("Done. ok:", sum(r[3] == "ok" for r in rows), "of", len(rows), flush=True)
    os._exit(0)


asyncio.run(main())