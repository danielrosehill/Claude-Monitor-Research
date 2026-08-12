# Readability geometry

The model that turns "I want 8 Claude sessions on screen" into a panel
specification. Implemented in [`../scripts/geometry.py`](../scripts/geometry.py).

Nothing here is monitor-specific until the final step. The chain runs:

```
angular target (arcmin)              <- ergonomics standard, or measured tolerance
  -> physical cap height at distance D (mm)
  -> physical cell size (mm)         <- font metrics
  -> physical grid size (mm)         <- pane tier x layout
  -> required diagonal + aspect ratio
  -> required resolution at a given pixel density
```

Change the font or the viewing distance and the whole answer re-derives. That is
the point of keeping it as a script rather than a table.

---

## Inputs, and how each was obtained

### Font metrics — measured

Read from `/usr/share/fonts/truetype/hack/Hack-Regular.ttf` with `fontTools` on
2026-08-12. `unitsPerEm = 2048`.

| Metric | Value | Ratio to em |
|---|---|---|
| Cap height (`OS/2.sCapHeight`) | 1493 | **0.7290** |
| x-height (`OS/2.sxHeight`) | 1120 | 0.5469 |
| Advance width (`hmtx['A']`) | 1233 | **0.6021** |
| hhea line height | 2384 | 1.1641 |

**The font's line height is not used.** Konsole lays out Hack 14 at **22.0 px**,
against an em of 18.667 px (14 pt at 96 DPI logical) — a ratio of **1.1786**, not
the font's 1.1641. The measured value is what the model uses, because the pixel
that matters is the one Konsole draws.

That 22.0 px was measured off
[`../evidence/konsole-4-pane-1920x1080-2026-08-12.png`](../evidence/konsole-4-pane-1920x1080-2026-08-12.png):
14 line gaps spanning 308 px in the `lsrecent` output.

Cross-check: the derived advance of 0.6021 × 18.667 = **11.24 px** matches the
character pitch measured off the same screenshot to within a rounding error.

### Panel baseline — measured

From `xrandr`:

```
eDP-1 connected primary 1920x1080+0+0  344mm x 193mm
```

- 344 × 193 mm is a **396 mm / 15.6″** diagonal, not the 14″ initially assumed.
- Density: 1920 ÷ 344 mm = 5.581 px/mm = **141.8 PPI**.
- Hack 14 cap height = 0.7290 × 18.667 px = 13.61 px = **2.44 mm**.

### Angular target — ISO 9241-303:2011

The readability/legibility clause of ISO 9241-303 sets the minimum height of
Latin characters at **16 arc-minutes**, and requires the display to be *capable*
of **20–22 arc-minutes**. ISO 9241-306 ties the 20–22′ range to the 400–750 mm
viewing distances users actually prefer at a desk.

An arc-minute is angular, so the physical requirement scales linearly with
viewing distance. This is the single most consequential fact in the model.

Where the current setup lands:

| Distance | Angular cap height | Verdict |
|---|---|---|
| 450 mm | 18.6′ | above floor, below target |
| **500 mm** *(typical laptop)* | **16.8′** | **0.8′ above the ISO floor** |
| 550 mm | 15.2′ | **below the ISO floor** |
| 600 mm | 14.0′ | below the floor |
| 700 mm | 12.0′ | far below the floor |

Two readings of this, both used in the model:

- **16.8′** — the demonstrated tolerance. Not comfortable, but proven in daily use,
  so it is the aggressive bound.
- **20–22′** — what the standard actually asks for, and the honest bound for a
  display bought deliberately for long sessions.

### Pane tiers — one measured, three assumed

How many cells one Claude Code session needs.

| Tier | Cells | Source | What it buys |
|---|---|---|---|
| `observed` | **26 × 39** | **measured 2026-08-12** | What is actually in daily use in a 1×6 split. See below. |
| `glanceable` | 60 × 18 | assumed | Spinner, current action line, and whether it is asking a question. Monitoring only. |
| `working` | 80 × 30 | assumed | The 80-column norm Claude Code's output is laid out against, plus enough rows for one complete tool call above the input box. |
| `review` | 100 × 45 | assumed | A diff hunk with context, unwrapped. What the pane you are actively driving needs. |

Plus **1 column and 1 row per pane** for Konsole's divider and pane title bar, and
**168 px** of window chrome (title bar, menu, toolbar, tab bar) measured off the
baseline screenshot — or **192 px** with `--fullscreen`, which is the maximised
figure and adds the Plasma taskbar.

The three assumed tiers remain judgement calls and are still the input most likely
to be wrong. The `observed` tier is not, and it shows the guesses were wrong in
shape, not just in magnitude — see the next section.

