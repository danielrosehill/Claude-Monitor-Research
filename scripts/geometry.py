#!/usr/bin/env python3
"""Readability geometry for a terminal-grid monitor.

Answers: given N concurrent Claude Code sessions that must stay legible at a
desk viewing distance, what physical panel and what pixel count does that
require — and which existing panel classes satisfy it?

The chain is:

    angular target (arcmin)  ->  physical cap height at distance D (mm)
                             ->  physical cell size (mm)          [font metrics]
                             ->  physical grid size (mm)          [pane tier x layout]
                             ->  required panel diagonal + aspect
                             ->  required resolution at that panel's density

Nothing here is monitor-specific until the last step. The first four are pure
ergonomics and typography, so changing the font or the distance re-derives the
whole answer.

Run:  python3 scripts/geometry.py            # human-readable report
      python3 scripts/geometry.py --json     # machine-readable, for docs/data

Verified 2026-08-12 against the measured baseline in
evidence/konsole-4-pane-1920x1080-2026-08-12.png.
"""

import argparse
import json
import math

# --------------------------------------------------------------------------
# Font metrics
# --------------------------------------------------------------------------
# Read from /usr/share/fonts/truetype/hack/Hack-Regular.ttf via fontTools on
# 2026-08-12. unitsPerEm = 2048.
#
# CAP_EM and ADV_EM come straight from the font. LINE_EM does NOT: the font's
# hhea line height is 1.1641 em, but Konsole actually lays out at 22.0 px for
# Hack 14 (= 18.667 px em), i.e. 1.179 em. The measured value is used, because
# the pixel that matters is the one Konsole draws, not the one the font
# suggests. Measured off the baseline screenshot: 14 line gaps over 308 px.
HACK = {
    "name": "Hack",
    "cap_em": 1493 / 2048,      # 0.7290 - capital letter height, the ISO 9241 metric
    "adv_em": 1233 / 2048,      # 0.6021 - monospace advance width
    "line_em": 22.0 / (14 * 96 / 72),  # 1.1786 - measured Konsole line pitch
}

# --------------------------------------------------------------------------
# Ergonomic targets - ISO 9241-303:2011, readability/legibility clause
# --------------------------------------------------------------------------
# 16' is the absolute minimum character height the standard permits.
# 20-22' is the range a display is required to be *capable* of providing, and
# is what ISO 9241-306 ties to the 400-750 mm desk viewing distances users
# actually prefer.
ANGULAR = {
    "iso_floor": 16.0,      # do not go below this
    "current": 16.8,        # what the laptop delivers today at 500 mm - measured
    "iso_target_low": 20.0,
    "iso_target_high": 22.0,
}

# --------------------------------------------------------------------------
# What one Claude Code pane needs, in text cells
# --------------------------------------------------------------------------
# Content only. Per-pane chrome (Konsole's pane title bar, the divider and the
# scrollbar) is added separately as PANE_CHROME.
TIERS = {
    "observed": {
        "cols": 26, "rows": 39,
        "note": "Measured, not assumed. The 1x6 vertical split actually in daily use "
                "on the 1920x1080 laptop, read live off Konsole on 2026-08-12. Far "
                "narrower and more than twice as tall as the 'glanceable' tier was "
                "guessed to be, because splitting vertically hands every pane the "
                "full panel height for nothing.",
    },
    "daily": {
        "cols": 40, "rows": 31,
        "note": "THE RECOMMENDATION - see docs/recommendation.md. 40 columns "
                "because columns are the scarce axis and 26 is a tolerance, not "
                "a preference. 31 rows because that is what a 32in 4K yields at "
                "two rows of panes, and it is ample: measured against the "
                "simulated sessions in fixtures/, the MEDIAN session needs 19 "
                "rows at 40 columns and only the longest exceeds 31. Unlike the "
                "observed tier's 39 rows - which is what the laptop happened to "
                "give, not what a session needs - this row count is derived from "
                "content demand.",
    },
    "glanceable": {
        "cols": 60, "rows": 18,
        "note": "Spinner, current action line, and whether it is asking a question. "
                "Monitoring only - you cannot work in this pane, you can only see "
                "that it is alive. ASSUMED - and the observed tier above shows the "
                "shape of this guess was wrong on both axes.",
    },
    "working": {
        "cols": 80, "rows": 30,
        "note": "The 80-column norm Claude Code's output is laid out against, plus "
                "enough rows to see one complete tool call above the input box. "
                "This is the real target.",
    },
    "review": {
        "cols": 100, "rows": 45,
        "note": "A diff hunk with surrounding context, unwrapped. What you need for "
                "the pane you are actually driving, as opposed to watching.",
    },
}

