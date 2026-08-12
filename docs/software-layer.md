# The software layer

The hardware half asks what panel makes 8 sessions visible. This half asks what
makes 8 sessions *usable* — because the geometry has already shown that visible
and readable are different things.

Environment: **KDE Plasma on Ubuntu (Wayland), Konsole 25.12.3, tmux 3.6**.

---

## The finding that drives the requirement

From [`readability-geometry.md`](readability-geometry.md#step-3--composite-layouts):
8 panes all at *working* legibility needs a 39–51″ panel, but **1 working pane + 6
glanceable panes fits a standard 32″ 4K**.

That is not a compromise to be apologised for. It matches how the sessions are
actually used: you drive one at a time, and the other seven only have to answer
one question — **are you blocked on me?**

So the software's primary job is not layout. It is **attention routing**. If the
grid can tell you which session needs you, the other panes never have to be
readable, and the hardware requirement collapses by ten inches of diagonal.

---

## Requirements

### R1 — Status per session, readable at a glance

The load-bearing feature. Each pane advertises one of:

| State | Meaning |
|---|---|
| `working` | Running; no action needed |
| `blocked` | Waiting on a permission prompt or a question — **needs you now** |
| `done` | Task finished, session idle |
| `failed` | Exited non-zero or errored |

Must be distinguishable **without reading the pane contents** — colour and glyph in
the pane border, since at 60×18 the body text is not legible at 700 mm anyway.

`blocked` is the only state that matters urgently, and it is currently invisible: a
session waiting on a permission prompt looks identical to one thinking hard.

### R2 — Direct addressing, never cycling

One keystroke to reach any pane by position. `Meta+1`…`Meta+8`, not `next-pane`
pressed repeatedly. With 8 panes, cycling averages 4 keypresses and requires
knowing where you are.

### R3 — Promote and demote in place

Zoom one pane to full window and back without disturbing the grid. This is what
makes the composite layout work: `glanceable` for watching, promote to full for
working, demote when done.

### R4 — Durable pane identity

A pane's title must say **which repo and which task**, not `bash`. In the baseline
screenshot two of four panes are labelled `github : bash`, which is no identity at
all. Titles must survive a detach/reattach.

### R5 — Survive a crash

Non-negotiable and **already solved** — see
[`Terminal-Multiplexing-QA`](https://github.com/danielrosehill/Terminal-Multiplexing-QA),
which settled on tmux over zellij for this machine and documents the Konsole
`Command=/usr/bin/tmux new -A -s main` integration.

### R6 — Layout as a named, reloadable thing

"Eight sessions across six repos" should be one command, not eight manual splits.

---

## What tmux 3.6 already provides

Verified by probe on a throwaway socket, 2026-08-12. These are **window** options
(`set -gw`), not session options — `show-options -g` will not list them, which is a
easy way to conclude wrongly that they do not exist.

| Requirement | Mechanism | Verified |
|---|---|---|
| R1 status | `pane-border-status top` + `pane-border-format` | ✓ both accepted; default is `off` |
| R2 addressing | `select-pane -t` bound to `Meta+N` | ✓ |
| R3 promote | `resize-pane -Z`, state readable via `#{window_zoomed_flag}` | ✓ returns `0`/`1` |
| R4 identity | `select-pane -T "<title>"`, read back via `#{pane_title}` | ✓ round-trips |
| R6 layout | `select-layout main-vertical` + `main-pane-width` | ✓ default 80, set to 101 OK |

**`main-vertical` is the composite layout.** One large pane on the left, the rest
stacked down the right — exactly the "1 review + N glanceable" shape the geometry
arrived at independently. Setting `main-pane-width 101` sizes the focus pane to the
`review` tier from the model.

Defaults worth knowing: `main-pane-width 80`, `main-pane-height 24`,
`pane-border-status off`, and a `pane-border-format` that already interpolates
`#{pane_title}`.

### The gap

Everything above is mechanism. **tmux has no idea what state a Claude session is
in** — R1 has no data source, and R1 is the requirement the whole design rests on.

## Filling R1: Claude Code hooks

Claude Code's hook system can write session state where tmux can read it. The
sketch:

1. A hook fires on stop / notification / permission-request and writes a state file
   keyed by pane, e.g. `~/.claude-user-data/fleet/<pane_id>.state`.
2. `pane-border-format` interpolates a `#()` shell call that reads that file and
   emits a coloured glyph.
3. `status-interval` controls refresh; borders redraw on the same tick.

Unverified: which hook events fire on a *permission prompt* specifically, and
whether a hook can cheaply learn its own tmux pane id (`$TMUX_PANE` is exported to
the shell, but a hook runs in Claude Code's process). Both need checking before
this is more than a sketch — that is the first implementation question, not a
detail.

The pane-border `#()` path is preferred over a KDE widget: it puts the indicator
inside the pane it describes, so it works with no compositor integration and
survives over SSH.

---

## Boundaries with existing repos

This repo should not re-derive work that already has a home.

| Repo | Owns | This repo defers on |
|---|---|---|
| [`Terminal-Multiplexing-QA`](https://github.com/danielrosehill/Terminal-Multiplexing-QA) | tmux vs zellij, crash survival, Konsole→tmux integration | R5 entirely |
| [`Claude-Fleet-Traffic-Shaper`](https://github.com/danielrosehill/Claude-Fleet-Traffic-Shaper) | Rate-limit contention across 6–8 concurrent sessions; which session eats a `429`/`529` | Everything about API-level fleet behaviour |
| [`interrupt-claude`](https://github.com/danielrosehill/interrupt-claude-plugin) | What to do with an interruption once you are in a session | In-session task routing |
| [`Claude-Breakout`](https://github.com/danielrosehill/Claude-Breakout) | Where an off-topic idea goes | Idea capture |

`Claude-Fleet-Traffic-Shaper` is the closest neighbour and reaches the same
conclusion from the API side: it distinguishes *the session being watched* from
*background sweeps nobody would miss*. That is the same focus/watch split the
geometry produces here. **If a priority signal already exists there, R1 should
consume it rather than invent a second one** — worth checking before building
anything.

## Status

Specification only. Nothing built. The tmux primitives are verified; the state
source for R1 is not, and it is the part that decides whether any of this works.
