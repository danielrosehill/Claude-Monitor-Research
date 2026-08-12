#!/usr/bin/env python3
"""Render true-physical-scale wireframes of a terminal grid.

The point is falsifiability. `geometry.py` asserts a pane size; this script
re-flows real-shaped session content into the pane a given panel would actually
give, **wrapping and clipping exactly as a terminal would**, so the assumption
can be looked at instead of argued about.

Content comes from ../fixtures/sessions.json - see ../fixtures/README.md for the
schema. Keeping it out of this file means the same content re-flows into every
candidate pane size, which is the comparison that matters.

Output is SVG in millimetres: 1 user unit = 1 mm, so the file is at true
physical size. Two ways to use it:

  * Print at 100% scale, tape it to a wall, stand `--distance` mm away.
  * Print scaled to fit the paper and stand proportionally closer. Scaling by k
    and viewing at k x distance preserves angular size exactly, so the verdict
    is unchanged. Each SVG prints its own equivalent distance in the footer.

Run:
    python3 scripts/wireframe.py --list
    python3 scripts/wireframe.py --config 8x1-32in-4k-observed --png
    python3 scripts/wireframe.py --all --png
"""

import argparse
import json
import os
import subprocess
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geometry import (  # noqa: E402
    ANGULAR, HACK, TIERS, WINDOW_CHROME_PX, cell_mm, panel_geometry,
)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "wireframes")
FIXTURES = os.path.join(HERE, "..", "fixtures", "sessions.json")

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------
# Matched BY EYE from screenshots of the live Claude Code TUI taken 2026-08-12;
# the source captures were not retained, so these are not sampled values. Close
# enough to judge legibility and contrast, not close enough to quote. Resample
# from a fresh capture if exact values are ever needed.
PALETTE = {
    "bg": "#1b1b1b",
    "pane": "#191919",
    "titlebar": "#262626",
    "text": "#e6e6e6",       # assistant prose, user input
    "result": "#cfcfcf",     # tool output under the elbow
    "dim": "#8a8a8a",        # truncation notices, elbows, rules
    "tool": "#61afef",       # tool names - bold blue
    "bullet_ok": "#2ea043",  # filled green dot before a tool call
    "bullet_msg": "#e6e6e6", # filled white dot before an assistant message
    "status": "#dd8452",     # Working… / Seasoning… / Lollygagging… - ORANGE
    "alert": "#ff5f5f",      # waiting for input, bypass permissions
    "shell": "#3ad900",      # shell prompt lines
    "border": "#3a3a3a",
    "ink": "#111111",
    "paper": "#ffffff",
}

# Pane border by session state - the signal docs/software-layer.md argues the
# software layer has to surface. Rendering it here shows what it would buy.
STATE_COLOUR = {
    "working": "#3a3a3a",
    "blocked": "#ff5f5f",
    "done": "#2ea043",
    "shell": "#3a3a3a",
}
STATE_GLYPH = {"working": "", "blocked": "●", "done": "✓", "shell": ""}

# kind -> (prefix, prefix colour, body colour, continuation indent)
STYLES = {
    "user":      ("❯ ",   "text",       "text",   "  "),
    "assistant": ("● ",   "bullet_msg", "text",   "  "),
    "tool":      ("● ",   "bullet_ok",  "tool",   "    "),
    "result":    ("  └ ", "dim",        "result", "    "),
    "truncated": ("  ",   "dim",        "dim",    "    "),
    "question":  ("",     "alert",      "alert",  "  "),
    "option":    ("  ",   "text",       "text",   "    "),
    "status":    ("✳ ",   "status",     "status", "  "),
    "alert":     ("",     "alert",      "alert",  "  "),
    "shell":     ("",     "shell",      "shell",  "  "),
}

INPUT_BOX = [
    {"kind": "rule"},
    {"kind": "user", "text": ""},
    {"kind": "footer", "text": "bypass permissions on (shift+tab to cycle)"},
]