PANE_CHROME = {"cols": 1, "rows": 1}  # divider column, pane title row

# --------------------------------------------------------------------------
# Measured pixel anatomy of a real multi-pane window
# --------------------------------------------------------------------------
# Read on 2026-08-12 from a live Konsole (6 sessions, maximised, 1920x1080
# eDP-1) two independent ways that agree:
#
#   1. Cell grid, authoritative: qdbus6 org.kde.konsole-<pid> /Sessions/<n>
#      Session.processId -> ps -o tty= -> stty -F /dev/pts/<n> size.
#      This is the pty's own idea of its size, not an estimate off an image.
#   2. Pixel bounds: column-uniformity scan of
#      evidence/konsole-6-pane-1920x1080-2026-08-12.png.
#
# The two together pin the per-pane overhead that the "1 divider column"
# approximation above understates: a pane costs 15 px of scrollbar plus 11 px
# of splitter handle = 26 px, which at an 11.24 px advance is ~2.3 columns,
# not 1. Across six panes that is 156 px - 8.1% of the panel width - spent
# before a single character is drawn.
MEASURED_6PANE = {
    "date": "2026-08-12",
    "display": {"output": "eDP-1", "px": [1920, 1080], "mm": [344, 193],
                "diagonal_in": 15.6, "ppi": 141.8},
    "host": "daniellaptop (Lenovo ThinkPad E15 Gen 3)",
    "session_type": "wayland",
    "layout": "1x6 (six panes side by side, one row)",
    # cols x rows straight from stty, per pane, left to right
    "panes_cells": [[26, 39], [26, 39], [26, 39], [27, 39], [25, 39], [26, 39]],
    "pane_widths_px": [313, 320, 320, 336, 305, 326],
    "scrollbar_px": 15,
    "splitter_px": 11,
    # Vertical budget, top to bottom, summing to 1080:
    "window_chrome_px": 136,   # title bar + menu bar + toolbar + tab bar
    "pane_title_px": 29,       # per-pane title strip
    "content_px": 858,         # 39 rows x 22.0 px line pitch
    "bottom_margin_px": 16,
    "taskbar_px": 40,
}

# Full-screen vertical overhead: the non-content pixels a maximised window
# pays that are NOT per-pane. pane_title_px is deliberately excluded - it
# recurs once per row of panes, so it is PANE_CHROME's job, and counting it
# here as well would charge it twice for a single-row layout.
#
# The 168 px constant above is the *window*-internal figure measured off the
# 4-pane capture (1913x1038, taskbar excluded, pane title included); this is
# the figure that applies when the window is maximised on the panel.
FULLSCREEN_CHROME_PX = (MEASURED_6PANE["window_chrome_px"]
                        + MEASURED_6PANE["bottom_margin_px"]
                        + MEASURED_6PANE["taskbar_px"])  # = 192

# --------------------------------------------------------------------------
# Existing panel classes
# --------------------------------------------------------------------------
# Physical dimensions are derived from diagonal + aspect, not quoted from spec
# sheets, so they are consistent with each other. Bezels excluded.
PANELS = [
    # 15.6, not 14: xrandr reports 344x193 mm, a 396 mm / 15.6" diagonal.
    ("laptop eDP-1 (current)", 15.6, 16, 9, 1920, 1080),
    ("24in 16:9 FHD", 23.8, 16, 9, 1920, 1080),
    ("24in 16:10 WUXGA", 24.0, 16, 10, 1920, 1200),
    ("27in 16:9 QHD", 27.0, 16, 9, 2560, 1440),
    ("27in 16:9 4K", 27.0, 16, 9, 3840, 2160),
    ("32in 16:9 4K", 32.0, 16, 9, 3840, 2160),
    ("42in 16:9 4K (OLED TV class)", 42.0, 16, 9, 3840, 2160),
    ("48in 16:9 4K (OLED TV class)", 48.0, 16, 9, 3840, 2160),
    ("34in 21:9 UWQHD", 34.0, 21, 9, 3440, 1440),
    ("45in 21:9 UWQHD", 45.0, 21, 9, 3440, 1440),
    ("40in 21:9 5K2K", 39.7, 21, 9, 5120, 2160),
    ("49in 32:9 DQHD", 49.0, 32, 9, 5120, 1440),
    ("57in 32:9 Dual-4K", 57.0, 32, 9, 7680, 2160),
    ("32in 4K rotated to portrait", 32.0, 9, 16, 2160, 3840),
]

