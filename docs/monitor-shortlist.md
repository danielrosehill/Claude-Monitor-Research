# Monitor shortlist — actual products, US prices

What to buy, by layout, with real models and approximate US street prices.
Gathered **2026-08-12**. Re-runnable via
[`../scripts/shortlist.py`](../scripts/shortlist.py), which imports the geometry
model rather than re-deriving anything, so if the model changes these numbers
change with it.

```bash
python3 scripts/shortlist.py --tier observed     # the layout in daily use
python3 scripts/shortlist.py --tier working      # 80x30 panes
python3 scripts/shortlist.py --json
```

> **Price status.** Dell figures were pulled live from dell.com on 2026-08-12.
> Micro Center figures are from their own listings. Everything else is from retail
> aggregation and deal trackers and is **indicative of tier, not a quote** —
> ultrawide prices in particular swing $200–400 on promotion. Verify before
> buying. All prices USD.

---

## The one thing that decides this

Not the panel. **The pane tier.** Every recommendation below changes completely
depending on whether a Claude Code pane needs 26 columns or 80.

| Tier | Cells | Status |
|---|---|---|
| `observed` | 26 × 39 | **Measured** — what six concurrent sessions actually get today |
| `working` | 80 × 30 | Assumed — the 80-column norm Claude Code lays out against |

26 columns is a *tolerance* forced by a 1920×1080 panel, not a preference. If it
is genuinely fine, the cheapest recommendation here is a **$300 monitor**. If you
really want 80 columns, the entry price is **$620** and the shape changes. This is
the open question that matters most, and it is answerable in ten minutes by
sitting at the current laptop and deciding whether those 26-column panes are
pleasant or merely survivable.

---

## Recommendation by layout

| If you want… | Buy | Size | Form | Panes | Price |
|---|---|---|---|---|---|
| **More of what you already do** — narrow panes, one row | LG 32UR500K-B or Dell S3225QS | **32″ 4K** | **traditional** | 9 | **$300–330** |
| **8 real 80-column panes**, font unchanged | INNOCN 40C1U or Deco Gear VIEW401 | **40″ 21:9 5K2K** | ultrawide | 8 (4×2) | **$620–680** |
| **Maximum sessions on screen** | CRUA 49 / INNOCN 49C1R / Samsung S49CG954 | **49″ 32:9 DQHD** | super-ultrawide | 15 | **$570–850** |
| **Maximum *working* panes** | LG 48″ C-series OLED | **48″ 4K** | TV | 12 (4×3) | **$1,100** |
| **No compromise, cost ignored** | Samsung Odyssey Neo G9 G95NC | **57″ 32:9** | super-ultrawide | 18 / 12 working | **~$1,600** |

### The headline

**The 40″ 5K2K shape the model derived is right, and Dell's version of it costs
3.6× the INNOCN version of the same panel spec.**

`docs/form-factors.md` derived a ≈2.45:1 panel with ~2000+ vertical pixels and
landed on the 40″ 21:9 5K2K class. That holds. What was never checked is that this
class spans **$620 to $2,250** for identical resolution and near-identical PPI:

| 40″ 5K2K | Price | Panes (working) | $/pane |
|---|---|---|---|
| INNOCN 40C1U | $620 | 8 | $78 |
| Deco Gear VIEW401 | $680 | 8 | $85 |
| LG 40WP95C-W | $1,300 | 8 | $163 |
| **Dell UltraSharp U4025QW** | **$2,250** | 8 | **$281** |

The Dell buys Thunderbolt 4 with 140 W power delivery, a KVM, 120 Hz, IPS Black
contrast and a 3-year advanced-exchange warranty. It buys **zero additional
panes**. If the panel is for terminals, that is $1,630 of dock.

---

## Full shortlist — `observed` tier (26 × 39), 700 mm

Panes in a **single row**, which is the arrangement actually in use. Sorted by
cost per pane.

