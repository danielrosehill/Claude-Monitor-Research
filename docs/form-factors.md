# Form factors

Existing panel classes scored against the requirement, and a specification for
what a purpose-built one would be.

Scoring is produced by [`../scripts/geometry.py`](../scripts/geometry.py). Physical
dimensions are **derived from diagonal + aspect ratio**, not quoted from spec
sheets, so they are internally consistent and exclude bezels. Model assumptions and
their weaknesses: [`readability-geometry.md`](readability-geometry.md).

**None of these have been verified in front of a physical display.** Everything
below is arithmetic.

---

## Scoring: 8 working panes (4×2, 80×30 each) at 16.8′ / 700 mm

Requirement: **324 columns × 62 rows**.

| Panel | PPI | Available grid | Fits | Limited by | Max working panes |
|---|---|---|---|---|---|
| laptop eDP-1 *(current)* | 141 | 122 × 29 | ✗ | both | 0 |
| 24″ 16:9 FHD | 93 | 186 × 45 | ✗ | both | 2 |
| 24″ 16:10 WUXGA | 94 | 182 × 50 | ✗ | both | 2 |
| 27″ 16:9 QHD | 109 | 211 × 53 | ✗ | both | 2 |
| 27″ 16:9 4K | 163 | 211 × 56 | ✗ | both | 2 |
| 32″ 16:9 4K | 138 | 250 × 66 | ✗ | horizontal | 6 |
| 34″ 21:9 UWQHD | 110 | 280 × 53 | ✗ | both | 3 |
| **49″ 32:9 DQHD** | 108 | 424 × 53 | **✗** | **vertical** | 5 |
| 42″ 16:9 4K *(OLED TV class)* | 105 | 329 × 87 | ✓ | — | 8 |
| 45″ 21:9 UWQHD | 83 | 371 × 70 | ✓ | — | 8 |
| **40″ 21:9 5K2K** | **140** | 328 × 65 | **✓** | — | **8** |
| 48″ 16:9 4K *(OLED TV class)* | 92 | 376 × 99 | ✓ | — | 12 |
| **57″ 32:9 Dual-4K** | **140** | 493 × 65 | **✓** | — | **12** |
| 32″ 4K rotated to portrait | 138 | 141 × 122 | ✗ | horizontal | 3 |

The laptop scores 0 because it is evaluated at 700 mm like everything else. At its
actual ~500 mm it manages 1 working pane, or the 4 cramped panes in the baseline
screenshot.

## What the table says

### The 32:9 super-ultrawide is the trap — only if panes are stacked

The 49″ DQHD is the **only** panel over 40″ that fails, and it is the one most
people would reach for. It has **424 columns — 100 more than needed** — and misses
on rows, 53 against 62.

Compare it to the 40″ 5K2K: identical 5120 horizontal pixels, but 2160 vertical
against 1440. The 21:9 passes and the 32:9 fails.

**A 4×2 grid of terminals is row-starved.** Every pane needs its rows for
scrollback, two stacked panes need twice as many, and rows are what 32:9
sacrifices. Buying width is buying the axis that was never short.

> **Superseded in part, 2026-08-12.** Every figure in the table above assumes the
> **4×2** grid, and the measured layout in
> [`readability-geometry.md`](readability-geometry.md#measured-layouts) is a
> **1×6 row** — nobody stacks, because a vertical split gives each pane the full
> panel height for free. In a single row the row requirement no longer scales with
> pane count, the vertical miss disappears, and this same 49″ DQHD **passes with
> the highest pane count of any shape scored** (15 at the observed 26×39 tier).
>
> The row-starvation argument is sound for the layout it assumes. It is the
> assumption, not the arithmetic, that the measurement broke. Re-score with:
>
> ```bash
> python3 ../scripts/geometry.py --tier observed --panes 8 --layout 8x1 --fullscreen
> ```

### Portrait rotation fails for the mirror reason

A rotated 32″ 4K has 122 rows — nearly double what is needed — and only 141
columns, which cannot hold even two 80-column panes side by side. Portrait is the
right instinct applied to the wrong quantity: it helps a *single* tall pane, not a
*grid*.

### Density and the font-size dividend

Panels near **140 PPI** — the 40″ 5K2K and the 57″ Dual-4K — match the laptop's
141 PPI. `Hack 14` renders at the same physical size it does now, so nothing has to
be re-tuned and both screens can share one profile.

The 42″/48″ OLED-TV options reach the pane count by being physically enormous at
92–105 PPI. They work, but text is coarser, they are TVs, and at 48″ the top corners
are outside a comfortable head-turn at 700 mm.

### The cheap answer, if the split is accepted

At the **glanceable** tier (60×18), 8 panes fits a **32″ 4K** — which also clears
the 7-pane composite (1 review + 6 glanceable) at 16.4:9. See
[`readability-geometry.md`](readability-geometry.md#step-3--composite-layouts).

---

## Specification: a purpose-built Claude grid monitor

What the requirement asks for, unconstrained by what is manufactured. Derived at
the 20′ ISO target and 700 mm — i.e. specified properly rather than at the
tolerated floor.

| Property | Spec | Why |
|---|---|---|
| **Aspect ratio** | **≈2.4:1** (22:9) | Falls out of 4×2 panes of 80×30 and is stable across every legibility target |
| **Diagonal** | 46″ at 20′, 39″ at the tolerated 16.8′ | Directly from cell size × grid |
| **Resolution** | **6000 × 2400** | 140 PPI at that diagonal |
| **Pixel density** | **140 PPI** | Matches the laptop, so font config carries over unchanged |
| **Panel height** | ≥ 440 mm active | The binding constraint; more valuable than any extra width |
| **Curvature** | Gentle, ~1500R | 1090 mm wide at 700 mm spans ~75°; the outer panes need turning towards |
| **Stand** | Height-adjustable, 100×100 VESA | Carried over from `Computer-Monitor-Purchase-0812` — eye level was non-negotiable there and still is |
| **Refresh** | 60 Hz | Irrelevant for text; do not pay for it |
| **Panel type** | IPS | Text clarity over contrast; avoid OLED subpixel fringing on small type |
| **Inputs** | 1× DisplayPort 1.4 / USB-C DP-alt | 6000×2400×60 Hz exceeds HDMI 2.0 |

Nearest thing that exists: **40″ 21:9 5K2K (5120×2160)** — 15% short on width at
the tolerated target, correct on height and density.

### The badge

Since the point of the exercise is a panel that does one job: a small Claude
sunburst on the bottom bezel, centre, where a vendor logo normally goes. Nothing
illuminated — it would sit under the lowest row of panes and compete with exactly
the thing being watched.

Etched or debossed rather than printed. If it needs power, it is in the wrong
place.

---

## Not yet costed

The travel purchase window makes this live, but no pricing has been gathered. The
40″ 5K2K class is the only realistic buy of the passing options, and it is
substantially more expensive than the 23.8″ 1080p that
`Computer-Monitor-Purchase-0812` settled on — the two decisions are not
interchangeable and should not be merged.

US retail pricing needs `geo-egress` with `egress="us"`; see the routing notes in
`~/CLAUDE.md`.
