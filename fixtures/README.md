# Fixtures — simulated session content

Dummy Claude Code transcripts used to populate the wireframes. Keeping them here
rather than inside [`../scripts/wireframe.py`](../scripts/wireframe.py) means the
content can be extended without touching the renderer, and that the *same*
content can be re-flowed into every candidate pane size — which is the whole
point of the exercise.

Nothing here is a real transcript. The repo names and the subject matter are real
so the line lengths are representative, but no session was recorded.

## Why fake content has to be realistic

The wireframes exist to test whether a pane size is workable. That test is only
meaningful if the content wraps the way real content wraps. So the fixtures
deliberately include the things that punish narrow panes:

- **Long single-token paths and commands** that cannot break cleanly —
  `~/repos/github/ai-claude-tooling/Claude-Monitor-Research`
- **Tool-call argument blocks** with hanging indents, which lose two columns to
  the indent on every wrapped line
- **Prose paragraphs** of the length Claude actually writes
- **A blocked permission prompt**, because spotting one at a glance is the thing
  the whole grid has to support
- **Shell output with aligned columns**, which becomes unreadable the moment it
  wraps

Content that is uniformly short would make every pane size look fine.

## Format

`sessions.json` is an array of session objects:

```json
{
  "title": "Claude-Monitor-Research : claude",
  "state": "working",
  "lines": [
    {"kind": "user",      "text": "…"},
    {"kind": "assistant", "text": "…"},
    {"kind": "tool",      "tool": "Bash", "text": "…"},
    {"kind": "result",    "text": "…"},
    {"kind": "truncated", "text": "… +22 lines (ctrl+o to expand)"},
    {"kind": "question",  "text": "Do you want to make this edit?"},
    {"kind": "option",    "text": "1. Yes"},
    {"kind": "status",    "text": "Working… (6m 38s)"}
  ]
}
```

### Line kinds

| `kind` | Renders as | Colour role |
|---|---|---|
| `user` | `❯ ` + text | prompt |
| `assistant` | `● ` + text | white bullet, body text |
| `tool` | `● ` + `Tool(` + text + `)` | green bullet, blue tool name |
| `result` | `└ ` + text, indented | dim rule, lighter body |
| `truncated` | text, indented | dim |
| `question` | text | alert |
| `option` | text, indented | body |
| `status` | `✳ ` + text | **orange** |
| `rule` | horizontal rule to pane width | dim |

`state` is one of `working`, `blocked`, `done`, `shell`. It drives the pane
border colour, and is the signal
[`../docs/software-layer.md`](../docs/software-layer.md) argues the real software
layer has to surface.

## Palette

Colours in the renderer are **matched by eye** from screenshots of the live TUI
taken 2026-08-12, not sampled from the pixels — the source captures were not
retained. They are close enough to judge legibility and contrast, and should not
be treated as exact values. Notably:

- Tool names render **bold blue**, with a **green** filled bullet.
- Assistant messages get a **white** filled bullet.
- The bottom-line status message (`Working…`, `Seasoning…`, `Lollygagging…`) is
  **orange**, prefixed `✳`.
- `bypass permissions on` in the footer is **red**.

If exact values are wanted later, sample them from a fresh capture rather than
trusting these.

## Adding a session

Append an object to `sessions.json`. The renderer cycles through the array, so
more sessions than panes is fine — extras are simply unused, and adding one
changes which content lands in which pane.