CONFIGS = {
    # --- today, measured -------------------------------------------------
    "6x1-laptop-observed": (
        "15.6in laptop — 6 panes side by side, today's measured split",
        15.6, 16, 9, 1920, 1080, 6, 1, "observed", 500.0),
    "4x1-laptop-observed": (
        "15.6in laptop — 4 panes side by side, the baseline screenshot",
        15.6, 16, 9, 1920, 1080, 4, 1, "observed", 500.0),
    # --- does the observed pane size scale to more panes? ----------------
    "8x1-32in-4k-observed": (
        "32in 16:9 4K — 8 panes side by side at the observed pane size",
        32.0, 16, 9, 3840, 2160, 8, 1, "observed", None),
    "8x1-40in-5k2k-observed": (
        "40in 21:9 5K2K — 8 panes side by side at the observed pane size",
        39.7, 21, 9, 5120, 2160, 8, 1, "observed", None),
    "8x1-49in-32x9-observed": (
        "49in 32:9 DQHD — 8 panes side by side at the observed pane size",
        49.0, 32, 9, 5120, 1440, 8, 1, "observed", None),
    # --- the working tier, if 80 columns is really wanted ----------------
    "4x2-40in-5k2k": (
        "40in 21:9 5K2K — 8 panes, 4x2", 39.7, 21, 9, 5120, 2160, 4, 2, "working", None),
    "4x2-32in-4k": (
        "32in 16:9 4K — 8 panes, 4x2", 32.0, 16, 9, 3840, 2160, 4, 2, "working", None),
    "8x1-32in-4k-working": (
        "32in 16:9 4K — 8 panes side by side at 80 columns each",
        32.0, 16, 9, 3840, 2160, 8, 1, "working", None),
    "6x1-32in-4k": (
        "32in 16:9 4K — 6 panes side by side, 6x1", 32.0, 16, 9, 3840, 2160, 6, 1, "working", None),
    "1x6-32in-4k": (
        "32in 16:9 4K — 6 panes stacked as rows, 1x6", 32.0, 16, 9, 3840, 2160, 1, 6, "working", None),
    "4x2-49in-32x9": (
        "49in 32:9 DQHD — 8 panes, 4x2", 49.0, 32, 9, 5120, 1440, 4, 2, "working", None),

    # --- the recommended daily driver -------------------------------------
    # 32in 4K, 6x2. See docs/recommendation.md. Two rows rather than one
    # because a single row hands every pane 63 rows when a measured session
    # uses 39 - spending that surplus on a second row doubles the instance
    # count at 40 columns each, against the 26 in use today.
    "6x2-32in-4k-RECOMMENDED": (
        "32in 16:9 4K — 12 panes, 6x2 — THE RECOMMENDATION",
        31.5, 16, 9, 3840, 2160, 6, 2, "daily", None),
    "9x2-32in-4k-max": (
        "32in 16:9 4K — 18 panes, 9x2 — the maximum at today's column width",
        31.5, 16, 9, 3840, 2160, 9, 2, "observed", None),  # max, judged on cols
    "7x1-32in-4k-roomy": (
        "32in 16:9 4K — 7 panes, 7x1 — roomier than today on both axes",
        31.5, 16, 9, 3840, 2160, 7, 1, "observed", None),

    # --- vertical, square and TV-class form factors -----------------------
    # Added 2026-08-12 alongside scripts/reference.py. Pane grids are not
    # chosen, they are the maximum each panel yields at 700 mm - recompute with
    # reference.py if the tier changes. The point of rendering these is that the
    # pane COUNT flatters several of them while the glyph rendering does not:
    # the 70 PPI signage panel draws Hack at a 7.8 px advance against the
    # laptop's 11.2, and only a wireframe shows what that looks like.
    "5x2-32in-signage-vertical": (
        "32in 9:16 vertical-NATIVE signage (1080x1920, 70 PPI) — 10 panes, 5x2",
        31.5, 9, 16, 1080, 1920, 5, 2, "observed", None),
    "3x2-24in-rotated": (
        "24in 1080p ROTATED to vertical (93 PPI) — 6 panes, 3x2; x3 = the economy grid",
        23.8, 9, 16, 1080, 1920, 3, 2, "observed", None),
    "4x2-27in-4k-rotated": (
        "27in 4K ROTATED to vertical (163 PPI) — 8 panes, 4x2",
        27.0, 9, 16, 2160, 3840, 4, 2, "observed", None),
    "5x2-32in-4k-rotated": (
        "32in 4K ROTATED to vertical (140 PPI) — 10 panes, 5x2",
        31.5, 9, 16, 2160, 3840, 5, 2, "observed", None),
    "6x2-28in-dualup": (
        "27.6in 16:18 LG DualUp, natively taller than wide (140 PPI) — 12 panes, 6x2",
        27.6, 16, 18, 2560, 2880, 6, 2, "observed", None),
    "6x1-26in-square": (
        "26.5in 1:1 square, Eizo EV2730Q class (102 PPI) — 6 panes, 6x1",
        26.5, 1, 1, 1920, 1920, 6, 1, "observed", None),
    "13x2-48in-tv": (
        "48in 16:9 4K TV class (92 PPI) — 26 panes, 13x2",
        48.0, 16, 9, 3840, 2160, 13, 2, "observed", None),
}

