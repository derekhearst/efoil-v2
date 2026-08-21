"""Scrape live prices for the V2 bill of materials.

Kept in the repo because these numbers go stale and the budget doc should be
reproducible rather than a snapshot of whatever I read once.

Usage:  python model/price_check.py
"""
import re
import ssl
import sys
import urllib.request

ssl._create_default_https_context = ssl._create_unverified_context
HDRS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"}

TARGETS = [
    # --- G10 / FR4, ePlastics ------------------------------------------
    # NO G10. There is none left on the board - module walls and rim ring are
    # printed ASA, floor and mast plate are aluminium. These five lines were
    # watching the price of parts that no longer exist.
    # Real product pages - this script scrapes a URL, it does not search.
    ("6061-T651 1/2in 12x18  (mast plate + handle strips)",
     "https://www.speedymetals.com/p-2411-12-6061-t651-aluminum-plate.aspx"),
    ("Divinycell H80 3/4in quarter 24x48  (mast block)",
     "https://fiberglasssupply.com/quarter-sheet-3-4-h-80-divinycell-plain-sheet/"),
    ("Divinycell H80 1/4in quarter 24x48  (module lid core)",
     "https://fiberglasssupply.com/quarter-sheet-1-4-h-80-divinycell-plain-sheet/"),
    # 5052 sheet and ASA filament are Amazon, which blocks scraping - check
    # those by hand. Derek's 5052 receipt was $61.99 for 2 x 12x24 1/8in.
    ("Divinycell H80 plain sheet 24x48",
     "https://fiberglasssupplydepot.com/product/"
     "divinycell-pvc-foam-core-h-80-5lb-density-plain-sheet.html"),
    # --- powertrain -----------------------------------------------------
    ("Flipsky 65161 motor",
     "https://flipsky.net/products/flipsky-brushless-motor-65161-6000w-"
     "waterproof-underwater-thruster-electric-boat-thruster-for-rov-rc-boat-"
     "jet-boards-outboard-motor-drive-boat-jet"),
    # URL 404s - Flipsky moved the page. Find the new one before trusting this.
    ("Flipsky VX3 Pro remote (URL STALE)",
     "https://flipsky.net/products/waterproof-remote-vx3-pro-controller"),
]

PRICE = re.compile(r"\$\s?([0-9]{1,4}(?:,[0-9]{3})?\.[0-9]{2})")


def prices(html):
    vals = []
    for m in PRICE.findall(html):
        try:
            v = float(m.replace(",", ""))
        except ValueError:
            continue
        if 1.0 <= v <= 5000.0:
            vals.append(v)
    return sorted(set(vals))


def main():
    for label, url in TARGETS:
        try:
            req = urllib.request.Request(url, headers=HDRS)
            html = urllib.request.urlopen(req, timeout=45).read()
            html = html.decode("utf-8", "ignore")
            p = prices(html)
            if not p:
                print(f"{label:38s} | no price found")
                continue
            print(f"{label:38s} | {p[:6]}")
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"{label:38s} | ERR {str(exc)[:60]}")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