| Monitor | Form | Size | PPI | Row | Grid | USD | $/pane |
|---|---|---|---|---|---|---|---|
| LG 32UR500K-B | traditional | 31.5″ | 140 | 9 | 9 | 300 | **33** |
| Dell S3225QS | traditional | 31.5″ | 140 | 9 | 9 | 330 | **37** |
| CRUA 49in DQHD | super-ultra | 49″ | 109 | **15** | 15 | 570 | **38** |
| INNOCN 49C1R | super-ultra | 49″ | 109 | **15** | 15 | 675 | 45 |
| INNOCN 40C1U | ultrawide | 39.7″ | 140 | 12 | 12 | 620 | 52 |
| Deco Gear VIEW401 | ultrawide | 39.7″ | 140 | 12 | 12 | 680 | 57 |
| Samsung Odyssey G9 S49CG954 | super-ultra | 49″ | 109 | 15 | 15 | 850 | 57 |
| Gigabyte AORUS CO49DQ | super-ultra | 49″ | 109 | 15 | 15 | 900 | 60 |
| Samsung Odyssey OLED G9 G93SC | super-ultra | 49″ | 109 | 15 | 15 | 900 | 60 |
| KTC G42P5 | traditional | 42″ | 105 | 12 | **24** | 800 | 67 |
| Acer Predator X49 | super-ultra | 49″ | 109 | 15 | 15 | 1000 | 67 |
| LG C4 42in OLED | tv | 42″ | 105 | 12 | **24** | 900 | 75 |
| LG C-series 48in OLED | tv | 48″ | 92 | 13 | **26** | 1100 | 85 |
| Dell UltraSharp 32 U3225QE | traditional | 31.5″ | 140 | 9 | 9 | 800 | 89 |
| Samsung Odyssey Neo G9 G95NC | super-ultra | 57″ | 140 | **18** | 18 | 1600 | 89 |
| Dell UltraSharp 49 U4924DW | super-ultra | 49″ | 109 | 15 | 15 | 1410 | 94 |
| LG 40WP95C-W | ultrawide | 39.7″ | 140 | 12 | 12 | 1300 | 108 |
| Dell UltraSharp 40 U4025QW | ultrawide | 39.7″ | 140 | 12 | 12 | 2250 | 188 |
| *laptop, for reference* | — | 15.6″ | 141 | 0 at 700 mm | | — | — |

The laptop shows **0** because at a 700 mm desk distance its 1920 px only yields
122 usable columns — not enough for even five 26-column panes plus chrome. It
manages six at 500 mm. That gap *is* the case for buying something.

## Full shortlist — `working` tier (80 × 30), 700 mm

Only panels reaching 8 panes are listed. Best packing, not single-row.

| Monitor | Form | Size | PPI | Row | Grid | USD |
|---|---|---|---|---|---|---|
| **INNOCN 40C1U** | ultrawide | 39.7″ | 140 | 4 | **8** | **620** |
| Deco Gear VIEW401 | ultrawide | 39.7″ | 140 | 4 | 8 | 680 |
| KTC G42P5 | traditional | 42″ | 105 | 4 | 8 | 800 |
| LG C4 42in OLED | tv | 42″ | 105 | 4 | 8 | 900 |
| LG C5 42in OLED | tv | 42″ | 105 | 4 | 8 | 1000 |
| **LG C-series 48in OLED** | tv | 48″ | 92 | 4 | **12** | 1100 |
| LG 40WP95C-W | ultrawide | 39.7″ | 140 | 4 | 8 | 1300 |
| **Samsung Odyssey Neo G9** | super-ultra | 57″ | 140 | 6 | **12** | 1600 |
| Dell UltraSharp 40 U4025QW | ultrawide | 39.7″ | 140 | 4 | 8 | 2250 |

Note what the 49″ DQHD does here: **5 panes, never 8.** It is unbeatable at the
observed tier and mediocre at the working tier, because 1440 px holds exactly one
row of 30-row panes. That single fact is the whole hardware decision in miniature.

---

## Does text get worse on a low-PPI panel?

A reasonable worry about the 49″ (109 PPI) and the TVs (92–105 PPI). The answer is
**no, except on the 48″** — because moving further away means each character is
physically larger, which recovers most of the pixels a lower density loses.

Pixels per character cell at the *same apparent size*, against the laptop today:

| Panel | PPI | Distance | Advance px | vs laptop |
|---|---|---|---|---|
| laptop 15.6″ (today) | 141 | 500 mm | 11.2 | 100% |
| 32″ 4K | 140 | 700 mm | 15.6 | **139%** |
| 40″ 21:9 5K2K | 140 | 700 mm | 15.6 | **139%** |
| 57″ 32:9 Dual-4K | 140 | 700 mm | 15.6 | **139%** |
| 49″ 32:9 DQHD | 109 | 700 mm | 12.1 | **108%** |
| 42″ 4K (TV) | 105 | 700 mm | 11.7 | 104% |
| 48″ 4K (TV) | 92 | 700 mm | 10.2 | **91%** |

Even the "low density" 49″ DQHD renders glyphs with **8% more pixels** than the
current laptop. Only the 48″ regresses, and only by 9%.

Two caveats this table does not capture:

- **Font size in points must change.** A 140 PPI panel at 700 mm wants roughly
  Hack 19–20 to hit the same 16.8′, against Hack 14 today. Panels at 140 PPI keep
  the *pixel* metrics identical to the laptop, so a profile ports cleanly; 109 PPI
  and below need re-tuning.
