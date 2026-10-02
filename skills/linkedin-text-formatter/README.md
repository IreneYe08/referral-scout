# LinkedIn Text Formatter

**Self-contained Agent Skill.** Draft with your agent → paste-ready LinkedIn post. No browser tab.

> **This folder is a mirror** of the [dedicated repo](https://github.com/IreneYe08/linkedin-text-formatter-cortex). Clone that repo directly to install.

## Install (recommended)

### Windows

```powershell
git clone https://github.com/IreneYe08/linkedin-text-formatter-cortex.git <skills-dir>\linkedin-text-formatter
py -3 <skills-dir>\linkedin-text-formatter\scripts\linkedin_post.py --self-test
```

### macOS / Linux

```bash
git clone https://github.com/IreneYe08/linkedin-text-formatter-cortex.git <skills-dir>/linkedin-text-formatter
python <skills-dir>/linkedin-text-formatter/scripts/linkedin_post.py --self-test
```

Restart your agent (or open a new session) so the skill loads.

## Install from the monorepo (alternative)

If you already cloned [linkedin-smart-formatter](https://github.com/IreneYe08/linkedin-smart-formatter), copy this skill's folder from it into `<skills-dir>/linkedin-text-formatter`.

## What's included

| File | Purpose |
|------|---------|
| `SKILL.md` | Agent instructions |
| `linkedin-post-guideline.md` | 8-block high-performing post structure |
| `Anti-AI_Writing_Guidelines.md` | Human voice, anti-AI patterns |
| `layout-rules.md` | Smart layout heuristics |
| `scripts/` | Python formatter (stdlib only) |

## Usage

Ask the agent:

> Format this LinkedIn post / Write a LinkedIn post about [topic] and format it for paste

The agent runs `scripts/linkedin_post.py` and returns copy-paste output.

## Update

**Dedicated repo:** `cd <skills-dir>/linkedin-text-formatter && git pull`

**Monorepo copy:** pull the main repo and re-copy this skill's folder.

## Full repo (other platforms)

Cursor, Claude Code, Codex adapters: [github.com/IreneYe08/linkedin-smart-formatter](https://github.com/IreneYe08/linkedin-smart-formatter)
