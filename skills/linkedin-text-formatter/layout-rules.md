# Smart Layout Rules

## Line breaks

- Blank line between blocks (hook → body → list → CTA → hashtags).
- Split paragraphs >220 chars at sentence boundaries.
- Lines >280 chars (no URL) get wrapped (`--no-wrap` to disable).

## Hook promotion

When line 1 is >100 chars (context/setup) and line 2–4 is a punchy line (≤90 chars, ends with `?` or no trailing `.`), line 2 moves above line 1.

Disable: `--no-promote-hook`.

## Bold (max 4)

1. **Hook** — first line after promotion
2. **Thesis** — `The (remaining )?challenge|opportunity|… is …`
3. **Section headers** — ends with `:`, or `Step N`, or `# Title`
4. **Stats** — `%`, `x`, `$`, counts only
5. **Manual** — lines already wrapped in `**`

`--less-bold` skips section headers (hook + thesis + manual still apply).

Never bold: hashtags, URLs, report titles, full paragraphs.

## Italic

- Short `"quotes"` only (<35 chars, no `20xx`)
- Report/article titles before `report` → **plain ASCII** (fixes cursor + digit breaks)
- CTA cues + closing engagement questions (`where do you spend…?`)

## Hashtags

- Auto-suggest up to 5 from `hashtags.py` rules; user tags kept first.
- Footer: blank line + `#Tag1 #Tag2 …` (plain ASCII only).
- `--no-hashtags` / `--hashtags N`

## User overrides

| Say | Do |
|-----|-----|
| less bold | `--less-bold` |
| more spacing | one sentence per line in draft |
| keep hashtags inline | `--no-hashtags`, append manually |
| custom markup | `**bold**` in draft or `format.py --inline` |

## Extend hashtags

Edit `scripts/hashtags.py` — add `(regex, "#Tag", priority)` tuples.
