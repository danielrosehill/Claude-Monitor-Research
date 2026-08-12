# Claude-Monitor-Research

Ergonomic and geometric research into a display **dedicated to running a grid of
concurrent Claude Code sessions** — and the software layer needed to move around
that grid quickly.

The target: **at least 8 sessions visible at once**, with no tabbing, no virtual
desktops and no window switching to see any of them.

This is a hardware *and* software problem, and the two halves constrain each other:

| Half | Question |
|---|---|
| **Hardware** | What panel — size, aspect ratio, pixel density — makes 8 legible terminal panes physically possible? |
| **Software** | Given that grid, how do you jump between sessions fast enough that 8 is useful rather than overwhelming? |

Environment assumed throughout: **KDE Plasma on Ubuntu**, Konsole, `Hack 14`.

---

## Why this is not the same as buying a monitor

The [`Computer-Monitor-Purchase-0812`](https://github.com/danielrosehill/Computer-Monitor-Purchase-0812)
research optimised for stand geometry and eye-level ergonomics, and landed on
23.8″ 1920×1080. For *this* use case that panel is the same 1920×1080 grid the
laptop already has — bigger characters, **zero additional pane capacity**.

Both conclusions are correct for their own brief. This repo exists because the
briefs are different, and this one has never been costed.

---

## Headline findings

All figures derived by [`scripts/geometry.py`](scripts/geometry.py), which is
re-runnable and takes viewing distance, font, legibility target and layout as
parameters. Full working in [`docs/readability-geometry.md`](docs/readability-geometry.md).

### 1. The current setup is already at the ergonomic floor

ISO 9241-303 sets **16 arc-minutes** as the absolute minimum character height and
**20–22′** as the range a display must be capable of. Measured on the laptop:

| | |
|---|---|
| Panel | 1920×1080, 344 × 193 mm (15.6″), **141 PPI** |
| Font | Hack 14 → cap height **2.44 mm** |
| At 500 mm viewing distance | **16.8 arc-minutes** |

That is 0.8′ above the ISO floor and **well below** the 20–22′ target. There is no
headroom to shrink text in exchange for more panes — the panes have to come from
more panel.

### 2. Distance is the hidden multiplier

A desk monitor sits further away than a laptop screen. Holding the *same* 16.8′
legibility while moving from 500 mm to 700 mm requires **1.4× larger text**, which
consumes most of a resolution upgrade before a single extra pane appears.

### 3. Eight working panes implies a shape the market barely makes

For 8 panes at 80×30 each (the "working" tier), 4×2, at 700 mm:

| Legibility target | Panel implied | Aspect | Resolution |
|---|---|---|---|
| 16.8′ *(current tolerance)* | **38.9″** | 22.1:9 (2.45:1) | 5045 × 2058 |
| 20′ *(ISO target, low)* | 46.2″ | 22.4:9 | 6006 × 2418 |
| 22′ *(ISO target, high)* | 50.8″ | 22.5:9 | 6607 × 2643 |

**≈2.45:1 with ~2000+ vertical pixels.** That is the **40″ 21:9 "5K2K"** class
(5120×2160) almost exactly — the requirement independently re-derives a product
category that exists but is rare.

### 4. Super-ultrawides solve the wrong axis — *if you stack panes*

The instinctive answer — a 49″ 32:9 — is the **only** large panel tested that
*fails*, and it fails on rows:

```
49in 32:9 DQHD (5120x1440)   424 cols x 53 rows   needs 324 x 62   FAIL: vertical
40in 21:9 5K2K (5120x2160)   328 cols x 65 rows   needs 324 x 62   PASS
```

Same width in pixels. The 21:9 wins because a **4×2 grid** of terminals is
row-starved, not column-starved, and 32:9 spends its entire budget on the axis
that was never short. Rotating a 32″ 4K to portrait fails for the mirror-image
reason: 141 columns cannot hold four pane-columns.

**This result is conditional on the 4×2 grid, and finding 6 shows 4×2 is not what
gets used.** In a single row of panes the row requirement stops scaling with pane
count — it is fixed at whatever one pane needs — and the same 49″ DQHD passes
comfortably. Read finding 6 before treating this as a buying signal.

### 5. The pagination split the geometry actually points at

Eight panes at *working* legibility needs a 39–51″ panel. Eight panes at
*glanceable* legibility (60×18 — enough to see the spinner and whether it is
blocked) fits a **32″ 4K** today.

That asymmetry is the answer to the tabbing question. You only ever *read* one
session at a time; the other seven only have to answer "are you waiting for me?"

| Composite layout | Panes | Panel implied | Aspect |
|---|---|---|---|
| 1 × review + 2×3 glanceable | **7** | **28.3″** | 16.4:9 — **standard 16:9** |
| 1 × review + 2×4 glanceable | 9 | 30.5″ | 12.6:9 — taller than anything sold |
| 1 × review + 1×8 glanceable | 9 | 38.7″ | 4.7:9 — portrait, absurd |

**7 panes (1 working + 6 watching) fits a normal 32″ 4K.** Going to 9 pushes the
aspect ratio to 1.4:1, which no monitor is. The cliff between 7 and 9 is where the
hardware argument actually lives.

### 6. Measured: the model is right, and the pane tiers were the wrong shape

Findings 1–5 were derived before any of them had been checked against a real
multi-pane window. On 2026-08-12 a live six-session layout was measured on the
laptop — grid read from each pty rather than estimated off an image, captured in
[`evidence/konsole-6-pane-1920x1080-2026-08-12.png`](evidence/konsole-6-pane-1920x1080-2026-08-12.png)
and [`data/observed-6pane-thinkpad-2026-08-12.json`](data/observed-6pane-thinkpad-2026-08-12.json).

**The model survives.** At this panel and 500 mm it predicts 171 usable columns
and 40 rows; the measurement accounts for 169.9 and 40. **0.6% error on columns,
exact on rows.** The chain from arc-minutes to panel specification is validated.

**The pane tiers do not.** A pane in actual daily use is **26 × 39**, against the
60 × 18 the `glanceable` tier assumed — 43% of the width, 217% of the height. The
guess was not mis-sized, it was **mis-proportioned**: it imagined a grid of short
wide panes, and what gets used is a row of tall narrow ones. Nobody chooses a
short pane, because splitting vertically hands every pane the full panel height
for free.

Two consequences:

- **Six sessions already fit on the laptop**, at 156 columns and 39 rows total.
  The premise that 8 concurrent sessions needs new hardware is weaker than it
  looked — what new hardware buys is *columns per session*, not session count.
- **Column overhead is worse than modelled.** A Konsole pane costs 15 px of
  scrollbar + 11 px of splitter = 26 px, ≈2.3 columns rather than the 1 assumed.
  Across six panes that is **8.1% of the panel width** before a character is drawn.

Re-scored on these terms — 8 panes at 26×39 in one row — the 49″ 32:9 that
finding 4 rejected now passes, at 15 panes, the best of any shape listed. See
[Step 4](docs/readability-geometry.md#step-4--re-scoring-the-market-against-the-observed-tier)
for that table and its two caveats: 26 columns is a tolerance proven at 500 mm and
not a preference, and a 1×N row has an off-axis viewing cost the model does not
price.

---

## The two candidate answers

**A. Buy the shape that exists.** 40″ 21:9 5K2K, ~140 PPI — matches the laptop's
density so `Hack 14` carries over unchanged, and clears 8 working panes at 4×2 with
a row to spare.

**B. Accept the split.** 32″ 4K, 1 review pane + 6 glanceable, with software doing
the promotion. Far cheaper, more portable, standard shape — and it makes the
software half load-bearing rather than optional.

> **Priced 2026-08-12** — real models and US street prices for all three are in
> [`docs/monitor-shortlist.md`](docs/monitor-shortlist.md). Short version: the
> shape candidate A derived is correct, and the class spans **$620 to $2,250** for
> the same resolution. Candidate B costs **$300**. Candidate C costs **$570–850**
> and holds the most sessions of anything under $1,000.

**C. Buy width, one row.** *Added after finding 6.* 49″ 32:9 DQHD, all panes in a
single row, no stacking. Rejected under A and B's 4×2 assumption; the strongest
option under the layout actually in use, at 15 panes of the observed tier. Its
weakness is the one thing the model does not price — the outer panes of a 1218 mm
row are well off-axis at 700 mm.

Undecided. See [`docs/form-factors.md`](docs/form-factors.md) for the full panel
scoring and the spec for a purpose-built panel (including, yes, where the Claude
logo goes), and [`docs/monitor-shortlist.md`](docs/monitor-shortlist.md) for what
each candidate actually costs.

---

## Repository map

```
README.md                        this brief and the headline findings
docs/readability-geometry.md     the model: assumptions, derivation, full tables
docs/form-factors.md             existing panels scored; spec for a purpose-built one
docs/monitor-shortlist.md        actual buyable models and US prices, by layout
docs/software-layer.md           the session-grid wrapper: requirements and prior art
scripts/geometry.py              re-runnable model; --json for machine output
scripts/shortlist.py             scores real, purchasable monitors against the model
scripts/wireframe.py             renders true-scale SVG mockups of any candidate grid
fixtures/sessions.json           simulated session content the wireframes re-flow
wireframes/                      generated SVG + PNG, one per candidate configuration
data/*.json                      generated output, checked in so it is diffable
data/observed-*.json             measured layouts — evidence, not model output
evidence/                        real working layouts, dated, with the panel used
```

## Wireframes — testing the tiers instead of asserting them

Finding 6 showed a guessed pane tier can be wrong in *shape*, not just size, which
makes the remaining guesses (`working`, `review`) the weakest part of the model.
[`scripts/wireframe.py`](scripts/wireframe.py) exists to attack them: it re-flows
the same simulated sessions from [`fixtures/sessions.json`](fixtures/sessions.json)
into whatever pane a candidate panel would actually give, **wrapping and clipping
exactly as a terminal does**.

Output is SVG in millimetres — true physical size. Print at 100%, stand at the
stated distance, and judge it. Or print scaled and stand proportionally closer:
scaling by *k* and viewing at *k* × distance preserves angular size exactly, and
each sheet prints its own equivalent distance.

```bash
python3 scripts/wireframe.py --list
python3 scripts/wireframe.py --config 8x1-32in-4k-observed --png
python3 scripts/wireframe.py --all --png
```

Two things the wireframes make visible that no table does:

- **The red `+N↑` counter** in each pane header — how many lines wrapping pushed
  off the top. It is the real cost of a narrow pane, and it is invisible in a
  columns × rows figure.
- **Border colour by session state.** The blocked session is obvious at a glance
  in a row of eight. That is requirement R1 from
  [`docs/software-layer.md`](docs/software-layer.md) drawn rather than described,
  and it is the argument for candidate B.

See [`wireframes/README.md`](wireframes/README.md) for what each configuration
shows.

## Status

**Specced 2026-08-12, model validated the same day.** Nothing bought, nothing
built.

The geometry model is complete, its inputs are measured rather than assumed, and
as of finding 6 it has been **checked against one real layout and reproduces it to
0.6%**. What remains unvalidated is not the arithmetic but the *requirements* fed
into it: the `working` and `review` pane tiers are still judgement calls, and
every panel recommendation rests on them.

Open:

- [ ] **Decide whether 26-column panes are acceptable or merely survivable.** This one judgement picks between a $330, a $620 and an $850 monitor, and no further arithmetic can substitute for it
- [ ] Pin down the real minimum for a *working* pane — 80×30 is still a guess, and finding 6 showed that a guessed tier can be wrong in shape, not just size
- [ ] Sit in front of a 49″ DQHD and a 40″ 5K2K at 700 mm and verify the derived cell grids — Micro Center Cambridge MA stocks both, ~45 min away
- [ ] Decide between candidates A, B and C above
- [ ] Price the off-axis cost of a 1×N row — the one term the model omits entirely
- [ ] Measure the external AOC panel's 4-pane layout the same way the 6-pane one was; its model and native resolution are not yet recorded
- [x] ~~Cost candidate A at US retail~~ — done 2026-08-12, [`docs/monitor-shortlist.md`](docs/monitor-shortlist.md)