---

## Measured layouts

The model above was derived before any of it had been checked against a real
multi-pane window. This section is that check.

### The 1×6 split, measured 2026-08-12

Six concurrent Claude Code sessions, Konsole maximised on the laptop panel
(1920×1080, eDP-1, Hack 14). Captured in
[`../evidence/konsole-6-pane-1920x1080-2026-08-12.png`](../evidence/konsole-6-pane-1920x1080-2026-08-12.png),
raw figures in
[`../data/observed-6pane-thinkpad-2026-08-12.json`](../data/observed-6pane-thinkpad-2026-08-12.json).

| Pane | Session | Cells | Width |
|---|---|---|---|
| 1 | `book-blueprint` | 26 × 39 | 313 px |
| 2 | `Sensory-Notebook` | 26 × 39 | 320 px |
| 3 | `github` | 26 × 39 | 320 px |
| 4 | `Claude-Monitor-Research` | 27 × 39 | 336 px |
| 5 | `book-episode-index` | 25 × 39 | 305 px |
| 6 | `github` | 26 × 39 | 326 px |

**156 content columns and 39 rows across the panel.** The one-column spread
between panes is splitter slack, not intent: Konsole sizes panes in pixels and
each takes `floor((width − overhead) / advance)` columns.

Two results matter more than the numbers themselves.

**1. The model is correct.** Run at this panel and 500 mm, `geometry.py` predicts
**171 usable columns and 40 rows**. The measurement accounts for
156 content columns + 156 px of per-pane overhead (13.9 columns) = **169.9**, and
39 content rows + 1 title strip = **40**. That is **0.6% error on columns and
exact on rows**, which promotes the whole chain from derived arithmetic to
validated arithmetic.

**2. The pane tiers were the wrong shape.** A real pane in daily use is
**26 × 39**: 43% of the width the `glanceable` tier assumed, and 217% of its
height. The guess was not merely mis-sized, it was mis-proportioned — because it
imagined a grid of short wide panes, and what actually gets used is a row of tall
narrow ones. Splitting vertically hands every pane the full panel height for free,
so nobody ever chooses a short pane.

### Per-pane overhead is 2.3 columns, not 1

The model charges 1 column per pane for the divider. Measured, a pane costs
**15 px of scrollbar + 11 px of splitter handle = 26 px**, which at an 11.24 px
advance is **≈2.3 columns**. Across six panes that is 156 px — **8.1% of the panel
width** gone before a character is drawn.

Vertically, of 1080 px:

| Region | px | |
|---|---|---|
| Window chrome (title, menu, toolbar, tab bar) | 136 | |
| Pane title strip | 29 | once per row of panes |
| **Terminal content** | **858** | 39 rows × 22.0 px — **79.4% of the panel** |
| Bottom margin | 16 | |
| Plasma taskbar | 40 | |

The 22.0 px line pitch assumed throughout the model falls straight out of this:
858 ÷ 39 = 22.0 exactly, independently confirming the figure originally measured
off the 4-pane capture.

### Measuring a live layout

Worth writing down, because the obvious approaches fail on this machine.

**Do not estimate the grid off a screenshot.** Ask the pty. Konsole exposes every
session on D-Bus, and each session's shell has a tty whose size the kernel will
report exactly:

```bash
SVC=org.kde.konsole-$(pgrep -x konsole)
for s in $(qdbus6 $SVC | grep -E '^/Sessions/[0-9]+$'); do
  pid=$(qdbus6 $SVC $s org.kde.konsole.Session.processId)
  tty=$(ps -o tty= -p "$pid" | tr -d ' ')
  echo "$(qdbus6 $SVC $s org.kde.konsole.Session.title 1)  $(stty -F /dev/$tty size)"
done   # prints "<title>  <rows> <cols>" per pane
```

`stty size` prints **rows then columns** — the opposite order to everything else
here. There is no `Session.size()` method on the D-Bus interface; the tty is the
only authoritative source.

Things that do **not** work, and why:

- **`xdotool` / `xwininfo`** return `There are no windows in the stack`. The
  session is Wayland (`XDG_SESSION_TYPE=wayland`) and Konsole is a native Wayland
  client, so it never appears in the X11 window stack. Misleading, because
  `xrandr` *does* still work — it reports through XWayland — so the first tool you
  reach for succeeds and the second silently returns nothing.
- **`loginctl show-session … -p Type`** reports `unspecified`. Use the
  `XDG_SESSION_TYPE` environment variable instead.
- **Reading `$COLUMNS`/`tput cols` from a tool-invoked shell** reports 80, the
  default for a process with no controlling terminal. It is not the pane's width.

