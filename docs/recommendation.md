# The recommendation

**32″ 16:9 4K (3840×2160, ~140 PPI), viewed at 700 mm, running 6×2 = 12 Claude
Code instances at 40×31 cells each. Absolute maximum 18. About $300–330.**

Decided 2026-08-13. Rendered at true scale in
[`../wireframes/6x2-32in-4k-RECOMMENDED.svg`](../wireframes/6x2-32in-4k-RECOMMENDED.svg).
Reproduce with:

```bash
python3 scripts/wireframe.py --config 6x2-32in-4k-RECOMMENDED --png
python3 scripts/geometry.py --tier daily --panes 12 --layout 6x2 --fullscreen
```

| | |
|---|---|
| **Size** | 32″ (31.5″ actual), 697 × 392 mm |
| **Aspect** | 16:9 |
| **Resolution** | 3840 × 2160, ~140 PPI |
| **Viewing distance** | 700 mm |
| **Layout** | 6 across × 2 down |
| **Instances** | **12** at 40 × 31 cells each |
| **Maximum** | 18 (9 × 2) at 26 × 31 |
| **Font** | Hack, ~19.4 pt at this distance (Hack 14 today at 500 mm) |
| **Price** | $300–330 street — LG 32UR500K-B, Dell S3225QS |

---

## Why each number

### Size: 32″, because it is the largest 16:9 that fits inside comfortable gaze

The comfortable gaze rectangle at 700 mm — eyes only, no head movement — is
**808 × 465 mm** ([`ergonomics.py`](../scripts/ergonomics.py), ±30° horizontal,
+5° to −30° vertical). A 32″ 16:9 is 697 × 392 mm, so **the whole panel sits
inside it**, at 86% of the comfort width and 84% of the height.

Nothing larger does:

| Panel | Coverage | Overflow |
|---|---|---|
| **32″ 16:9** | **100%** | — |
| 40″ 21:9 | 87% | 119 mm wide |
| 42″ 16:9 | 67% | 122 mm wide, 119 mm tall |
| 49″ 32:9 | 68% | 390 mm wide |
| 48″ 16:9 | 51% | 254 mm wide, 194 mm tall |
| 57″ 32:9 | 58% | 585 mm wide |

A pane you have to turn your head to read is not a monitored session. It is a
session you will stop checking. That is why the metric throughout this repo is
*comfortable* panes, not total panes.

### Aspect: 16:9, because that is what the eye's comfort rectangle already is

The comfort rectangle is **1.74:1**. 16:9 is **1.78:1** — the closest match of any
shipping aspect ratio. This is not a defence of convention; it fell out of the
ergonomic arithmetic and was mildly surprising.

Ultrawide sells pixels outside the cone. The 49″ 32:9 is the clearest case: it has
the highest raw pane count of anything scored (15), but **5 of them fall outside
comfortable gaze**, and its 1440 px height holds exactly one row of panes, so it
cannot form a grid at all. It fails the `daily` tier on rows — 52 available
against 64 needed.

### Resolution: 4K, because 140 PPI means nothing has to be re-tuned

The laptop is 141 PPI. A 32″ 4K is ~140. That matters twice:

- **The font profile ports over unchanged.** Same pixel metrics, only the point
  size changes to hold 16.8′ at the greater distance.
- **Glyphs get better, not worse.** At 700 mm a 140 PPI panel draws Hack at a
  15.6 px advance against the laptop's 11.2 — **139%** of today's pixel count per
  character.

### Instances: 12, because a single row wastes rows

This was the non-obvious part. Putting all panes in one row on this panel gives
**63 rows per pane**. Measured against the simulated sessions in
[`../fixtures/sessions.json`](../fixtures/sessions.json), the *median* session
needs **19 rows at 40 columns**. Sixty-three is not headroom, it is waste.

Spending that surplus on a second row doubles the instance count at a *wider*
pane:

| Layout | Instances | Cells/pane | Notes |
|---|---|---|---|
| 7 × 1 | 7 | 34 × 64 | roomier than today on both axes, but only 7 |
| 8 × 1 | 8 | 29 × 63 | 34 rows/pane never used |
| **6 × 2** | **12** | **40 × 31** | **the recommendation** |
| 9 × 1 | 9 | 26 × 63 | today's width, half the height wasted |
| 9 × 2 | 18 | 26 × 31 | the maximum |

**40 columns is 54% wider than the 26 in daily use today**, and columns are the
scarce axis — 26 is a tolerance a 1920×1080 panel forced, never a preference.

Row demand by pane width, from the fixtures:

| Pane width | Median rows needed | Longest session |
|---|---|---|
| 26 cols | 25 | 54 |
| 34 cols | 21 | 40 |
| **40 cols** | **19** | **37** |
| 48 cols | 17 | 32 |
| 60 cols | 15 | 28 |

At 40 × 31 only the longest session exceeds the pane, by 7 lines, and terminals
scroll. The render confirms it: eleven panes clean, one showing `+7↑`.

---

## What not to buy

**Do not rotate a panel to vertical.** It breaks subpixel text rendering — ClearType
and FreeType LCD filtering both assume horizontal RGB stripes. Verified on this
machine: `fc-match` reports `rgba: 1`, nothing anywhere sets `vrgb`, and fontconfig
has no per-display subpixel order, so a desk mixing rotated and unrotated panels
cannot have both correct. And the trade is poor anyway — rotating a 32″ 4K buys
**2 extra panes and costs 4 columns each** (8 at 30×65 landscape → 10 at 26×59
rotated).

**Do not buy the 49″ 32:9.** Best raw pane count, wrong axis. See above.

**Do not buy Dell's 40″ U4025QW at $2,250.** Identical 5120×2160 and ~140 PPI to
the $620 INNOCN 40C1U, and identical 8 working panes. The premium buys Thunderbolt
4, a KVM and 120 Hz — no additional panes.

**Vertical-native panels are a real category but not the answer here.** Genuinely
vertical-first products exist (portrait-only commercial signage, the LG DualUp
28MQ780 at 16:18, the Mobile Pixels Geminos), and they avoid the rotation penalty
honestly. But every vertical and square configuration produces panes far taller
than a session needs and narrower than one wants — the 1:1 square is the extreme at
27 × 77 — and the affordable native option is a 70 PPI signage panel, the coarsest
glyph rendering of anything scored. See
[`vertical-and-exotic-form-factors.md`](vertical-and-exotic-form-factors.md).

---

## What this recommendation rests on, and where it is weakest

Ranked by how much damage it would do if wrong.

1. **31 rows is derived from simulated content, not real transcripts.** The row
   demand table above comes from `fixtures/sessions.json`, which is hand-written to
   be *shaped* like real sessions. If real sessions run longer, 6×2 is wrong and
   the answer moves toward 7×1 or 8×1. **This is the one worth checking**, and it
   is checkable: measure the rows real panes consume before scrolling.
2. **"Columns are the scarce axis" is well-evidenced but not measured.** It follows
   from the 26-column tolerance being panel-imposed, and from the row surplus
   above. It has not been tested by giving someone a 40-column pane and asking.
3. **The comfort rectangle uses standard human-factors angles, not your eyes.**
   ±30° horizontal and +5/−30° vertical are the documented preferred ranges. They
   are not measured for this user, and a habitual ultrawide user may be entirely
   happy outside them.
4. **Prices move.** $300–330 was US street on 2026-08-12. The recommendation is a
   panel *class*, not a SKU; any 32″ 4K IPS at ~140 PPI satisfies it.

Not a risk: the geometry itself. The model was validated against a real six-pane
layout to 0.6% on columns and exactly on rows — see finding 6 in the README.
