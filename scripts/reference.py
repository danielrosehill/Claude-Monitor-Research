#!/usr/bin/env python3
"""Workstation configurations scored on all four axes at once.

The question this answers is not "how many panes fit" - geometry.py does that -
but "what are the ways you could actually set up a desk for this, and which of
them are good?" Four axes, because a configuration can win one and lose the rest:

  economic    USD per pane you will actually use
  ergonomic   how many panes land inside comfortable gaze (ergonomics.py)
  ease        scaling, cabling, timings, whether it is one boring purchase
  quality     glyph pixels, subpixel layout, panel technology

The headline metric is COMFORTABLE panes, not total panes. A pane you have to
turn your head to read is not a monitored session, it is a session you will
forget about. Panes are counted by placing them left-to-right, top-to-bottom and
testing whether each pane's centre falls inside the comfortable gaze rectangle.

Emits data/reference.json, which both the README table and the Typst reference
in reference/ are generated from - so all three stay in sync by construction.

Run:  python3 scripts/reference.py
      python3 scripts/reference.py --tier working
      python3 scripts/reference.py --json > data/reference.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from geometry import HACK, TIERS, PANE_CHROME, FULLSCREEN_CHROME_PX, cell_mm
from ergonomics import comfort_box, panel_mm

# --------------------------------------------------------------------------
# Panels available to build a configuration from
# --------------------------------------------------------------------------
# diag_in, aspect_w, aspect_h, px_w, px_h, usd, form, note
PANELS = {
    "24-1080":   (23.8, 16, 9, 1920, 1080,  100, "traditional", "commodity office panel"),
    "27-1440":   (27.0, 16, 9, 2560, 1440,  180, "traditional", "commodity"),
    "27-4k":     (27.0, 16, 9, 3840, 2160,  350, "traditional", "163 PPI, needs scaling"),
    "32-4k":     (31.5, 16, 9, 3840, 2160,  310, "traditional", "140 PPI, matches laptop"),
    "42-4k-oled":(42.0, 16, 9, 3840, 2160,  800, "tv-class",    "WRGB subpixel, text fringes"),
    "48-4k-oled":(48.0, 16, 9, 3840, 2160, 1100, "tv-class",    "WRGB subpixel, text fringes"),
    "40-5k2k":   (39.7, 21,  9, 5120, 2160,  620, "ultrawide",  "140 PPI, rare category"),
    "49-dqhd":   (49.0, 32,  9, 5120, 1440,  570, "super-ultra", "109 PPI"),
    "57-dual4k": (57.0, 32,  9, 7680, 2160, 1600, "super-ultra", "needs DisplayPort 2.1"),
    "26-square": (26.5,  1,  1, 1920, 1920,  500, "square",     "Eizo EV2730Q, DISCONTINUED, used only"),
    "28-dualup": (27.6, 16, 18, 2560, 2880,  697, "near-square", "LG DualUp 28MQ780, current product"),
    "bar-8.8":   ( 8.8,  4,  1, 1920,  480,   70, "bar",        "status strip, cannot hold a pane"),
    "bar-29":    (29.0, 16, 4.5, 1920, 540,  200, "bar",        "signage panel, price is an estimate"),
    # Vertical-NATIVE: the panel is manufactured taller than wide, or is sold
    # and warranted for vertical installation. Not a rotated landscape monitor.
    "32-signage-v": (31.5, 9, 16, 1080, 1920, 380, "vertical-native",
                     "commercial portrait-only signage panel, 24/7 rated, "
                     "price converted from UK inc-VAT listing"),
    "geminos":      (23.8, 16, 9, 1920, 1080, 320, "vertical-native",
                     "one half of a Mobile Pixels Geminos stacked pair"),
}

# --------------------------------------------------------------------------
# Configurations: named desk setups
# --------------------------------------------------------------------------
# panels: list of (key, rotated) - rotated=True means physically turned portrait
# (name, [(panel_key, rotated)], distance_mm, arrangement)
# rotated=True means a LANDSCAPE panel physically turned 90 degrees. That is a
# different thing from a vertical-native panel and carries a real text-rendering
# penalty - see docs/vertical-and-exotic-form-factors.md.
CONFIGS = [
    ("Laptop only (today)",       [("laptop", False)],                    500, "row"),
    ("One boring monitor",        [("32-4k", False)],                     700, "row"),
    ("Rotated economy grid",      [("24-1080", True)] * 3,                700, "row"),
    ("Rotated 4K pair",           [("27-4k", True)] * 2,                  700, "row"),
    ("Rotated single tall",       [("32-4k", True)],                      700, "row"),
    ("Vertical-native signage",   [("32-signage-v", False)] * 2,          700, "row"),
    ("Geminos stacked pair",      [("geminos", False)] * 2,               700, "stack"),
    ("Near-square (LG DualUp)",   [("28-dualup", False)],                 700, "row"),
    ("The wide row",              [("49-dqhd", False)],                   700, "row"),
    ("Working-pane rig",          [("40-5k2k", False)],                   700, "row"),
    ("Main panel + status strip", [("32-4k", False), ("bar-8.8", False)], 700, "row"),
    ("Twin 32in",                 [("32-4k", False)] * 2,                 700, "row"),
    ("TV class",                  [("48-4k-oled", False)],                700, "row"),
    ("The wall",                  [("57-dual4k", False)],                 700, "row"),
]

LAPTOP = (15.6, 16, 9, 1920, 1080, 0, "traditional", "the machine you have")


def panel_spec(key):
    return LAPTOP if key == "laptop" else PANELS[key]


def score(config, tier, arcmin, distance_mm):
    name, panels, dist, arrangement = config
    dist = distance_mm or dist
    cw_mm, ch_mm, _ = cell_mm(HACK, arcmin, dist)
    comfort_w, comfort_h = comfort_box(dist)

    per_w = TIERS[tier]["cols"] + PANE_CHROME["cols"]
    per_h = TIERS[tier]["rows"] + PANE_CHROME["rows"]
    pane_w_mm = per_w * cw_mm
    pane_h_mm = per_h * ch_mm

    total_panes = comfy_panes = 0
    cost = 0
    forms, notes = [], []
    array_w = 0.0
    max_h = 0.0

    for key, rotated in panels:
        diag, aw, ah, pw, ph, usd, form, note = panel_spec(key)
        if rotated:
            aw, ah = ah, aw
            pw, ph = ph, pw
            form = form + " (rotated)"
        w_mm, h_mm = panel_mm(diag, aw, ah)
        cost += usd
        forms.append(form)
        if note not in notes:
            notes.append(note)
        if arrangement == "stack":
            array_w = max(array_w, w_mm)
            max_h += h_mm
        else:
            array_w += w_mm
            max_h = max(max_h, h_mm)

    # Place the array centred horizontally on the viewer with the top edge at eye
    # level, then walk the pane grid and test whether each pane's centre falls
    # inside the comfortable gaze rectangle.
    x_cursor = -array_w / 2.0
    y_cursor = 0.0
    down_limit = comfort_h  # measured downward from eye level
    for key, rotated in panels:
        diag, aw, ah, pw, ph, usd, form, note = panel_spec(key)
        if rotated:
            aw, ah = ah, aw
            pw, ph = ph, pw
        w_mm, h_mm = panel_mm(diag, aw, ah)
        px_per_mm = pw / w_mm

        cols = int(pw // (cw_mm * px_per_mm))
        rows = int((ph - FULLSCREEN_CHROME_PX) // (ch_mm * px_per_mm))
        across = cols // per_w
        down = rows // per_h

        # A stacked panel is centred horizontally; a row panel walks rightward.
        panel_x0 = -w_mm / 2.0 if arrangement == "stack" else x_cursor

        for r in range(down):
            for c in range(across):
                total_panes += 1
                cx = panel_x0 + (c + 0.5) * pane_w_mm
                cy = y_cursor + (r + 0.5) * pane_h_mm  # downward from array top
                if abs(cx) <= comfort_w / 2 and cy <= down_limit:
                    comfy_panes += 1

        if arrangement == "stack":
            y_cursor += h_mm
        else:
            x_cursor += w_mm

    return {
        "config": name,
        "arrangement": arrangement,
        "panels": [f"{'rotated ' if rot else ''}{k}" for k, rot in panels],
        "form": "+".join(sorted(set(forms))),
        "distance_mm": dist,
        "array_mm": [round(array_w), round(max_h)],
        "comfort_mm": [round(comfort_w), round(comfort_h)],
        "panes_total": total_panes,
        "panes_comfortable": comfy_panes,
        "usd": cost,
        "usd_per_comfortable_pane": round(cost / comfy_panes) if comfy_panes else None,
        "notes": "; ".join(notes),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tier", default="observed", choices=sorted(TIERS))
    ap.add_argument("--arcmin", type=float, default=16.8)
    ap.add_argument("--distance", type=float, default=None,
                    help="override each config's natural distance, mm")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rows = [score(c, args.tier, args.arcmin, args.distance) for c in CONFIGS]

    if args.json:
        print(json.dumps({
            "generated": "scripts/reference.py",
            "tier": args.tier,
            "tier_cells": TIERS[args.tier],
            "arcmin": args.arcmin,
            "gathered": "2026-08-12",
            "price_caveat": "US street prices, USD, indicative of tier only. Bar "
                            "and square panel prices are estimates; the Eizo "
                            "square is discontinued and used-only.",
            "configs": rows,
        }, indent=2))
        return

    t = TIERS[args.tier]
    print(f"Tier '{args.tier}' = {t['cols']}x{t['rows']} cells per pane, {args.arcmin}'")
    print("'comfy' = panes whose centre is inside the comfortable gaze rectangle\n")
    print(f"{'configuration':28}{'form':22}{'array mm':>11}"
          f"{'total':>6}{'comfy':>6}{'USD':>6}{'$/comfy':>8}")
    for r in sorted(rows, key=lambda x: -(x["panes_comfortable"])):
        aw, ah = r["array_mm"]
        print(f"{r['config']:28}{r['form'][:22]:22}{f'{aw}x{ah}':>11}"
              f"{r['panes_total']:>6}{r['panes_comfortable']:>6}"
              f"{r['usd']:>6}{r['usd_per_comfortable_pane'] or '-':>8}")


if __name__ == "__main__":
    main()