Screenshots do work, via `spectacle -b -n -f -o <path>` (background, no
notification, fullscreen). Pixel bounds can then be recovered by scanning each
column for uniformity down the pane body: dividers, scrollbar troughs and margins
are constant in *y*, and text is not.

---

## Step 1 — cell size required, by target and distance

At **700 mm** (desk monitor):

| Target | Cap height | Cell (w × h) | Hack size at 140 PPI |
|---|---|---|---|
| 16.8′ | 3.42 mm | 2.83 × 5.53 mm | 19.4 pt |
| 20.0′ | 4.07 mm | 3.36 × 6.58 mm | 23.1 pt |
| 22.0′ | 4.48 mm | 3.70 × 7.24 mm | 25.4 pt |

Compare the current laptop cell: **2.01 × 3.94 mm**. Moving the same legibility to
arm's length inflates every cell by **1.4×** on each axis — **1.96× the area per
character** before a single pane is added.

## Step 2 — the panel 8 working panes implies

8 panes at 80×30, ignoring what is on the market:

| Target | Layout | Cells | Physical | Diagonal | Aspect | Resolution @140 PPI |
|---|---|---|---|---|---|---|
| 16.8′ | **4 × 2** | 324 × 62 | 915 × 373 mm | **38.9″** | **22.1:9** | 5045 × 2058 |
| 16.8′ | 2 × 4 | 162 × 124 | 458 × 716 mm | 33.5″ | 5.8:9 | 2523 × 3948 |
| 20.0′ | 4 × 2 | 324 × 62 | 1090 × 439 mm | 46.2″ | 22.4:9 | 6006 × 2418 |
| 20.0′ | 2 × 4 | 162 × 124 | 545 × 847 mm | 39.6″ | 5.8:9 | 3003 × 4668 |
| 22.0′ | 4 × 2 | 324 × 62 | 1199 × 480 mm | 50.8″ | 22.5:9 | 6607 × 2643 |
| 22.0′ | 2 × 4 | 162 × 124 | 599 × 929 mm | 43.5″ | 5.8:9 | 3303 × 5118 |

`8 × 1` and `1 × 8` are computed but omitted: a single row of eight working panes
needs **648 columns**, which is wider than any panel at any legible size.

**The 4×2 aspect ratio is stable at ≈22:9 (2.45:1) across every legibility target**
— raising the target scales the panel but does not reshape it. The shape is a
property of the layout, not of the ergonomics.

## Step 3 — composite layouts

One pane at `review`, the rest at `glanceable`, at 16.8′ / 700 mm:

| Layout | Panes | Cells | Physical | Diagonal | Aspect |
|---|---|---|---|---|---|
| 1 review + **2×3** glanceable | **7** | 223 × 57 | 630 × 346 mm | 28.3″ | **16.4:9** |
| 1 review + 2×4 glanceable | 9 | 223 × 76 | 630 × 451 mm | 30.5″ | 12.6:9 |
| 1 review + 1×8 glanceable | 9 | 162 × 152 | 458 × 871 mm | 38.7″ | 4.7:9 |

The 7-pane composite lands on **16.4:9 — within 3% of standard 16:9**, at a
diagonal a 32″ 4K comfortably exceeds. The 9-pane version is 1.4:1, which is not a
shape monitors come in.

That discontinuity between 7 and 9 panes is the most actionable output of the whole
model, and it is a *software* result as much as a hardware one: it says the
cheapest way to get to 8+ sessions is to stop trying to make them all readable
simultaneously.

## Step 4 — re-scoring the market against the observed tier

Steps 2 and 3 asked what panel eight *working* (80×30) panes need in a **4×2**
grid. The measured layout uses a different tier and a different arrangement, so
the market question is worth asking again on the terms actually in use: eight
panes at **26×39** in a **single row**, 700 mm, 16.8′.

```
python3 scripts/geometry.py --tier observed --panes 8 --layout 8x1 --fullscreen
```

| Panel | Usable grid | Fits 216×40? | Panes at this tier |
|---|---|---|---|
| 24″ 16:9 FHD | 186 × 44 | no — horizontal | 6 |
| 27″ 16:9 QHD | 211 × 52 | no — horizontal | 7 |
| 27″ 16:9 4K | 211 × 55 | no — horizontal | 7 |
| **32″ 16:9 4K** | 250 × 65 | **yes** | **9** |
| 34″ 21:9 UWQHD | 280 × 52 | yes | 10 |
| **40″ 21:9 5K2K** | 328 × 64 | **yes** | **12** |
| **49″ 32:9 DQHD** | 424 × 52 | **yes** | **15** |
| 57″ 32:9 Dual-4K | 493 × 64 | yes | 18 |
| 42″ 16:9 4K | 329 × 86 | yes | 24 |

