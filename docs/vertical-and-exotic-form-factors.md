# Horizontal vs vertical vs square

The recurring question, answered with the numbers this repo generated rather than
with taste. Short version:

> **For one tall thing, vertical wins. For many things at once, horizontal wins.
> Square wins nothing.** The reason is the same in all three cases: the rectangle
> of comfortable gaze is much wider than it is tall, so a panel's job is to tile
> that rectangle, and a vertical panel is a bet that you want *one* tall window
> rather than *several* windows.

---

## The fact everything follows from

Comfortable gaze at 700 mm — eye rotation only, no head movement
([`../scripts/ergonomics.py`](../scripts/ergonomics.py)):

```
horizontal   +/- 30 deg          ->  808 mm
vertical     +5 to -30 deg       ->  465 mm
                                     ------------
                                     1.74 : 1
```

**The vertical budget is not symmetric, and that is the whole story.** You get 30°
downward and only about 5° upward, because looking up loads the neck extensors and
exposes more of the eye surface. Horizontally you get 30° *each way*. So the
usable rectangle is 1.74× wider than tall before any monitor enters the room.

16:9 is 1.78:1. That is not a coincidence worth being cynical about — it is
roughly the shape of the field of view people are willing to use, which is why the
industry converged there.

---

## Horizontal

**What it gets right:** it matches the comfort rectangle, so nearly all of the
panel is reachable by eye alone.

| Panel | Coverage of the panel inside comfortable gaze |
|---|---|
| 24″ 16:9 | 100% |
| 27″ 16:9 | 100% |
| **32″ 16:9** | **100%** |
| 42″ 16:9 | 67% |
| 48″ 16:9 | 51% |

A 32″ 16:9 (697 × 392 mm) is the **largest panel of any shape that fits entirely
inside comfortable gaze at 700 mm**. Past that you are buying screen you must turn
your head to read.

**Where it stops:** beyond ~32″ a 16:9 panel grows in both axes at once, so it
overflows the short vertical budget as well as the long horizontal one. A 48″ is
598 mm tall against a 465 mm budget. This is why the answer is not "buy the
biggest 16:9".

### Ultrawide is horizontal past the point of usefulness

21:9 and 32:9 extend the axis that was already the longer one, and they extend it
past 808 mm:

| Panel | Width | Overflow beyond comfort | Comfortable panes / total |
|---|---|---|---|
| 40″ 21:9 | 927 mm | 119 mm | 12 / 16 |
| 49″ 32:9 | 1198 mm | **390 mm** | 7 / 10 |
| 57″ 32:9 | 1394 mm | **585 mm** | 14 / 24 |

The 40″ 21:9 delivers **exactly the same 12 comfortable panes as a 32″ 4K at
double the price** — the extra width lands outside the cone. And the 49″ 32:9 is
the worst panel scored: 1440 px of height holds only one row of panes, so it
cannot form a grid at all.

---

## Vertical

Two genuinely different things, routinely conflated:

| | What it is | Penalty |
|---|---|---|
| **Rotated** | A landscape panel turned 90° | Breaks subpixel text rendering |
| **Vertical-native** | Panel manufactured taller than wide, or sold and warranted for vertical installation | None of the above, but the affordable options are low-PPI |

### Rotated panels have a specific, verifiable text penalty

ClearType and FreeType's LCD filtering both assume **horizontal RGB stripes**.
Rotate the panel and the stripes become vertical, so the subpixel maths no longer
matches the hardware and text picks up colour fringing.

Verified on this machine, 2026-08-12:

```
$ fc-match --verbose Hack | grep rgba
        rgba: 1(i)(w)          # 1 = FC_RGBA_RGB, horizontal stripe
```

Nothing anywhere sets `vrgb` or `vbgr`, and **fontconfig has no per-display
subpixel order** — so a desk mixing a rotated panel with an unrotated one cannot
have correct subpixel rendering on both at once. Windows is worse: it has no
per-monitor setting at all. The practical fix is to drop that display to grayscale
antialiasing, which means giving up subpixel rendering rather than fixing it.

For a use case that is *entirely text*, that is not a rounding error.

### And the trade was poor even before that

Same panel, with and without rotation, both rendered at true scale:

| 32″ 4K | Panes | Cells/pane |
|---|---|---|
| landscape | 8 | 30 × 65 |
| rotated | 10 | 26 × 59 |

**Two extra panes, four fewer columns each.** Columns are the scarce axis; rows
already have a surplus.

### Does anybody make a vertical-native monitor?

Almost nobody, and that is informative rather than an oversight. What exists:

| Product | Form | Status | ~USD |
|---|---|---|---|
| Commercial portrait-only signage | native 1080×1920, 24/7 rated, VESA rated vertical | current, niche | ~380 |
| **LG DualUp 28MQ780** | 16:18, 2560×2880 — natively taller than wide | current | 697 |
| Mobile Pixels Geminos | two 24″ stacked as one designed unit | current | 640–1000 |
| UPERFECT Y | 15.6″ portable, vertical-first stand | current | ~200 |