# Deliberately NOT rendered: the 8.8in and 29in bar displays. At 700 mm a
# 1920x540 bar yields 23 usable rows and a 1920x480 bar yields 8 - both below
# the 40 rows one pane needs, so there is no pane layout to draw. A bar panel is
# a status strip (one line per session), not a pane device, and this script only
# knows how to draw panes. See docs/vertical-and-exotic-form-factors.md.


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_sessions():
    with open(FIXTURES) as f:
        return json.load(f)


def clip_row(segs, cols):
    """Hard-truncate a row to `cols` characters.

    The guarantee, not the mechanism. textwrap gets this nearly right but not
    exactly - it will exceed `width` to keep a trailing whitespace chunk - and a
    row one character too wide silently draws into the neighbouring pane, which
    would make a too-small pane look usable. Clip unconditionally so a wrapping
    bug shows up as visible truncation instead.
    """
    out, used = [], 0
    for colour, chunk in segs:
        if used >= cols:
            break
        take = chunk[:cols - used]
        if take:
            out.append((colour, take))
            used += len(take)
    return out


def expand(line, cols):
    """One fixture line -> list of rows; each row is [(colour, text), ...].

    Wrapping uses a hanging indent, exactly as the TUI does, which is why
    narrow panes hurt more than a naive character count suggests: every
    continuation line pays the indent again.
    """
    kind = line.get("kind", "assistant")
    if kind == "rule":
        return [[("dim", "─" * cols)]]

    if kind == "footer":
        prefix, pcol, bcol, cont = "▸▸ ", "alert", "alert", "   "
    else:
        prefix, pcol, bcol, cont = STYLES.get(kind, STYLES["assistant"])

    body = line.get("text", "")
    if kind == "tool":
        body = f"{line.get('tool', 'Tool')}({body})"

    # Wrap against the FULL pane width with the prefix and the hanging indent
    # counted in, then strip the placeholder indent back off row 0. Wrapping at
    # (cols - prefix) instead lets continuation lines reach cols + len(cont).
    pieces = textwrap.wrap(body, width=max(cols, 8),
                           initial_indent=" " * len(prefix),
                           subsequent_indent=cont,
                           break_long_words=True) or [" " * len(prefix)]

    rows = []
    for i, piece in enumerate(pieces):
        if i == 0:
            piece = piece[len(prefix):]
            segs = [(pcol, prefix)] if prefix else []
            # Tool name renders blue, its arguments in body text.
            name = line.get("tool", "Tool")
            if kind == "tool" and piece.startswith(name):
                segs.append(("tool", name))
                segs.append(("text", piece[len(name):]))
            else:
                segs.append((bcol, piece))
        else:
            segs = [(bcol, piece)]
        rows.append(clip_row(segs, cols))
    return rows