**The 49″ 32:9 now passes.** It was the one large panel the working-tier analysis
singled out as failing, and it failed on rows: 8 working panes in 4×2 need 62
rows, and DQHD's 1440 px only yields ~52.

Nothing about the panel changed. The *layout* changed. A 4×2 grid needs two panes'
worth of rows stacked; a 1×N row needs one. Once the arrangement is a single row,
**the row requirement stops scaling with pane count entirely** — it is fixed at
whatever one pane needs — and width becomes the only axis that buys panes. That is
precisely the axis 32:9 sells.

So the README's "super-ultrawides solve the wrong axis" conclusion is real but
**conditional on the 4×2 grid**, and 4×2 is not what gets used. Under the observed
layout the conclusion inverts: 32:9 is the *best* value of any shape listed, at 15
panes.

Two honest caveats before this is treated as a buying signal:

1. **26 columns is a tolerance, not a preference.** It is what six panes on a
   1920×1080 panel forces, not what was chosen. A 49″ DQHD could equally be spent
   on 7 panes at 60 columns or 5 at 80 — the "15 panes" figure only holds if 26
   columns is genuinely acceptable at 700 mm, and it is currently only proven
   acceptable at 500 mm.
2. **A 1×N row of panes has a viewing-angle cost the model does not price.** At
   1218 mm wide, the outermost pane of a 49″ panel is well off-axis at 700 mm.
   Every figure here assumes head-on viewing.

---

## Reproducing

```bash
python3 scripts/geometry.py                              # working tier, 8 panes, 700 mm
python3 scripts/geometry.py --tier glanceable
python3 scripts/geometry.py --distance 600 --arcmin 20
python3 scripts/geometry.py --layout 4x2 --json          # machine-readable

# The measured tier and the layout actually in use
python3 scripts/geometry.py --tier observed --panes 8 --layout 8x1 --fullscreen

# Reproduce the validation: should report the laptop fitting 6 panes at 171x40
python3 scripts/geometry.py --tier observed --panes 6 --layout 6x1 \
        --distance 500 --arcmin 16.8 --fullscreen
```

Checked-in output lives in [`../data/`](../data/) so changes to the model show up
as a reviewable diff rather than having to be re-run to be noticed.

## Known weaknesses

1. **Three of the four pane tiers are still guesses.** `observed` (26×39) is
   measured, and it showed `glanceable` was wrong in both directions at once.
   `working` (80×30) and `review` (100×45) remain reasoned rather than measured,
   and every Step 2 and Step 3 figure rests on them. If Claude Code's real working
   floor is 100 columns, those panel figures grow ~25%.
2. **26 columns is a proven tolerance at 500 mm only.** It is what six panes on a
   1920×1080 panel forces, not a preference expressed. Whether it stays legible
   and useful at 700 mm on a bought panel is untested, and Step 4's pane counts
   depend entirely on it.
3. **Viewing angle is not modelled.** Every figure assumes the whole panel is
   viewed head-on. For a 1×N row on a 49″ panel that is plainly false for the
   outer panes, and it is the main thing arguing against the Step 4 conclusion.
4. **Bezels ignored.** Physical sizes are active area only.
5. **Single font.** Everything assumes Hack. A narrower monospace changes the
   column arithmetic but not the row arithmetic. Under the 4×2 grid that made the
   conclusions robust to font choice, because rows were binding — but Step 4 shows
   that under a 1×N row it is *columns* that bind, so for the observed layout the
   font choice now matters directly and a narrower face buys panes.
6. **Konsole-specific chrome.** The 168/192 px window overhead, the 26 px per-pane
   scrollbar-plus-splitter and the pane title row are Konsole's. A different
   multiplexer changes these by a few percent — though tmux, with no scrollbars
   and 1 px dividers, would recover most of the 8.1% width overhead measured here.
7. **No scaling-factor modelling.** Assumes 100% scaling with font size varied
   directly, which is how Konsole is actually configured here.

## Sources

- [ISO 9241-303:2011 — Requirements for electronic visual displays](https://www.iso.org/standard/57992.html) ([preview PDF](https://cdn.standards.iteh.ai/samples/57992/bddfd91165b444f6b9815a6993feadc5/ISO-9241-303-2011.pdf))
- [ISO 9241-306 preview — viewing distance and character height](https://www.sis.se/api/document/preview/80005893/)
- [Userfocus summary of ISO 9241 Part 3 visual display requirements](https://www.userfocus.co.uk/resources/iso9241/part3.html)
