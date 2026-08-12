#!/usr/bin/env python3
"""Score actual purchasable monitors against the pane-capacity model.

geometry.py answers "what shape of panel does this layout need?" using idealised
panel classes. This answers the buying question: given real products at real US
prices, how many Claude Code panes does each one actually hold, and what does a
pane cost?

Everything geometric is imported from geometry.py - this file adds no new
arithmetic, only a product list. If the model changes, these numbers change with
it.

Prices are US street prices in USD, gathered 2026-08-12, and they move constantly
- treat them as "what tier of spend is this", not as quotes. `list_usd` is MSRP /
launch RRP where known. See docs/monitor-shortlist.md for sourcing.

Run:  python3 scripts/shortlist.py
      python3 scripts/shortlist.py --tier working --distance 700
      python3 scripts/shortlist.py --json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from geometry import (HACK, TIERS, PANE_CHROME, FULLSCREEN_CHROME_PX,
                      panel_geometry, cell_mm)

# --------------------------------------------------------------------------
# Real products, 2026-08-12
# --------------------------------------------------------------------------
# form: "traditional"  = a normal 16:9 desktop monitor, sold everywhere, boring
#       "ultrawide"    = 21:9, a normal product category but a minority one
#       "super-ultra"  = 32:9, a niche within a niche
#       "tv"           = a television being used as a monitor
#
# street_usd is what it actually sells for; list_usd is RRP/launch price.
PRODUCTS = [
    # name, model, diag_in, aspect_w, aspect_h, px_w, px_h, street, list, form
    ("Dell S3225QS",          "S3225QS",   31.5, 16, 9, 3840, 2160,  330,  400, "traditional"),
    ("LG 32UR500K-B",         "32UR500K",  31.5, 16, 9, 3840, 2160,  300,  400, "traditional"),
    ("Dell UltraSharp 32",    "U3225QE",   31.5, 16, 9, 3840, 2160,  800,  950, "traditional"),
    ("KTC G42P5 (42in OLED)", "G42P5",     42.0, 16, 9, 3840, 2160,  800, 1000, "traditional"),
    ("LG C4 42in OLED TV",    "OLED42C4",  42.0, 16, 9, 3840, 2160,  900, 1400, "tv"),
    ("LG C5 42in OLED TV",    "OLED42C5",  42.0, 16, 9, 3840, 2160, 1000, 1400, "tv"),
    ("LG C-series 48in OLED", "OLED48C4",  48.0, 16, 9, 3840, 2160, 1100, 1500, "tv"),
    ("Deco Gear VIEW401",     "VIEW401",   39.7, 21, 9, 5120, 2160,  680,  750, "ultrawide"),
    ("INNOCN 40in 5K2K",      "40C1U",     39.7, 21, 9, 5120, 2160,  620, 1000, "ultrawide"),
    ("LG 40WP95C-W",          "40WP95C",   39.7, 21, 9, 5120, 2160, 1300, 1600, "ultrawide"),
    ("Dell UltraSharp 40",    "U4025QW",   39.7, 21, 9, 5120, 2160, 2250, 2400, "ultrawide"),
    ("CRUA 49in DQHD",        "CRUA49",    49.0, 32, 9, 5120, 1440,  570,  700, "super-ultra"),
    ("INNOCN 49C1R",          "49C1R",     49.0, 32, 9, 5120, 1440,  675,  900, "super-ultra"),
    ("Samsung Odyssey G9",    "S49CG954",  49.0, 32, 9, 5120, 1440,  850, 1300, "super-ultra"),
    ("Gigabyte AORUS CO49DQ", "CO49DQ",    49.0, 32, 9, 5120, 1440,  900, 1300, "super-ultra"),
    ("Samsung Odyssey OLED G9", "G93SC",   49.0, 32, 9, 5120, 1440,  900, 1600, "super-ultra"),
    ("Acer Predator X49",     "X49bmiphuz", 49.0, 32, 9, 5120, 1440, 1000, 1200, "super-ultra"),
    ("Dell UltraSharp 49",    "U4924DW",   49.0, 32, 9, 5120, 1440, 1410, 1500, "super-ultra"),
    ("Samsung Odyssey Neo G9", "G95NC",    57.0, 32, 9, 7680, 2160, 1600, 2500, "super-ultra"),
    # Reference point, not for sale separately:
    ("[laptop, for reference]", "eDP-1",   15.6, 16, 9, 1920, 1080,    0,    0, "traditional"),
]


def capacity(p, tier, arcmin, distance_mm, chrome_px):
    """Usable grid and pane capacity for one product."""
    _name, _model, diag, aw, ah, pw, ph = p[:7]
    w_mm, h_mm, px_per_mm, ppi = panel_geometry(diag, aw, ah, pw, ph)
    cw_mm, ch_mm, _ = cell_mm(HACK, arcmin, distance_mm)
    cw_px, ch_px = cw_mm * px_per_mm, ch_mm * px_per_mm

    cols = int(pw // cw_px)
    rows = int((ph - chrome_px) // ch_px)

    per_pane_cols = TIERS[tier]["cols"] + PANE_CHROME["cols"]
    per_pane_rows = TIERS[tier]["rows"] + PANE_CHROME["rows"]
    across = cols // per_pane_cols
    down = rows // per_pane_rows
    return {
        "ppi": round(ppi),
        "width_mm": round(w_mm),
        "grid": [cols, rows],
        "panes_across": across,
        "panes_down": down,
        "panes_one_row": across if down >= 1 else 0,
        "panes_max_grid": across * down,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tier", default="observed", choices=sorted(TIERS))
    ap.add_argument("--distance", type=float, default=700.0, help="mm")
    ap.add_argument("--arcmin", type=float, default=16.8)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    chrome = FULLSCREEN_CHROME_PX
    rows_out = []
    for p in PRODUCTS:
        name, model, diag, aw, ah, pw, ph, street, lst, form = p
        c = capacity(p, args.tier, args.arcmin, args.distance, chrome)
        panes = c["panes_one_row"] or c["panes_max_grid"]
        rows_out.append({
            "name": name, "model": model, "form": form,
            "diagonal_in": diag, "aspect": f"{aw}:{ah}",
            "resolution": f"{pw}x{ph}", "ppi": c["ppi"],
            "street_usd": street, "list_usd": lst,
            "usable_grid": f"{c['grid'][0]}x{c['grid'][1]}",
            "panes_one_row": c["panes_one_row"],
            "panes_max_grid": c["panes_max_grid"],
            "usd_per_pane": round(street / panes) if panes and street else None,
        })

    if args.json:
        print(json.dumps({
            "tier": args.tier, "tier_cells": TIERS[args.tier],
            "distance_mm": args.distance, "arcmin": args.arcmin,
            "chrome_px": chrome,
            "prices_gathered": "2026-08-12",
            "price_caveat": "US street prices, USD, indicative only - they move "
                            "weekly and none of these were re-checked at time of "
                            "run.",
            "products": rows_out,
        }, indent=2))
        return

    t = TIERS[args.tier]
    print(f"Tier '{args.tier}' = {t['cols']}x{t['rows']} per pane, "
          f"{args.distance:.0f} mm, {args.arcmin}'")
    print(f"Panes counted in a SINGLE ROW (the layout actually in use); "
          f"'grid' is the best 2D packing.\n")
    print(f"{'monitor':26} {'form':13} {'res':>10} {'PPI':>4} "
          f"{'usable':>9} {'row':>4} {'grid':>5} {'USD':>6} {'$/pane':>7}")
    for r in rows_out:
        print(f"{r['name'][:26]:26} {r['form']:13} {r['resolution']:>10} "
              f"{r['ppi']:>4} {r['usable_grid']:>9} {r['panes_one_row']:>4} "
              f"{r['panes_max_grid']:>5} {r['street_usd'] or '-':>6} "
              f"{r['usd_per_pane'] or '-':>7}")


if __name__ == "__main__":
    main()