def wrap_and_clip(lines, cols, rows):
    """Expand every line, then keep the tail like a terminal.

    Bottom-anchored on purpose: a narrow pane does not show less content, it
    shows the *same* content pushed off the top by wrapping. That is the effect
    under test, and the red +N counter reports it.
    """
    cols = max(cols, 6)
    out = []
    for line in lines:
        out.extend(expand(line, cols))
    return (out[-rows:] if rows > 0 else []), len(out)


def render(key, cfg, distance, arcmin, sessions, png=False):
    label, diag, aw, ah, pw, ph, gc, gr, tier, dist_override = cfg
    distance = dist_override or distance
    w_mm, h_mm, px_per_mm, ppi = panel_geometry(diag, aw, ah, pw, ph)
    cw, ch, em = cell_mm(HACK, arcmin, distance)

    chrome_mm = WINDOW_CHROME_PX / px_per_mm
    pane_w = w_mm / gc
    pane_h = (h_mm - chrome_mm) / gr

    p_cols = int(pane_w / cw) - 1
    p_rows = int(pane_h / ch) - 1
    want = TIERS[tier]
    ok = p_cols >= want["cols"] and p_rows >= want["rows"]

    pad, head = 26.0, 34.0
    W, H = w_mm + pad * 2, h_mm + pad * 2 + head

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.1f}mm" '
         f'height="{H:.1f}mm" viewBox="0 0 {W:.1f} {H:.1f}">',
         f'<rect width="{W:.1f}" height="{H:.1f}" fill="{PALETTE["paper"]}"/>']

    def text(x, y, t, size, fill, weight="normal", anchor="start",
             family="Hack, monospace"):
        s.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}" '
                 f'font-size="{size:.3f}" fill="{fill}" font-weight="{weight}" '
                 f'text-anchor="{anchor}" xml:space="preserve">{esc(t)}</text>')

    sans = "DejaVu Sans, sans-serif"
    text(pad, 13, label, 5.2, PALETTE["ink"], weight="bold", family=sans)
    text(W - pad, 13, "READABLE" if ok else "TOO SMALL", 5.2,
         "#0a7a2f" if ok else "#b00020", weight="bold", anchor="end", family=sans)
    text(pad, 21,
         f"{pw}x{ph} · {ppi:.0f} PPI · {w_mm:.0f}x{h_mm:.0f} mm · {gc}x{gr} panes · "
         f"{p_cols}x{p_rows} cells per pane (target {want['cols']}x{want['rows']}, "
         f"tier '{tier}') · Hack {em * px_per_mm * 72 / 96:.1f}pt",
         3.5, "#444444", family=sans)
    text(pad, 28,
         f"Character height {arcmin:.1f}' at {distance:.0f} mm. "
         f"ISO 9241-303: 16' floor, 20-22' target.", 3.5, "#444444", family=sans)

    ox, oy = pad, pad + head
    s.append(f'<rect x="{ox:.2f}" y="{oy:.2f}" width="{w_mm:.2f}" '
             f'height="{h_mm:.2f}" fill="{PALETTE["bg"]}" rx="2"/>')
    s.append(f'<rect x="{ox:.2f}" y="{oy:.2f}" width="{w_mm:.2f}" '
             f'height="{chrome_mm:.2f}" fill="{PALETTE["titlebar"]}"/>')
    text(ox + 2, oy + chrome_mm * 0.62, "github : bash — Konsole",
         min(chrome_mm * 0.42, 4.0), PALETTE["dim"])

    gy = oy + chrome_mm
    fs = ch / HACK["line_em"]

    for r in range(gr):
        for c in range(gc):
            i = r * gc + c
            sess = sessions[i % len(sessions)]
            state = sess.get("state", "working")
            x, y = ox + c * pane_w, gy + r * pane_h

            s.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{pane_w:.2f}" '
                     f'height="{pane_h:.2f}" fill="{PALETTE["pane"]}" '
                     f'stroke="{STATE_COLOUR.get(state, PALETTE["border"])}" '
                     f'stroke-width="{0.5 if state == "blocked" else 0.25}"/>')

            visible, total = wrap_and_clip(sess["lines"] + INPUT_BOX,
                                           p_cols, p_rows)
            overflow = total - p_rows

            glyph = STATE_GLYPH.get(state, "")
            title = (glyph + " " if glyph else "") + sess["title"]
            # Leave room for the overflow counter so the two cannot collide.
            title_room = max(p_cols - (len(str(overflow)) + 3 if overflow > 0 else 0), 4)
            text(x + cw * 0.5, y + ch * 0.8, title[:title_room], fs,
                 STATE_COLOUR.get(state) if state in ("blocked", "done")
                 else PALETTE["dim"])

            # Clip to the pane: a wrapping bug should show up as truncation
            # inside the pane, never as text spilling into its neighbour.
            cid = f"pane{r}_{c}"
            s.append(f'<clipPath id="{cid}"><rect x="{x:.2f}" y="{y:.2f}" '
                     f'width="{pane_w:.2f}" height="{pane_h:.2f}"/></clipPath>')
            s.append(f'<g clip-path="url(#{cid})">')
            base = y + pane_h - ch * 0.35
            for j, segs in enumerate(reversed(visible)):
                yy = base - ch * j
                xx = x + cw * 0.5
                for colour, chunk in segs:
                    if chunk:
                        text(xx, yy, chunk, fs, PALETTE[colour],
                             weight="bold" if colour == "tool" else "normal")
                        xx += len(chunk) * cw
            s.append("</g>")

            if overflow > 0:
                text(x + pane_w - cw * 0.5, y + ch * 0.8, f"+{overflow}↑",
                     fs * 0.9, PALETTE["alert"], anchor="end")

    k = (297.0 - 20) / W
    text(pad, H - 12, f"Printed at 100% scale, view from {distance:.0f} mm.",
         3.6, PALETTE["ink"], family=sans)
    text(pad, H - 6.5,
         f"Printed to fit A4 landscape (x{k:.3f}), view from {distance * k:.0f} mm — "
         f"scaling by k and viewing at k x distance preserves angular size exactly.",
         3.6, "#444444", family=sans)
    text(W - pad, H - 6.5, "red +N↑ = lines pushed off the top by wrapping",
         3.6, "#b00020", anchor="end", family=sans)

    s.append("</svg>")
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{key}.svg")
    with open(path, "w") as f:
        f.write("\n".join(s))

    if png:
        subprocess.run(["inkscape", path, "--export-type=png", "--export-dpi=110",
                        f"--export-filename={path[:-4]}.png"],
                       check=False, capture_output=True)
    return {"key": key, "cells": (p_cols, p_rows),
            "target": (want["cols"], want["rows"]), "ok": ok}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", action="append", choices=list(CONFIGS))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--distance", type=float, default=700.0)
    ap.add_argument("--arcmin", type=float, default=ANGULAR["current"])
    ap.add_argument("--png", action="store_true")
    args = ap.parse_args()

    if args.list:
        for k, v in CONFIGS.items():
            print(f"{k:<24} {v[0]}")
        return

    sessions = load_sessions()
    keys = list(CONFIGS) if args.all else (args.config or ["8x1-32in-4k-observed"])
    print(f"{'config':<24} {'per-pane cells':>15} {'target':>10} {'verdict':>10}")
    for k in keys:
        r = render(k, CONFIGS[k], args.distance, args.arcmin, sessions, args.png)
        print(f"{r['key']:<24} {r['cells'][0]:6d}x{r['cells'][1]:<8d} "
              f"{r['target'][0]:4d}x{r['target'][1]:<5d} "
              f"{'READABLE' if r['ok'] else 'TOO SMALL':>10}")


if __name__ == "__main__":
    main()
