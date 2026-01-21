#!/usr/bin/env python3
# <xbar.title>METAR Wind + TAF</xbar.title>
# <xbar.version>v2.3</xbar.version>
# <xbar.author>You</xbar.author>
# <xbar.desc>METAR-style wind + flight category with raw METAR/TAF</xbar.desc>
# <xbar.dependencies>python3</xbar.dependencies>

import json
import urllib.request
import sys

# ===== CONFIG =====
AIRPORT = "KDPA"   # ICAO code
TIMEOUT = 10
# ==================

METAR_URL = "https://aviationweather.gov/api/data/metar?ids={airport}&format=json&hours=1"
TAF_URL   = "https://aviationweather.gov/api/data/taf?ids={airport}&format=json"

def fetch_json(url):
    """Fetch JSON with a proper User-Agent header."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "xbar-metar-plugin/1.0 (contact: you@example.com)"
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        data = r.read().decode().strip()
        if not data:
            raise ValueError("Empty response from server")
        return json.loads(data)

def parse_visibility(vis):
    """Convert visibility string to float (handles '10+' and fractions)."""
    if vis is None:
        return 10.0
    if isinstance(vis, (int, float)):
        return float(vis)
    v = str(vis).strip()
    if v.endswith("+"):
        v = v[:-1]
    if "/" in v:
        try:
            n, d = v.split("/")
            return float(n) / float(d)
        except:
            return 1.0
    try:
        return float(v)
    except:
        return 10.0

def parse_ceiling(clouds):
    """Determine ceiling from sky_conditions."""
    ceilings = [
        c["base"] * 100
        for c in clouds
        if c.get("cover") in ("BKN", "OVC") and c.get("base")
    ]
    return min(ceilings) if ceilings else 99999

def flight_category(vis, ceiling):
    if ceiling <= 500 or vis <= 1:
        return "LIFR"
    if ceiling <= 1000 or vis < 3:
        return "IFR"
    if ceiling <= 3000 or vis < 5:
        return "MVFR"
    return "VFR"

def category_color(cat):
    return {
        "LIFR": "magenta",
        "IFR": "red",
        "MVFR": "blue",
        "VFR": "green",
    }.get(cat, "black")

def format_wind(m):
    """Format wind like METAR: 22012KT or VRB04KT"""
    wdir = m.get("wdir")
    wspd = m.get("wspd")
    gust = m.get("wgst")

    if not wspd:
        return "00000KT"

    if wdir is None:
        d = "VRB"
    else:
        try:
            d = f"{int(float(wdir)):03d}"
        except:
            d = "VRB"

    s = f"{int(float(wspd)):02d}"

    if gust:
        g = f"G{int(float(gust)):02d}"
    else:
        g = ""

    return f"{d}{s}{g}KT"

def main():
    try:
        metar_json = fetch_json(METAR_URL.format(airport=AIRPORT))
        taf_json   = fetch_json(TAF_URL.format(airport=AIRPORT))
    except Exception as e:
        print("METAR ⚠️ | color=red")
        print("---")
        print(str(e))
        sys.exit(0)

    # Extract METAR
    if isinstance(metar_json, list):
        metar_list = metar_json
    elif isinstance(metar_json, dict):
        metar_list = metar_json.get("METAR", []) or metar_json.get("data", {}).get("METAR", [])
    else:
        metar_list = []

    if not metar_list:
        print("No METAR | color=red")
        sys.exit(0)


    m = metar_list[0]

    # Extract TAF
    if isinstance(taf_json, list):
        taf_list = taf_json
    elif isinstance(taf_json, dict):
        taf_list = taf_json.get("TAF", []) or taf_json.get("data", {}).get("TAF", [])
    else:
        taf_list = []


    raw_metar = m.get("raw_text") or m.get("rawOb") or "METAR not available"
    raw_taf   = taf_list[0].get("raw_text") if taf_list else "TAF not available"

    # Flight category
    vis = parse_visibility(m.get("visib"))
    ceiling = parse_ceiling(m.get("sky_conditions", []))
    category = flight_category(vis, ceiling)

    # Wind
    wind = format_wind(m)

    # ===== MENU BAR =====
    print(f"{wind}  {AIRPORT} | color={category_color(category)}")

    # ===== DROPDOWN =====
    print("---")
    print(f"{AIRPORT} {category}")
    print("---")
    print("METAR")
    print(f"--{raw_metar}")
    print("---")
    print("TAF")
    print(f"--{raw_taf}")

if __name__ == "__main__":
    main()