# Window chrome outside the terminal grid: Konsole title bar, menu bar,
# toolbar and tab bar. Measured at 168 px on the baseline screenshot.
WINDOW_CHROME_PX = 168


def arcmin_to_mm(arcmin, distance_mm):
    """Physical height subtending `arcmin` minutes of arc at `distance_mm`."""
    return 2 * distance_mm * math.tan(math.radians(arcmin / 60) / 2)


def cell_mm(font, arcmin, distance_mm):
    """Physical size of one text cell, in mm, to hit the angular target."""
    cap = arcmin_to_mm(arcmin, distance_mm)
    em = cap / font["cap_em"]
    return em * font["adv_em"], em * font["line_em"], em


def panel_geometry(diagonal_in, aspect_w, aspect_h, px_w, px_h):
    """Physical width/height in mm and pixel density, from diagonal + aspect."""
    diag_mm = diagonal_in * 25.4
    ratio = aspect_w / aspect_h
    norm = math.hypot(ratio, 1)
    w_mm = diag_mm * ratio / norm
    h_mm = diag_mm / norm
    return w_mm, h_mm, px_w / w_mm, px_w / w_mm * 25.4


def required_cells(tier, grid_cols, grid_rows):
    """Total text cells needed for a grid_cols x grid_rows arrangement."""
    t = TIERS[tier]
    return (
        (t["cols"] + PANE_CHROME["cols"]) * grid_cols,
        (t["rows"] + PANE_CHROME["rows"]) * grid_rows,
    )