- **OLED subpixel layout.** The LG WOLED panels (42″/48″ C-series, KTC G42P5) use
  a WRGB layout, not RGB stripe, and produce visible colour fringing on small
  text. Widely reported and it is the standard reason people return them as
  monitors. IPS is the safer buy for a terminal wall. Not modelled anywhere here.

---

## Traditional vs non-traditional

| Form | Category health | Notes |
|---|---|---|
| **32″ 4K** | fully mainstream | Dozens of models, $300 floor, stocked everywhere. Zero risk. |
| **40″ 21:9 5K2K** | **thin** | The best fit for 8 working panes, and a genuinely rare category — a handful of models, mostly minor brands, with Dell/LG charging a large premium. Buy the cheap one or wait. |
| **49″ 32:9 DQHD** | mainstream-niche | A real, competitive category thanks to gaming. Best pane count per dollar. Sold at Best Buy/Micro Center. |
| **42–48″ 4K OLED** | mainstream as *TVs* | Cheap per pane and enormous grids, but they are televisions: no DisplayPort on the LG sets, WRGB text fringing, and 48″ at desk distance is a lot of neck movement. The KTC G42P5 is the monitor-shaped version of this bet (DisplayPort + KVM). |
| **57″ 32:9 Dual-4K** | exotic | One product, effectively. Needs DisplayPort 2.1 to drive 7680×2160 properly. |

---

## Buying in the US, now

Relevant because the README lists costing this at US retail as an open item and
**that window is currently open** — this machine is egressing from Spectrum
residential in Worcester, MA as of 2026-08-12.

- **Micro Center, 730 Memorial Drive, Cambridge MA** — roughly 45 minutes from
  Worcester, and the only realistic place to *see* a 49″ and a 40″ ultrawide side
  by side before committing. Their listed 49″ stock as of 2026-08-12: Samsung
  S49CG954 at $849.99 (from $1,299.99), Gigabyte AORUS CO49DQ at $899.99, Acer
  Predator X49 at $999.99. Set the store to Cambridge for real stock; several
  ultrawides show "usually ships 5–7 days" rather than shelf stock, and member
  pricing needs a sign-in to display.
- **Dell.com** — sells its own panels well above street. Live on 2026-08-12:
  U4025QW $2,249.99, U4924DW $1,409.99.
- **Amazon** — where the INNOCN/Deco Gear/CRUA prices live. These fluctuate
  weekly; the 40C1U has traded between $595 and $750 in 2026.

**Given a physical shortlist trip is possible, the highest-value thing to do is
not to buy anything yet** — it is to look at a 49″ DQHD at 700 mm in the Cambridge
store and settle whether 26-column panes are acceptable. That single judgement
picks between a $330 monitor, a $620 monitor and an $850 monitor, and no amount of
further arithmetic here can substitute for it.

---

## Sources

Gathered 2026-08-12.

- [Dell U4025QW — dell.com](https://www.dell.com/en-us/shop/dell-ultrasharp-40-curved-thunderbolt-hub-monitor-u4025qw/apd/210-bmdp/monitors-monitor-accessories) (live price)
- [Dell U4924DW — dell.com](https://www.dell.com/en-us/shop/dell-ultrasharp-49-curved-usb-c-hub-monitor-u4924dw/apd/210-bgtz/monitors-monitor-accessories) (live price)
- [Dell U4025QW review — DisplayNinja](https://www.displayninja.com/dell-u4025qw-review/)
- [Dell U3225QE review — RTINGS](https://www.rtings.com/monitor/reviews/dell/u3225qe)
- [Samsung Odyssey Neo G9 G95NC review — RTINGS](https://www.rtings.com/monitor/reviews/samsung/odyssey-neo-g9-g95nc-s57cg95)
- [LG C5 42 OLED as monitor — RTINGS](https://www.rtings.com/monitor/reviews/lg/c5-42-oled)
- [INNOCN 40C1U deal history — PCWorld](https://www.pcworld.com/article/3089766/innocn-40-inch-5k-ultrawide-monitor-hits-lowest-price-595.html)
- [INNOCN 40C1R review (the WQHD model, not 5K2K) — PC Gamer](https://www.pcgamer.com/innocn-40c1r-ultrawide-gaming-monitor-review/)
- [Micro Center ultrawide listings](https://www.microcenter.com/category/4294966896,4294806802/ultrawide-computer-monitors)
- [Deco Gear VIEW401 — Best Buy](https://www.bestbuy.com/product/deco-gear-40-inch-curved-super-ultrawide-nano-ips-monitor-5120x2160-5k2k-219-hdr10-100-srgb-usb-c-65w-black/JJG3SJ3S7Q/sku/10189225)
- [Samsung Odyssey Neo G9 — B&H](https://www.bhphotovideo.com/c/product/1760813-REG/samsung_ls57cg952nnxza_odyssey_neo_g9_57.html)
