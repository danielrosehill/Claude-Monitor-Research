#!/usr/bin/env python3
"""How much of a panel can you actually look at without moving your head?

geometry.py answers "do the characters fit and are they legible". It says nothing
about whether the pixels are somewhere your neck is willing to go, which is the
axis that decides between a portrait panel and a landscape one at identical cost
and identical pane count.

The model: at a fixed viewing distance there is a rectangle of comfortable gaze,
bounded by eye rotation alone. Beyond it you turn your head; beyond that you turn
your chair. Terminal panes outside the comfortable rectangle are not "extra
screen", they are screen you will stop checking.

Angular limits, ISO 9241-303 / ISO 9241-5 and standard human-factors practice:

  horizontal   +/- 30 deg   comfortable eye rotation, symmetric
  vertical     +5 to -30    NOT symmetric. Looking down is cheap and is the
                            natural resting gaze; looking up loads the neck
                            extensors and dries the eyes. Screen tops above eye
                            level are the single most common ergonomic fault.

That asymmetry is the whole reason a portrait panel scores badly and is invisible
to any pixel-count analysis.

Run:  python3 scripts/ergonomics.py
      python3 scripts/ergonomics.py --distance 600 --json
"""

import argparse
import json
import math

# Comfortable gaze cone, degrees.
GAZE = {"left": 30.0, "right": 30.0, "up": 5.0, "down": 30.0}
# With head rotation added - still "usable", but it is a movement, not a glance.
GAZE_HEAD = {"left": 55.0, "right": 55.0, "up": 15.0, "down": 40.0}


def comfort_box(distance_mm, gaze=GAZE):
    """The rectangle of comfortable gaze at this distance, in mm."""
    w = distance_mm * (math.tan(math.radians(gaze["left"]))
                       + math.tan(math.radians(gaze["right"])))
    h = distance_mm * (math.tan(math.radians(gaze["up"]))
                       + math.tan(math.radians(gaze["down"])))
    return w, h


def panel_mm(diagonal_in, aspect_w, aspect_h):
    diag = diagonal_in * 25.4
    r = math.hypot(aspect_w, aspect_h)
    return diag * aspect_w / r, diag * aspect_h / r


def coverage(diagonal_in, aspect_w, aspect_h, distance_mm, gaze=GAZE):
    """What fraction of the panel sits inside the comfortable rectangle?

    The panel is assumed centred horizontally, and positioned vertically the way
    an ergonomically set-up display is: top of screen at eye level. That is the
    best case for a tall panel, and it is still not enough to save one.
    """
    pw, ph = panel_mm(diagonal_in, aspect_w, aspect_h)
    cw, ch = comfort_box(distance_mm, gaze)

    # Horizontal: centred, so overlap is symmetric.
    vis_w = min(pw, cw)

    # Vertical: top of panel at eye level. The comfort box extends `up` above eye
    # level and `down` below, so the panel occupies from 0 down to -ph.
    down_mm = distance_mm * math.tan(math.radians(gaze["down"]))
    vis_h = min(ph, down_mm)

    return {
        "panel_mm": [round(pw), round(ph)],
        "comfort_mm": [round(cw), round(ch)],
        "visible_mm": [round(vis_w), round(vis_h)],
        "coverage": round((vis_w * vis_h) / (pw * ph), 3),
        "width_over": round(max(0.0, pw - cw)),
        "height_over": round(max(0.0, ph - down_mm)),
    }


FORMS = [
    # label, diagonal_in, aspect_w, aspect_h
    ("24in 16:9 landscape",        23.8, 16, 9),
    ("27in 16:9 landscape",        27.0, 16, 9),
    ("32in 16:9 landscape",        31.5, 16, 9),
    ("42in 16:9 landscape",        42.0, 16, 9),
    ("48in 16:9 landscape",        48.0, 16, 9),
    ("24in 9:16 PORTRAIT",         23.8, 9, 16),
    ("27in 9:16 PORTRAIT",         27.0, 9, 16),
    ("32in 9:16 PORTRAIT",         31.5, 9, 16),
    ("26.5in 1:1 square",          26.5, 1, 1),
    ("27.6in 16:18 near-square",   27.6, 16, 18),
    ("40in 21:9 ultrawide",        39.7, 21, 9),
    ("49in 32:9 super-ultra",      49.0, 32, 9),
    ("57in 32:9 super-ultra",      57.0, 32, 9),
    ("29in bar 1920x540",          29.0, 16, 4.5),
    ("8.8in bar 1920x480",          8.8, 4, 1),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--distance", type=float, default=700.0, help="mm")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cw, ch = comfort_box(args.distance)
    out = {"distance_mm": args.distance,
           "gaze_deg": GAZE,
           "comfort_box_mm": [round(cw), round(ch)],
           "comfort_aspect": round(cw / ch, 2),
           "forms": []}

    for label, d, aw, ah in FORMS:
        # The tiny bar display is a near-field device; judge it at arm's length.
        dist = 500.0 if d < 12 else args.distance
        c = coverage(d, aw, ah, dist)
        c["label"] = label
        c["distance_mm"] = dist
        out["forms"].append(c)

    if args.json:
        print(json.dumps(out, indent=2))
        return

    print(f"Comfortable gaze at {args.distance:.0f} mm "
          f"(eyes only, no head movement):")
    print(f"  {cw:.0f} x {ch:.0f} mm  =  {cw/ch:.2f}:1")
    print(f"  horizontal +/-{GAZE['left']:.0f} deg, "
          f"vertical +{GAZE['up']:.0f} to -{GAZE['down']:.0f} deg\n")
    print(f"{'form factor':28}{'panel mm':>12}{'in comfort':>12}"
          f"{'cover':>7}{'overflow':>18}")
    for c in out["forms"]:
        pw, ph = c["panel_mm"]
        vw, vh = c["visible_mm"]
        over = []
        if c["width_over"]:
            over.append(f"{c['width_over']}mm wide")
        if c["height_over"]:
            over.append(f"{c['height_over']}mm tall")
        print(f"{c['label']:28}{f'{pw}x{ph}':>12}{f'{vw}x{vh}':>12}"
              f"{c['coverage']*100:>6.0f}%{', '.join(over) or '-':>18}")


if __name__ == "__main__":
    main()