def evaluate(panel, font, arcmin, distance_mm, tier, grid_cols, grid_rows,
             chrome_px=WINDOW_CHROME_PX):
    """Does `panel` fit this grid at this legibility target?"""
    name, diag, aw, ah, pw, ph = panel
    w_mm, h_mm, px_per_mm, ppi = panel_geometry(diag, aw, ah, pw, ph)
    cw_mm, ch_mm, _ = cell_mm(font, arcmin, distance_mm)

    # Cell size in this panel's pixels, then the grid it can actually show.
    cw_px = cw_mm * px_per_mm
    ch_px = ch_mm * px_per_mm
    avail_cols = int(pw // cw_px)
    avail_rows = int((ph - chrome_px) // ch_px)

    need_cols, need_rows = required_cells(tier, grid_cols, grid_rows)
    return {
        "panel": name,
        "diagonal_in": diag,
        "aspect": f"{aw}:{ah}",
        "resolution": f"{pw}x{ph}",
        "ppi": round(ppi, 1),
        "physical_mm": [round(w_mm), round(h_mm)],
        "font_pt_needed": round(cell_mm(font, arcmin, distance_mm)[2] * px_per_mm * 72 / 96, 1),
        "available_cells": [avail_cols, avail_rows],
        "required_cells": [need_cols, need_rows],
        "fits": avail_cols >= need_cols and avail_rows >= need_rows,
        "limiting_axis": (
            "none" if avail_cols >= need_cols and avail_rows >= need_rows
            else "vertical" if avail_cols >= need_cols
            else "horizontal" if avail_rows >= need_rows
            else "both"
        ),
        "max_panes_this_shape": (avail_cols // (TIERS[tier]["cols"] + 1))
                                * (avail_rows // (TIERS[tier]["rows"] + 1)),
    }


def ideal_panel(font, arcmin, distance_mm, tier, grid_cols, grid_rows, ppi,
                chrome_px=WINDOW_CHROME_PX):
    """The panel this requirement implies, ignoring what is on the market."""
    cw_mm, ch_mm, _ = cell_mm(font, arcmin, distance_mm)
    need_cols, need_rows = required_cells(tier, grid_cols, grid_rows)
    w_mm = need_cols * cw_mm
    h_mm = need_rows * ch_mm + chrome_px / (ppi / 25.4)
    return {
        "tier": tier,
        "layout": f"{grid_cols}x{grid_rows}",
        "panes": grid_cols * grid_rows,
        "angular_target_arcmin": arcmin,
        "viewing_distance_mm": distance_mm,
        "required_cells": [need_cols, need_rows],
        "physical_mm": [round(w_mm), round(h_mm)],
        "diagonal_in": round(math.hypot(w_mm, h_mm) / 25.4, 1),
        "aspect_ratio": round(w_mm / h_mm, 2),
        "aspect_as_x9": f"{round(w_mm / h_mm * 9, 1)}:9",
        "resolution_at_ppi": [
            round(w_mm * ppi / 25.4), round(h_mm * ppi / 25.4)
        ],
        "assumed_ppi": ppi,
    }


def composite_panel(font, arcmin, distance_mm, focus_tier, watch_tier,
                    watch_cols, watch_rows, ppi, chrome_px=WINDOW_CHROME_PX):
    """A two-zone layout: one full pane you work in, plus a grid you only watch.

    This is the shape the tier arithmetic pushes towards. Eight *working* panes
    needs a 39-51" panel, but eight *glanceable* panes plus one review pane is
    a far smaller target, because only one session at a time is being read
    properly - the other seven only have to answer "are you blocked?".
    """
    cw_mm, ch_mm, _ = cell_mm(font, arcmin, distance_mm)
    focus = TIERS[focus_tier]
    watch = TIERS[watch_tier]

    cols = (focus["cols"] + 1) + (watch["cols"] + 1) * watch_cols
    rows = max(focus["rows"] + 1, (watch["rows"] + 1) * watch_rows)

    w_mm = cols * cw_mm
    h_mm = rows * ch_mm + chrome_px / (ppi / 25.4)
    return {
        "layout": f"1x {focus_tier} + {watch_cols}x{watch_rows} {watch_tier}",
        "panes": 1 + watch_cols * watch_rows,
        "angular_target_arcmin": arcmin,
        "required_cells": [cols, rows],
        "physical_mm": [round(w_mm), round(h_mm)],
        "diagonal_in": round(math.hypot(w_mm, h_mm) / 25.4, 1),
        "aspect_ratio": round(w_mm / h_mm, 2),
        "aspect_as_x9": f"{round(w_mm / h_mm * 9, 1)}:9",
        "resolution_at_ppi": [round(w_mm * ppi / 25.4), round(h_mm * ppi / 25.4)],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--distance", type=float, default=700.0,
                    help="viewing distance in mm (default 700, desk monitor)")
    ap.add_argument("--arcmin", type=float, default=None,
                    help="angular cap height target (default: sweep the ISO range)")
    ap.add_argument("--tier", default="working", choices=list(TIERS))
    ap.add_argument("--panes", type=int, default=8)
    ap.add_argument("--layout", default=None,
                    help="force a grid, e.g. 4x2 (default: closest to square)")
    ap.add_argument("--ppi", type=float, default=140.0,
                    help="assumed density for the ideal panel (default 140, "
                         "matching the laptop so font size carries over)")
    ap.add_argument("--fullscreen", action="store_true",
                    help="charge the maximised-window vertical overhead "
                         f"({FULLSCREEN_CHROME_PX} px, measured, includes the "
                         f"Plasma taskbar) instead of the window-internal "
                         f"{WINDOW_CHROME_PX} px")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    chrome_px = FULLSCREEN_CHROME_PX if args.fullscreen else WINDOW_CHROME_PX

    targets = ([args.arcmin] if args.arcmin
               else [ANGULAR["current"], ANGULAR["iso_target_low"], ANGULAR["iso_target_high"]])

    # Every rectangular arrangement of the requested pane count.
    layouts = [(c, args.panes // c) for c in range(1, args.panes + 1)
               if args.panes % c == 0]

    out = {
        "font": HACK["name"],
        "font_metrics": {k: round(v, 4) for k, v in HACK.items() if k != "name"},
        "viewing_distance_mm": args.distance,
        "tier": args.tier,
        "tier_spec": TIERS[args.tier],
        "chrome_px": chrome_px,
        "measured_reference": MEASURED_6PANE,
        "panes": args.panes,
        "ideal_panels": [],
        "existing_panels": [],
    }

    for arcmin in targets:
        for gc, gr in layouts:
            out["ideal_panels"].append(
                ideal_panel(HACK, arcmin, args.distance, args.tier, gc, gr,
                            args.ppi, chrome_px))

    # Score existing panels against the most plausible layout: the landscape
    # arrangement closest to square. For 8 panes that is 4x2, not 8x1 - a
    # single row of eight would need 648 columns and no panel comes close.
    if args.layout:
        gc, gr = (int(n) for n in args.layout.lower().split("x"))
        best_layout = (gc, gr)
    else:
        best_layout = min((l for l in layouts if l[0] >= l[1]),
                          key=lambda l: l[0] / l[1])
    for panel in PANELS:
        out["existing_panels"].append(
            evaluate(panel, HACK, ANGULAR["current"], args.distance,
                     args.tier, *best_layout, chrome_px=chrome_px))
    out["scored_layout"] = f"{best_layout[0]}x{best_layout[1]}"

    # The composite alternative: work in one, watch the rest.
    out["composite_panels"] = [
        composite_panel(HACK, arcmin, args.distance, "review", "glanceable",
                        wc, wr, args.ppi, chrome_px)
        for arcmin in targets
        for wc, wr in ((2, 4), (1, 8), (2, 3))
    ]

    if args.json:
        print(json.dumps(out, indent=2))
        return

    print(f"Font {HACK['name']}  cap={HACK['cap_em']:.4f}em  "
          f"adv={HACK['adv_em']:.4f}em  line={HACK['line_em']:.4f}em")
    print(f"Viewing distance {args.distance:.0f} mm   tier '{args.tier}' = "
          f"{TIERS[args.tier]['cols']}x{TIERS[args.tier]['rows']} per pane\n")

    print("=== Cell size required, by angular target ===")
    for arcmin in targets:
        cw, ch, em = cell_mm(HACK, arcmin, args.distance)
        print(f"  {arcmin:5.1f}'  cap={arcmin_to_mm(arcmin, args.distance):5.2f}mm  "
              f"cell={cw:5.2f} x {ch:5.2f}mm  "
              f"(Hack {em * 5.51 * 72 / 96:4.1f}pt at 140 PPI)")

    print(f"\n=== The panel {args.panes} panes implies (ignoring the market) ===")
    print(f"{'target':>7} {'layout':>7} {'cells':>10} {'physical mm':>14} "
          f"{'diag':>7} {'aspect':>8} {'resolution':>12}")
    for row in out["ideal_panels"]:
        if row["aspect_ratio"] < 0.4 or row["aspect_ratio"] > 6:
            continue  # absurd shapes, listed in JSON only
        print(f"{row['angular_target_arcmin']:6.1f}' {row['layout']:>7} "
              f"{row['required_cells'][0]:4d}x{row['required_cells'][1]:<4d} "
              f"{row['physical_mm'][0]:6d}x{row['physical_mm'][1]:<6d} "
              f"{row['diagonal_in']:6.1f}\" {row['aspect_as_x9']:>8} "
              f"{row['resolution_at_ppi'][0]:5d}x{row['resolution_at_ppi'][1]:<5d}")

    print("\n=== Composite: one pane you work in + a grid you only watch ===")
    print(f"{'target':>7} {'layout':>34} {'panes':>6} {'cells':>10} "
          f"{'physical mm':>14} {'diag':>7} {'aspect':>8} {'resolution':>12}")
    for row in out["composite_panels"]:
        print(f"{row['angular_target_arcmin']:6.1f}' {row['layout']:>34} "
              f"{row['panes']:6d} "
              f"{row['required_cells'][0]:4d}x{row['required_cells'][1]:<4d} "
              f"{row['physical_mm'][0]:6d}x{row['physical_mm'][1]:<6d} "
              f"{row['diagonal_in']:6.1f}\" {row['aspect_as_x9']:>8} "
              f"{row['resolution_at_ppi'][0]:5d}x{row['resolution_at_ppi'][1]:<5d}")

    print(f"\n=== Existing panels vs {out['scored_layout']} at "
          f"{ANGULAR['current']}' ({args.tier}) ===")
    print(f"{'panel':<32} {'PPI':>5} {'grid':>10} {'need':>10} {'fits':>6} "
          f"{'limit':>10} {'panes':>6}")
    for row in out["existing_panels"]:
        print(f"{row['panel']:<32} {row['ppi']:5.0f} "
              f"{row['available_cells'][0]:4d}x{row['available_cells'][1]:<5d} "
              f"{row['required_cells'][0]:4d}x{row['required_cells'][1]:<5d} "
              f"{'yes' if row['fits'] else 'no':>6} {row['limiting_axis']:>10} "
              f"{row['max_panes_this_shape']:6d}")


if __name__ == "__main__":
    main()