The LG DualUp is the only mainstream desktop panel that is genuinely taller than
wide by design. Every other "vertical monitor" on sale is a landscape panel with a
pivot stand.

**The catch for this use case:** the affordable native option is a signage panel at
**70 PPI**, which draws Hack at a 7.8 px advance against the laptop's 11.2 — the
coarsest glyph rendering of anything scored here. See
[`../wireframes/5x2-32in-signage-vertical.png`](../wireframes/5x2-32in-signage-vertical.png).

### Why vertical loses *for a grid*, having won its reputation elsewhere

Vertical monitors earned their reputation on **one long thing**: a code file, a
log, a document, a chat. That reputation is deserved and this analysis does not
contradict it.

A grid of terminals is not one long thing. It tiles. And tiling into a rectangle
that is 1.74:1 wants width. Measured across every vertical and square
configuration rendered:

| Configuration | Cells per pane |
|---|---|
| 24″ rotated | 33 × 42 |
| 27″ 4K rotated | 28 × 50 |
| 32″ 4K rotated | 26 × 59 |
| 32″ vertical-native signage | 26 × 56 |
| LG DualUp 16:18 | 26 × 43 |
| **26.5″ 1:1 square** | **27 × 77** |

Every one produces panes **far taller than a session needs and narrower than one
wants**. Against these, the median simulated session needs **19 rows at 40 columns**
and 25 rows at 26 columns. Vertical form factors deliver surplus on the axis that
was already in surplus, and take it from the axis that was already short.

---

## Square

The intuition is good: an even grid should want an even panel. The arithmetic
disagrees, for a reason worth knowing.

**A grid does not want a square panel. It wants a panel shaped like the pane,
multiplied by the grid.** And a comfortable Claude Code pane at 40 × 31 cells is
**229 × 171 mm — about 4:3**, not square. So even a perfect 3 × 3 grid of them is
687 × 513 mm ≈ **1.34:1**, and the best packing into the comfort rectangle is
wider still:

```
comfort rectangle       808 x 465 mm
pane at 40x31 cells     229 x 171 mm
best fit                4 across x 3 down     ->  916 x 513 mm  =  1.79:1
```

**1.79:1 is 16:9.** The grid argument, followed honestly, arrives back at a
landscape 16:9 panel.

A 26.5″ 1:1 square (476 × 476 mm) manages 85% coverage — respectable — but it does
so by being **simultaneously too tall and too narrow**: it overflows the 465 mm
vertical budget while leaving 332 mm of horizontal comfort completely unused. It
loses on both axes at once, which is the characteristic failure of a compromise
shape.

And the category is effectively dead. The Eizo FlexScan EV2730Q (26.5″,
1920 × 1920, ~102 PPI) is the only real desktop square monitor, it is
**discontinued**, and supply is used Japanese imports.

---

## The summary table

At 700 mm, `daily` tier panes (40 × 31 cells):

| Shape | Fits the comfort rectangle? | Pane it produces | Verdict for a session grid |
|---|---|---|---|
| **16:9 landscape ≤32″** | **entirely** | balanced | **buy this** |
| 16:9 landscape 42–48″ | 51–67% | balanced | more panes, but you turn your head |
| 21:9 ultrawide | 87% | balanced | no more *comfortable* panes than a 32″, double the price |
| 32:9 super-ultrawide | 58–68% | wide, too few rows | worst of the set; cannot grid |
| Vertical (rotated) | 58–77% | too tall, too narrow | +2 panes, −4 columns, and breaks subpixel text |
| Vertical (native) | 58–77% | too tall, too narrow | honest engineering, wrong shape here, and cheap ones are 70 PPI |
| Square 1:1 | 85% | far too tall | too tall *and* too narrow at once; category discontinued |
| Bar / stretched | 100% | none — 8–23 rows | not a pane device; a status strip, one line per session |

---

## Where this could be wrong

- **The gaze angles are standard, not yours.** ±30° horizontal and +5/−30° vertical
  are documented preferred ranges from ISO 9241 and general human-factors practice.
  They are not measured for this user. Someone habituated to a 49″ ultrawide may be
  perfectly happy outside them, and for them the ultrawide rows re-enter play.
- **Pane row demand comes from simulated sessions.** The "19 rows at 40 columns"
  figure is measured off [`../fixtures/sessions.json`](../fixtures/sessions.json),
  which is hand-written to be shaped like real sessions. If real sessions are
  taller, vertical panels recover some ground.
- **One head position is assumed.** The model assumes you face the centre of the
  array. People with ultrawides turn their chairs, which is a real adaptation the
  arithmetic here does not credit.
